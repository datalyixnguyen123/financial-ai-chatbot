
from __future__ import annotations

from datetime import date, datetime, timedelta
from threading import Lock
import re
import uuid


_STATE_LOCK = Lock()
_ROADMAP_STATE = {
    "plans": [],
    "updated_at": None,
}


def clear_study_roadmap() -> None:
    with _STATE_LOCK:
        _ROADMAP_STATE["plans"] = []
        _ROADMAP_STATE["updated_at"] = None


def process_study_goal_message(message: str) -> dict | None:
    parsed_goal = _extract_study_goal(message)
    if parsed_goal is None:
        return None

    with _STATE_LOCK:
        existing_plan = _find_plan_by_topic(parsed_goal["topic"])
        plan = _build_plan(parsed_goal, existing_plan=existing_plan)
        if existing_plan is None:
            _ROADMAP_STATE["plans"].append(plan)
        else:
            index = _ROADMAP_STATE["plans"].index(existing_plan)
            _ROADMAP_STATE["plans"][index] = plan

        _ROADMAP_STATE["plans"].sort(key=lambda item: item["target_date"])
        _ROADMAP_STATE["updated_at"] = datetime.now().isoformat()
        return _serialize_plan(plan)


def get_study_roadmap() -> dict:
    with _STATE_LOCK:
        serialized_plans = [_serialize_plan(plan) for plan in _ROADMAP_STATE["plans"]]
        total_actions = sum(plan["total_actions"] for plan in serialized_plans)
        total_completed_actions = sum(
            plan["completed_actions"] for plan in serialized_plans
        )
        return {
            "has_plans": bool(serialized_plans),
            "total_plans": len(serialized_plans),
            "total_actions": total_actions,
            "total_completed_actions": total_completed_actions,
            "plans": serialized_plans,
            "empty_state_message": (
                "Chưa có lộ trình học nào được tạo. "
                "Bạn hãy trò chuyện với AI như: 'Tôi muốn đặt mục tiêu IELTS 7.0 trong 60 ngày'."
            ),
            "updated_at": _ROADMAP_STATE["updated_at"],
        }


def toggle_study_action(
    plan_id: str,
    action_id: str,
    completed: bool | None = None,
) -> dict | None:
    with _STATE_LOCK:
        for plan in _ROADMAP_STATE["plans"]:
            if plan["id"] != plan_id:
                continue

            for action in plan["actions"]:
                if action["id"] != action_id:
                    continue
                action["completed"] = (
                    not action["completed"] if completed is None else bool(completed)
                )
                action["completed_at"] = (
                    datetime.now().isoformat() if action["completed"] else None
                )
                plan["updated_at"] = datetime.now().isoformat()
                _ROADMAP_STATE["updated_at"] = plan["updated_at"]
                return _serialize_plan(plan)

    return None


def build_study_plan_context(message: str, updated_plan: dict | None = None,) -> str:
    roadmap = get_study_roadmap()
    has_study_reference = _contains_study_reference(message)

    if updated_plan is None and not (roadmap["has_plans"] and has_study_reference):
        return ""
    
    parts = []
    if updated_plan is not None:
        parts.append(
            "\n".join(
                [
                    "=== STUDY ROADMAP UPDATE ===",
                    "status: created_or_updated",
                    f"topic: {updated_plan['topic']}",
                    f"target: {updated_plan['target_label']}",
                    f"progress_percent: {updated_plan['progress_percent']}",
                    f"days_remaining: {updated_plan['days_remaining']}",
                    f"target_date: {updated_plan['target_date']}",
                    "The roadmap has been stored in application memory.",
                ]
            )
        )
    if roadmap["has_plans"]:
        summary_lines = [
            "=== STUDY ROADMAP SUMMARY ===",
            f"total_plans: {roadmap['total_plans']}",
        ]
        for index, plan in enumerate(roadmap["plans"], start=1):
            summary_lines.extend(
                [
                    f"plan_{index}_topic: {plan['topic']}",
                    f"plan_{index}_target: {plan['target_label']}",
                    f"plan_{index}_progress_percent: {plan['progress_percent']}",
                    f"plan_{index}_days_remaining: {plan['days_remaining']}",
                ]
            )
        parts.append("\n".join(summary_lines))

    return "\n\n".join(part for part in parts if part)


