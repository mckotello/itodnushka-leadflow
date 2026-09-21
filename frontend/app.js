const form = document.getElementById("leadForm");
const result = document.getElementById("result");


form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(form);

    const data = {
        name: formData.get("name"),
        company: formData.get("company") || null,
        contact: formData.get("contact"),
        message: formData.get("message"),
        budget: formData.get("budget") || null,
    };

    result.textContent = "Отправляем...";
    result.className = "result";


    try {
        const response = await fetch(
            "http://127.0.0.1:8000/leads",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                },

                body: JSON.stringify(data),
            }
        );


        if (!response.ok) {
            throw new Error("Ошибка отправки");
        }


        const lead = await response.json();

        result.textContent =
            `Заявка №${lead.id} успешно отправлена`;

        result.className = "result success";

        form.reset();

    } catch (error) {

        console.error(error);

        result.textContent =
            "Не удалось отправить заявку";

        result.className = "result error";
    }
});