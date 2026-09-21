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

    # 1. Сначала сохраняем заявку.
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

    # 2. Выполняем AI-анализ.
    analysis = None

    try:
        analysis = analyze_lead(
            message=message,
            budget=budget,
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

    except Exception as error:
        lead.ai_status = "failed"

        db.commit()
        db.refresh(lead)

        print(
            f"Ошибка AI-анализа заявки #{lead.id}: {error}"
        )

    # 3. Формируем Telegram-уведомление.
    if analysis:
        features = "\n".join(
            f"• {feature}"
            for feature in analysis.features
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
            analysis.category,
            analysis.category,
        )

        priority = priority_labels.get(
            analysis.priority,
            analysis.priority,
        )

        ai_block = (
            f"Статус AI: выполнен\n\n"
            f"Категория: {category}\n"
            f"Приоритет: {priority}\n"
            f"Сложность: {analysis.estimate}\n\n"
            f"Функции:\n"
            f"{features or '• не определены'}"
        )

    else:
        ai_block = (
            "Статус AI: ошибка\n\n"
            "AI временно недоступен.\n"
            "Заявка сохранена без AI-анализа."
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

    # 4. Telegram не должен ломать создание заявки.
    try:
        send_telegram_message(
            telegram_message
        )

    except Exception as error:
        print(
            f"Ошибка отправки Telegram-уведомления "
            f"для заявки #{lead.id}: {error}"
        )

    return lead


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