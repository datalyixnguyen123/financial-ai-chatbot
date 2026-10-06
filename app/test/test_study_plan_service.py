
from app.services.study_plan_service import (
    build_study_plan_context,
    clear_study_roadmap,
    get_study_roadmap,
    process_study_goal_message,
    toggle_study_action,
)

def setup_function():
    clear_study_roadmap()

def test_process_study_goal_message_creates_plan():
    plan = process_study_goal_message(
        "Toi muon dat muc tieu IELTS 7.0 trong 60 ngay"
    )
    assert plan is not None
    assert plan["topic"] == "Tiếng Anh IELTS"
    assert plan["target_label"] == "Target IELTS 7.0"
    assert plan["days_remaining"] > 0
    assert len(plan["actions"]) == 4

    roadmap = get_study_roadmap()
    assert roadmap["has_plans"] is True
    assert roadmap["total_plans"] == 1


def test_process_study_goal_message_ignores_non_study_text():
    plan = process_study_goal_message("Hom nay minh vua an com xong")
    roadmap = get_study_roadmap()
    assert plan is None
    assert roadmap["has_plans"] is False
    assert roadmap["plans"] == []


def test_toggle_study_action_updates_progress():
    plan = process_study_goal_message(
        "Toi muon hoc Python trong 30 ngay"
    )
    action = plan["actions"][0]
    updated_plan = toggle_study_action(
        plan_id = plan["id"],
        action_id = action["id"],
        completed = True,
    )
    assert updated_plan is not None
    assert updated_plan["completed_actions"] == 1
    assert updated_plan["progress_percent"] == 25
    assert updated_plan["actions"][0]["completed"] is True


def test_build_study_plan_context_returns_summary_when_plan_exists():
    plan = process_study_goal_message(
        "Toi muon dat muc tieu GPA 3.6 cho mon Giai tich trong 45 ngay"
    )
    context = build_study_plan_context(
        "Tien do hoc cua minh den dau roi?",
        updated_plan=plan,
    )
    assert "STUDY ROADMAP UPDATE" in context
    assert "Giải Tích" in context
    assert "Mục tiêu GPA 3.6" in context
