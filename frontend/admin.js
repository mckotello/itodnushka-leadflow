const API_URL = "http://127.0.0.1:8000";

const leadsList = document.getElementById("leads-list");

const totalCount = document.getElementById("total-count");
const newCount = document.getElementById("new-count");
const inProgressCount = document.getElementById("in-progress-count");
const doneCount = document.getElementById("done-count");

const searchInput = document.getElementById("search-input");
const statusFilter = document.getElementById("status-filter");
const priorityFilter = document.getElementById("priority-filter");
const resetFilters = document.getElementById("reset-filters");

let allLeads = [];


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
        console.error(
            "Ошибка чтения AI-функций:",
            error
        );

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


function renderAiAnalysis(lead) {
    const features = parseFeatures(
        lead.ai_features
    );

    const featuresHtml = features.length
        ? `
            <div class="ai-features">
                ${features
                    .map(
                        (feature) => `
                            <span class="ai-feature">
                                ${escapeHtml(feature)}
                            </span>
                        `
                    )
                    .join("")}
            </div>
        `
        : `
            <div class="ai-empty">
                Функции не определены
            </div>
        `;

    return `
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

                ${featuresHtml}

            </div>

        </div>
    `;
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

    return `
        <article class="lead">

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


            <div class="lead-message">
                ${escapeHtml(lead.message)}
            </div>


            <div class="lead-meta">

                <span class="tag">
                    Создана:
                    ${escapeHtml(formattedDate)}
                </span>

                <span class="tag">
                    Контакт:
                    ${escapeHtml(
                        lead.contact
                    )}
                </span>

                <span class="tag">
                    Бюджет:
                    ${escapeHtml(
                        lead.budget ||
                        "Не указан"
                    )}
                </span>

            </div>


            ${renderAiAnalysis(lead)}


            <div class="actions">

                <a
                    href="lead.html?id=${lead.id}"
                    class="button-link"
                >
                    Открыть
                </a>

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

        </article>
    `;
}


function updateStats(leads) {
    totalCount.textContent =
        leads.length;

    newCount.textContent =
        leads.filter(
            (lead) =>
                lead.status === "new"
        ).length;

    inProgressCount.textContent =
        leads.filter(
            (lead) =>
                lead.status === "in_progress"
        ).length;

    doneCount.textContent =
        leads.filter(
            (lead) =>
                lead.status === "done"
        ).length;
}


function renderFilteredLeads() {
    const search = searchInput.value
        .trim()
        .toLowerCase();

    const status = statusFilter.value;
    const priority = priorityFilter.value;

    const filteredLeads = allLeads.filter((lead) => {

        const matchesSearch =
            !search ||
            String(lead.id).includes(search) ||
            lead.name
                .toLowerCase()
                .includes(search) ||
            (lead.company || "")
                .toLowerCase()
                .includes(search) ||
            lead.contact
                .toLowerCase()
                .includes(search);

        const matchesStatus =
            status === "all" ||
            lead.status === status;

        const matchesPriority =
            priority === "all" ||
            lead.ai_priority === priority;

        return (
            matchesSearch &&
            matchesStatus &&
            matchesPriority
        );
    });


    if (!filteredLeads.length) {
        leadsList.innerHTML = `
            <div class="empty">
                По заданным условиям заявки не найдены
            </div>
        `;

        return;
    }


    leadsList.innerHTML = filteredLeads
        .map(renderLead)
        .join("");
}


async function loadLeads() {
    try {
        const response = await fetch(
            `${API_URL}/leads`
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const leads =
            await response.json();

        allLeads = leads;

        updateStats(leads);

        if (!leads.length) {
            leadsList.innerHTML = `
                <div class="empty">
                    Заявок пока нет
                </div>
            `;

            return;
        }

        renderFilteredLeads();

    } catch (error) {
        console.error(
            "Ошибка загрузки заявок:",
            error
        );

        leadsList.innerHTML = `
            <div class="empty">
                Не удалось загрузить заявки.
                Проверь, запущен ли FastAPI.
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

        await loadLeads();

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


searchInput.addEventListener(
    "input",
    renderFilteredLeads
);


statusFilter.addEventListener(
    "change",
    renderFilteredLeads
);


priorityFilter.addEventListener(
    "change",
    renderFilteredLeads
);


resetFilters.addEventListener(
    "click",
    () => {
        searchInput.value = "";
        statusFilter.value = "all";
        priorityFilter.value = "all";

        renderFilteredLeads();
    }
);


loadLeads();


setInterval(
    loadLeads,
    10000
);