def _extract_study_goal(message: str) -> dict | None:
    raw_text = str(message or "").strip()
    normalized_text = _normalize_text(raw_text)

    if not _contains_study_reference(normalized_text):
        return None
    target = _extract_target(raw_text, normalized_text)
    topic = _extract_topic(raw_text, normalized_text, target["topic_hint"])
    target_date = _extract_target_date(raw_text, normalized_text)
    days_total = max((target_date - date.today()).days, 1)
    return {
        "topic": topic,
        "target_label": target["target_label"],
        "topic_badge": target["topic_badge"],
        "target_date": target_date,
        "days_total": days_total,
        "source_message": raw_text,
    }

def _contains_study_reference(text: str) -> bool:
    normalized = _normalize_text(text)
    trigger_patterns = (
        "dat muc tieu hoc",
        "muc tieu hoc",
        "ke hoach hoc",
        "ke hoach on thi",
        "lo trinh hoc",
        "lo trinh on thi",
        "muon hoc",
        "muon on",
        "muon dat",
        "gpa",
        "ielts",
        "toeic",
        "toefl",
        "sat",
        "python",
        "on thi",
        "hoc mon",
        "ke hoach luyen de",
        "tien do hoc",
        "study plan",
        "study goal",
        "hsk",
        "jlpt",
        "vstep",
        "chứng chỉ"
    )
    return any(pattern in normalized for pattern in trigger_patterns)


def _extract_target(raw_text: str, normalized_text: str,) -> dict:
    gpa_match = re.search(r"\bgpa\s*([0-9]+(?:[.,][0-9]+)?)", normalized_text)
    if gpa_match:
        value = gpa_match.group(1).replace(",", ".")
        return {
            "target_label": f"Mục tiêu GPA {value}",
            "topic_hint": None,
            "topic_badge": "GPA",
        }


    ielts_match = re.search(r"\bielts\s*([0-9]+(?:[.,][0-9]+)?)", normalized_text)
    if ielts_match:
        value = ielts_match.group(1).replace(",", ".")
        return {
            "target_label": f"Target IELTS {value}",
            "topic_hint": "Tiếng Anh IELTS",
            "topic_badge": "IELTS",
        }

    toeic_match = re.search(r"\btoeic\s*([0-9]+)", normalized_text)
    if toeic_match:
        value = toeic_match.group(1)
        return {
            "target_label": f"Target TOEIC {value}",
            "topic_hint": "Tiếng Anh TOEIC",
            "topic_badge": "TOEIC",
        }

    score_match = re.search(
        r"(?:dat|muc tieu)\s*([0-9]+(?:[.,][0-9]+)?)\s*(?:diem|point)?",
        normalized_text,
    )
    if score_match:
        value = score_match.group(1).replace(",", ".")
        return {
            "target_label": f"Mục tiêu {value} điểm",
            "topic_hint": None,
            "topic_badge": "Học tập",
        }
    return {
        "target_label": "Hoàn thành lộ trình học tập",
        "topic_hint": None,
        "topic_badge": "Học tập",
    }


def _extract_topic(raw_text: str, normalized_text: str, topic_hint: str | None,) -> str:
    if topic_hint:
        return topic_hint
    known_topics = (
        ("ielts", "Tiếng Anh IELTS"),
        ("toeic", "Tiếng Anh TOEIC"),
        ("toefl", "Tiếng Anh TOEFL"),
        ("sat", "Luyện thi SAT"),
        ("python", "Lập Trình Python"),
        ("giai tich", "Giải Tích"),
        ("xac suat thong ke", "Xác Suất Thống Kê"),
        ("kinh te vi mo", "Kinh Tế Vi Mô"),
        ("kinh te vi mo", "Kinh Tế Vi Mô"),
        ("ke toan", "Kế Toán"),
        ("nhap mon AI", "Nhập môn AI"),
        ("cau truc du lieu", "Cấu Trúc Dữ Liệu"),
        ("lap trinh huong doi tuong", "Lập Trình Hướng Đối Tượng"),
        ("ly thuyet do thi", "Lý Thuyết Đồ Thị")
    )

    for pattern, label in known_topics:
        if pattern in normalized_text:
            return label
    candidate_patterns = [
        r"(?:hoc|on|thi|mon)\s+(.+?)(?=\s+(?:trong|de|voi|muc tieu|dat|truoc|den)\b|$)",
        r"(?:muc tieu\s+hoc)\s+(.+?)(?=\s+(?:trong|de|voi|dat|truoc|den)\b|$)",
    ]
    for pattern in candidate_patterns:
        match = re.search(pattern, normalized_text)
        if not match:
            continue
        candidate = match.group(1)
        candidate = re.sub(r"\b(?:gpa|ielts|toeic|toefl|sat)\b.*$", "", candidate,).strip()
        if candidate:
            return _title_case_ascii(candidate)

    return "Lộ Trình Học Tập Mới"


