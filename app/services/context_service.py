
from sqlalchemy.orm import Session
from app.models import UserContext
from app.services.context_extractor import extract_context


def get_or_create_context(db: Session) -> UserContext:
    context = db.query(UserContext).first()
    if context is None:
        context = UserContext(
            profile={},
            goals={},
            study={},
            time={},
            current={},
        )
        db.add(context)
        db.commit()
        db.refresh(context)
    return context

def _merge_section(existing: dict, incoming: dict | None,) -> dict:
    if incoming is None:
        return existing or {}
    merged = dict(existing or {})
    merged.update(incoming)
    return merged

def update_context(
    db: Session,
    *,
    profile: dict | None = None,
    goals: dict | None = None,
    study: dict | None = None,
    time: dict | None = None,
    current: dict | None = None,
) -> UserContext:

    context = get_or_create_context(db)
    context.profile = _merge_section(context.profile, profile,)
    context.goals = _merge_section(context.goals, goals,)
    context.study = _merge_section(context.study, study,)
    context.time = _merge_section(context.time, time,)
    context.current = _merge_section(context.current, current,)
    db.commit()
    db.refresh(context)

    return context


def apply_context_updates(db: Session, updates: dict,) -> UserContext:
    context = get_or_create_context(db)
    for section in (
        "profile",
        "goals",
        "study",
        "time",
    ):
        incoming = updates.get(section) or {}
        if incoming:
            setattr(context, section, _merge_section(getattr(context, section), incoming,),)
    current_updates = updates.get("current") or {}
    
    if current_updates:
        context.current = _merge_section(context.current, current_updates,)
    db.commit()
    db.refresh(context)

    return context

def extract_and_apply_context(db: Session, text: str, *, intent: str | None = None, entities: dict | None = None,) -> tuple[dict, UserContext]:
    result = extract_context(text, intent = intent, entities = entities,)
    context = apply_context_updates(db, result["updates"],)
    return result, context

