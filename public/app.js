const details = {
    graduation: ["🎓", "Research internships and scholarships for undergraduate students."],
    masters: ["🏫", "Graduate programs, funding opportunities, and admission deadlines."],
    industry: ["💼", "Internships and early-career opportunities in industry."],
    conferences: ["📚", "Calls for papers, submission deadlines, and conference dates."],
    ai_ml_research_fellowships: ["🤖", "AI/ML research programs, fellowships, and courses."],
    personal: ["🗂️", "A personal shortlist of opportunities and important dates."],
    all: ["🌐", "Every published opportunity in one combined calendar."],
};

function renderCalendars(calendars) {
    const list = document.querySelector("#calendar-list");
    list.innerHTML = calendars.map(calendar => {
        const [icon, description] = details[calendar.id];
        const calendarUrl = new URL(calendar.ics_url, window.location.href).href;
        const datasetLink = calendar.csv_url
            ? `<a href="${calendar.csv_url}" class="btn btn-download">View Dataset</a>`
            : "";

        return `
            <article class="card">
                <div class="card-header"><h2>${icon} ${calendar.name}</h2></div>
                <p class="card-description">${description}</p>
                <div class="subscription-url">
                    Calendar URL: <a href="${calendarUrl}">${calendarUrl}</a>
                </div>
                <div class="card-links">
                    <a href="${calendarUrl}" class="btn btn-subscribe">Subscribe Calendar</a>
                    <a href="${calendar.ics_url}" class="btn btn-download" download>Download .ics</a>
                    ${datasetLink}
                </div>
            </article>`;
    }).join("");
}

fetch("calendars.json")
    .then(response => response.json())
    .then(calendars => {
        renderCalendars(calendars);
        calendars.forEach(calendar => {
            const counter = document.querySelector(`[data-track="${calendar.id}"]`);
            if (counter) counter.textContent = calendar.event_count;
        });
    })
    .catch(() => {});