def _extract_target_date(raw_text: str, normalized_text: str) -> date:
    iso_match = re.search(r"\b(20\d{2})-(\d{1,2})-(\d{1,2})\b", raw_text)
    if iso_match:
        return date(
            int(iso_match.group(1)),
            int(iso_match.group(2)),
            int(iso_match.group(3)),
        )
    slash_match = re.search(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{4}))?\b", raw_text)
    if slash_match:
        day = int(slash_match.group(1))
        month = int(slash_match.group(2))
        year = int(slash_match.group(3) or date.today().year)
        parsed_date = date(year, month, day)
        if parsed_date < date.today() and slash_match.group(3) is None:
            parsed_date = date(year + 1, month, day)
        return parsed_date

    duration_match = re.search(r"trong\s+(\d+)\s*(ngay|tuan|thang)", normalized_text,)
    if duration_match:
        amount = int(duration_match.group(1))
        unit = duration_match.group(2)
        multiplier = {
            "ngay": 1,
            "tuan": 7,
            "thang": 30,
        }[unit]
        return date.today() + timedelta(days=amount * multiplier)
    if "ielts" in normalized_text or "toeic" in normalized_text:
        return date.today() + timedelta(days=60)
    return date.today() + timedelta(days=30)


def _build_plan(parsed_goal: dict, existing_plan: dict | None = None) -> dict:
    today = date.today()
    target_date = parsed_goal["target_date"]
    days_total = max((target_date - today).days, 1)
    actions = _build_actions(
        topic=parsed_goal["topic"],
        target_label=parsed_goal["target_label"],
        start_date=today,
        target_date=target_date,
        existing_plan=existing_plan,
    )

    return {
        "id": existing_plan["id"] if existing_plan is not None else str(uuid.uuid4()),
        "topic": parsed_goal["topic"],
        "topic_key": _normalize_text(parsed_goal["topic"]),
        "topic_badge": parsed_goal["topic_badge"],
        "target_label": parsed_goal["target_label"],
        "start_date": today.isoformat(),
        "target_date": target_date.isoformat(),
        "days_total": days_total,
        "actions": actions,
        "source_message": parsed_goal["source_message"],
        "updated_at": datetime.now().isoformat(),
    }

def _build_actions(
    topic: str,
    target_label: str,
    start_date: date,
    target_date: date,
    existing_plan: dict | None = None,
) -> list[dict]:
    total_days = max((target_date - start_date).days, 1)
    checkpoints = [0.15, 0.4, 0.7, 0.95]
    templates = [
        (
            f"Chốt mục tiêu cho {topic}",
            f"Làm rõ đầu ra cần đạt: {target_label}. Chia nhỏ theo từng tuần.",
        ),
        (
            f"Củng cố nền tảng {topic}",
            "Tập trung các chủ đề cốt lõi và lập lịch học theo block Pomodoro.",
        ),
        (
            f"Luyện tập trọng tâm {topic}",
            "Hoàn thành bài tập, đề luyện, hoặc bộ câu hỏi trọng tâm của giai đoạn giữa.",
        ),
        (
            f"Tổng ôn và tự đánh giá {topic}",
            "Ôn lại điểm yếu, tự kiểm tra kết quả và chốt các việc cần hoàn thành trước deadline.",
        ),
    ]

    previous_actions_by_title = {}
    if existing_plan is not None:
        previous_actions_by_title = {
            action["title"]: action for action in existing_plan.get("actions", [])
        }
    actions = []
    for index, (title, description) in enumerate(templates):
        due_offset = max(int(total_days * checkpoints[index]), index + 1)
        due_date = min(start_date + timedelta(days=due_offset), target_date)
        previous = previous_actions_by_title.get(title)
        actions.append(
            {
                "id": previous["id"] if previous is not None else str(uuid.uuid4()),
                "title": title,
                "description": description,
                "due_date": due_date.isoformat(),
                "completed": bool(previous["completed"]) if previous else False,
                "completed_at": previous["completed_at"] if previous else None,
            }
        )
    return actions

