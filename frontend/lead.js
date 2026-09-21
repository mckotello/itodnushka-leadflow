const API_URL = "http://127.0.0.1:8000";

const leadDetails =
    document.getElementById("lead-details");


function escapeHtml(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function parseFeatures(value) {
    if (!value) {
        return [];
    }

    try {
        const features = JSON.parse(value);

        return Array.isArray(features)
            ? features
            : [];
    } catch (error) {
        return [];
    }
}


function getStatusLabel(status) {
    const labels = {
        new: "Новая",
        in_progress: "В работе",
        done: "Завершена",
        cancelled: "Отменена",
    };

    return labels[status] || status;
}


function getCategoryLabel(category) {
    const labels = {
        web: "Веб-проект",
        mobile: "Мобильное приложение",
        automation: "Автоматизация",
        integration: "Интеграция",
        bot: "Telegram-бот",
        other: "Другое",
    };

    return labels[category] || category || "Не определена";
}


function getPriorityLabel(priority) {
    const labels = {
        low: "Низкий",
        medium: "Средний",
        high: "Высокий",
    };

    return labels[priority] || priority || "Не определён";
}


function getStatusClass(status) {
    const classes = {
        new: "status-new",
        in_progress: "status-progress",
        done: "status-done",
        cancelled: "status-cancelled",
    };

    return classes[status] || "";
}


function renderLead(lead) {
    const createdAt = new Date(
        lead.created_at
    );

    const formattedDate =
        createdAt.toLocaleString(
            "ru-RU",
            {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
            }
        );

    const features = parseFeatures(
        lead.ai_features
    );

    const featuresHtml = features.length
        ? features
            .map(
                (feature) => `
                    <span class="ai-feature">
                        ${escapeHtml(feature)}
                    </span>
                `
            )
            .join("")
        : `
            <span class="ai-empty">
                Функции не определены
            </span>
        `;

    return `
        <div class="lead">

            <div class="lead-top">

                <div>
                    <div class="lead-id">
                        Заявка #${lead.id}
                    </div>

                    <div class="lead-name">
                        ${escapeHtml(lead.name)}
                    </div>

                    ${
                        lead.company
                            ? `
                                <div class="lead-company">
                                    ${escapeHtml(
                                        lead.company
                                    )}
                                </div>
                            `
                            : ""
                    }
                </div>

                <div
                    class="tag status ${getStatusClass(
                        lead.status
                    )}"
                >
                    ${escapeHtml(
                        getStatusLabel(
                            lead.status
                        )
                    )}
                </div>

            </div>


            <div class="lead-meta">

                <span class="tag">
                    Создана:
                    ${escapeHtml(formattedDate)}
                </span>

                <span class="tag">
                    Контакт:
                    ${escapeHtml(lead.contact)}
                </span>

                <span class="tag">
                    Бюджет:
                    ${escapeHtml(
                        lead.budget ||
                        "Не указан"
                    )}
                </span>

            </div>


            <div class="lead-message">
                ${escapeHtml(lead.message)}
            </div>


            <div class="ai-analysis">

                <div class="ai-title">
                    AI-анализ
                </div>


                <div class="ai-grid">

                    <div class="ai-item">

                        <span class="ai-label">
                            Категория
                        </span>

                        <strong>
                            ${escapeHtml(
                                getCategoryLabel(
                                    lead.ai_category
                                )
                            )}
                        </strong>

                    </div>


                    <div class="ai-item">

                        <span class="ai-label">
                            Приоритет
                        </span>

                        <strong
                            class="ai-priority ai-priority-${escapeHtml(
                                lead.ai_priority
                            )}"
                        >
                            ${escapeHtml(
                                getPriorityLabel(
                                    lead.ai_priority
                                )
                            )}
                        </strong>

                    </div>


                    <div class="ai-item">

                        <span class="ai-label">
                            Сложность
                        </span>

                        <strong>
                            ${escapeHtml(
                                lead.ai_estimate ||
                                "Не определена"
                            )}
                        </strong>

                    </div>

                </div>


                <div class="ai-functions">

                    <span class="ai-label">
                        Выявленные функции
                    </span>

                    <div class="ai-features">
                        ${featuresHtml}
                    </div>

                </div>

            </div>


            <div class="actions">

                <button
                    onclick="updateStatus(
                        ${lead.id},
                        'new'
                    )"
                >
                    Новая
                </button>

                <button
                    onclick="updateStatus(
                        ${lead.id},
                        'in_progress'
                    )"
                >
                    В работу
                </button>

                <button
                    onclick="updateStatus(
                        ${lead.id},
                        'done'
                    )"
                >
                    Завершить
                </button>

                <button
                    onclick="updateStatus(
                        ${lead.id},
                        'cancelled'
                    )"
                >
                    Отменить
                </button>

            </div>

        </div>
    `;
}


async function loadLead() {
    const params =
        new URLSearchParams(
            window.location.search
        );

    const leadId =
        params.get("id");

    if (!leadId) {
        leadDetails.innerHTML = `
            <div class="empty">
                Не указана заявка.
            </div>
        `;

        return;
    }

    try {
        const response = await fetch(
            `${API_URL}/leads/${leadId}`
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const lead =
            await response.json();

        document.title =
            `LeadFlow — заявка #${lead.id}`;

        leadDetails.innerHTML =
            renderLead(lead);

    } catch (error) {
        console.error(
            "Ошибка загрузки заявки:",
            error
        );

        leadDetails.innerHTML = `
            <div class="empty">
                Не удалось загрузить заявку.
            </div>
        `;
    }
}


async function updateStatus(
    leadId,
    status
) {
    try {
        const response = await fetch(
            `${API_URL}/leads/${leadId}/status`,
            {
                method: "PATCH",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body: JSON.stringify({
                    status,
                }),
            }
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        await loadLead();

    } catch (error) {
        console.error(
            "Ошибка изменения статуса:",
            error
        );

        alert(
            "Не удалось изменить статус заявки."
        );
    }
}


loadLead();