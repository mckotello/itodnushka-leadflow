import json

import httpx
from pydantic import BaseModel


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"


class LeadAnalysis(BaseModel):
    category: str
    priority: str
    features: list[str]
    estimate: str


def analyze_lead(
    message: str,
    budget: str | None = None,
) -> LeadAnalysis:
    prompt = f"""
Ты AI-аналитик IT-студии.

Твоя задача — внимательно проанализировать реальную заявку клиента
и извлечь из неё конкретные требования.

ТЕКСТ ЗАЯВКИ:
{message}

БЮДЖЕТ:
{budget or "не указан"}

Правила:

1. category:
Определи тип проекта:
- web — сайт или веб-сервис
- mobile — мобильное приложение
- automation — автоматизация процессов
- integration — интеграция систем
- bot — Telegram/чат-бот
- other — другое

2. priority:
Определи приоритет:
- low — простая задача без срочности
- medium — обычная коммерческая задача
- high — явно срочная или критичная задача

Если срочность не указана, используй "medium".

3. features:
Извлеки ТОЛЬКО конкретные функции и требования,
которые действительно присутствуют в заявке.

Например, если клиент написал:
"Нужен сайт с каталогом товаров и формой заказа"

нужно вернуть:

[
    "каталог товаров",
    "форма заказа"
]

НЕ пиши:
"список функций или требований"
"краткая предварительная оценка сложности"
"требуется уточнение"

4. estimate:
Дай короткую предварительную оценку сложности проекта:
- низкая
- средняя
- высокая

Оценивай только по информации из заявки.

5. Не придумывай требования.

6. Ответ должен содержать ТОЛЬКО JSON.

Формат ответа:

{{
    "category": "web",
    "priority": "medium",
    "features": [
        "конкретная функция 1",
        "конкретная функция 2"
    ],
    "estimate": "средняя"
}}
"""

    response = httpx.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        },
        timeout=120.0,
    )

    response.raise_for_status()

    data = response.json()
    result = data["response"]

    parsed = json.loads(result)

    analysis = LeadAnalysis.model_validate(parsed)

    forbidden_features = {
        "список функций или требований",
        "краткая предварительная оценка сложности",
        "требуется уточнение",
    }

    analysis.features = [
        feature
        for feature in analysis.features
        if feature.lower().strip() not in forbidden_features
    ]

    if analysis.priority not in {"low", "medium", "high"}:
        analysis.priority = "medium"

    if analysis.category not in {
        "web",
        "mobile",
        "automation",
        "integration",
        "bot",
        "other",
    }:
        analysis.category = "other"

    if analysis.estimate not in {
        "низкая",
        "средняя",
        "высокая",
    }:
        analysis.estimate = "средняя"

    return analysis