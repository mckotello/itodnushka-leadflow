import json

from sqlalchemy.orm import Session

from models import Lead
from services.ai_service import analyze_lead
from services.telegram_service import send_telegram_message


def create_lead(
    db: Session,
    name: str,
    company: str | None,
    contact: str,
    message: str,
    budget: str | None,
) -> Lead:

    lead = Lead(
        name=name,
        company=company,
        contact=contact,
        message=message,
        budget=budget,
        status="new",
        ai_status="pending",
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    analyze_lead_for_lead(
        db=db,
        lead=lead,
    )

    send_lead_telegram_notification(lead)

    return lead


def analyze_lead_for_lead(
    db: Session,
    lead: Lead,
) -> bool:
    """
    Выполняет AI-анализ существующей заявки.

    Возвращает:
    True — анализ успешно выполнен.
    False — произошла ошибка.
    """

    lead.ai_status = "pending"

    db.commit()
    db.refresh(lead)

    try:
        analysis = analyze_lead(
            message=lead.message,
            budget=lead.budget,
        )

        lead.ai_category = analysis.category
        lead.ai_priority = analysis.priority
        lead.ai_features = json.dumps(
            analysis.features,
            ensure_ascii=False,
        )
        lead.ai_estimate = analysis.estimate
        lead.ai_status = "completed"

        db.commit()
        db.refresh(lead)

        return True

    except Exception as error:
        lead.ai_status = "failed"

        db.commit()
        db.refresh(lead)

        print(
            f"Ошибка AI-анализа заявки #{lead.id}: {error}"
        )

        return False


def send_lead_telegram_notification(
    lead: Lead,
) -> None:

    if lead.ai_status == "completed":

        features = json.loads(
            lead.ai_features or "[]"
        )

        features_text = "\n".join(
            f"• {feature}"
            for feature in features
        )

        category_labels = {
            "web": "Веб-проект",
            "mobile": "Мобильное приложение",
            "automation": "Автоматизация",
            "integration": "Интеграция",
            "bot": "Telegram-бот",
            "other": "Другое",
        }

        priority_labels = {
            "low": "Низкий",
            "medium": "Средний",
            "high": "Высокий",
        }

        category = category_labels.get(
            lead.ai_category,
            lead.ai_category,
        )

        priority = priority_labels.get(
            lead.ai_priority,
            lead.ai_priority,
        )

        ai_block = (
            f"Статус AI: выполнен\n\n"
            f"Категория: {category}\n"
            f"Приоритет: {priority}\n"
            f"Сложность: {lead.ai_estimate}\n\n"
            f"Функции:\n"
            f"{features_text or '• не определены'}"
        )

    elif lead.ai_status == "failed":

        ai_block = (
            "Статус AI: ошибка\n\n"
            "AI-анализ не выполнен.\n"
            "Заявка сохранена."
        )

    else:

        ai_block = (
            "Статус AI: обработка"
        )

    telegram_message = (
        f"Новая заявка в ITоднушка LeadFlow\n\n"
        f"Заявка #{lead.id}\n\n"
        f"Клиент: {lead.name}\n"
        f"Компания: {lead.company or 'не указана'}\n"
        f"Контакт: {lead.contact}\n"
        f"Бюджет: {lead.budget or 'не указан'}\n\n"
        f"Что нужно:\n"
        f"{lead.message}\n\n"
        f"AI-анализ\n\n"
        f"{ai_block}"
    )

    try:
        send_telegram_message(
            telegram_message
        )

    except Exception as error:
        print(
            f"Ошибка отправки Telegram-уведомления "
            f"для заявки #{lead.id}: {error}"
        )


def get_leads(db: Session) -> list[Lead]:
    return (
        db.query(Lead)
        .order_by(Lead.id.desc())
        .all()
    )


def get_lead(
    db: Session,
    lead_id: int,
) -> Lead | None:
    return db.get(Lead, lead_id)


def update_status(
    db: Session,
    lead: Lead,
    status: str,
) -> Lead:

    lead.status = status

    db.commit()
    db.refresh(lead)

    return lead