def _serialize_plan(plan: dict) -> dict:
    today = date.today()
    target_date = date.fromisoformat(plan["target_date"])
    days_remaining = max((target_date - today).days, 0)
    total_actions = len(plan["actions"])
    completed_actions = sum(
        1 for action in plan["actions"] if action["completed"]
    )
    progress_percent = round((completed_actions / total_actions) * 100) if total_actions else 0
    serialized_actions = []
    for action in plan["actions"]:
        due_date = date.fromisoformat(action["due_date"])
        serialized_actions.append(
            {
                "id": action["id"],
                "title": action["title"],
                "description": action["description"],
                "due_date": action["due_date"],
                "due_label": _build_due_label(due_date),
                "completed": action["completed"],
                "completed_at": action["completed_at"],
            }
        )

    return {
        "id": plan["id"],
        "topic": plan["topic"],
        "topic_badge": plan["topic_badge"],
        "target_label": plan["target_label"],
        "start_date": plan["start_date"],
        "target_date": plan["target_date"],
        "days_total": max((target_date - date.fromisoformat(plan["start_date"])).days, 1),
        "days_remaining": days_remaining,
        "progress_percent": progress_percent,
        "completed_actions": completed_actions,
        "total_actions": total_actions,
        "status_label": _build_status_label(days_remaining),
        "last_source_message": plan["source_message"],
        "actions": serialized_actions,
    }


def _build_due_label(due_date: date) -> str:
    day_delta = (due_date - date.today()).days
    if day_delta <= 0:
        return "Đến hạn hôm nay"
    if day_delta == 1:
        return "Còn 1 ngày"
    return f"Còn {day_delta} ngày"

def _build_status_label(days_remaining: int) -> str:
    if days_remaining <= 7:
        return f"Gấp: còn {days_remaining} ngày"
    if days_remaining <= 21:
        return f"Ổn định: còn {days_remaining} ngày"
    return f"Dài hạn: còn {days_remaining} ngày"


def _find_plan_by_topic(topic: str) -> dict | None:
    topic_key = _normalize_text(topic)
    for plan in _ROADMAP_STATE["plans"]:
        if plan["topic_key"] == topic_key:
            return plan
    return None


def _normalize_text(text: str) -> str:
    normalized = str(text or "").lower().strip()
    replacements = {
        "à": "a",
        "á": "a",
        "ạ": "a",
        "ả": "a",
        "ã": "a",
        "â": "a",
        "ầ": "a",
        "ấ": "a",
        "ậ": "a",
        "ẩ": "a",
        "ẫ": "a",
        "ă": "a",
        "ằ": "a",
        "ắ": "a",
        "ặ": "a",
        "ẳ": "a",
        "ẵ": "a",
        "è": "e",
        "é": "e",
        "ẹ": "e",
        "ẻ": "e",
        "ẽ": "e",
        "ê": "e",
        "ề": "e",
        "ế": "e",
        "ệ": "e",
        "ể": "e",
        "ễ": "e",
        "ì": "i",
        "í": "i",
        "ị": "i",
        "ỉ": "i",
        "ĩ": "i",
        "ò": "o",
        "ó": "o",
        "ọ": "o",
        "ỏ": "o",
        "õ": "o",
        "ô": "o",
        "ồ": "o",
        "ố": "o",
        "ộ": "o",
        "ổ": "o",
        "ỗ": "o",
        "ơ": "o",
        "ờ": "o",
        "ớ": "o",
        "ợ": "o",
        "ở": "o",
        "ỡ": "o",
        "ù": "u",
        "ú": "u",
        "ụ": "u",
        "ủ": "u",
        "ũ": "u",
        "ư": "u",
        "ừ": "u",
        "ứ": "u",
        "ự": "u",
        "ử": "u",
        "ữ": "u",
        "ỳ": "y",
        "ý": "y",
        "ỵ": "y",
        "ỷ": "y",
        "ỹ": "y",
        "đ": "d",
    }
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def _title_case_ascii(text: str) -> str:
    words = [word for word in re.split(r"\s+", text.strip()) if word]
    return " ".join(word[:1].upper() + word[1:] for word in words)
