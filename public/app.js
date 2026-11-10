const details = {
    graduation: ["🎓", "Research internships and scholarships for undergraduate students."],
    masters: ["🏫", "Graduate programs, funding opportunities, and admission deadlines."],
    industry: ["💼", "Internships and early-career opportunities in industry."],
    conferences: ["📚", "Calls for papers, submission deadlines, and conference dates."],
    ai_ml_research_fellowships: ["🤖", "AI/ML research programs, fellowships, and courses."],
    personal: ["🗂️", "A personal shortlist of opportunities and important dates."],
    all: ["🌐", "Every published opportunity in one combined calendar."],
};

function getHighlights(opportunities, track) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    return opportunities
        .filter(opportunity => track === "all" || opportunity.track === track)
        .map(opportunity => ({
            opportunity,
            milestone: opportunity.milestones
                .filter(item => new Date(`${item.start_date}T00:00:00`) >= today)
                .sort((a, b) => a.start_date.localeCompare(b.start_date))[0],
        }))
        .filter(highlight => highlight.milestone)
        .sort((a, b) => a.milestone.start_date.localeCompare(b.milestone.start_date))
        .slice(0, 3);
}

function renderHighlights(opportunities, track) {
    const highlights = getHighlights(opportunities, track);
    if (!highlights.length) return '<p class="no-highlights">No upcoming dates.</p>';

    return `<ul class="highlights">${highlights.map(({ opportunity, milestone }) => {
        const date = new Date(`${milestone.start_date}T00:00:00`).toLocaleDateString(
            "en-US",
            { day: "numeric", month: "short", year: "numeric" },
        );
        const label = milestone.kind.replaceAll("-", " ");
        return `<li><strong>${opportunity.title}</strong><span>${date} · ${label}</span></li>`;
    }).join("")}</ul>`;
}

function renderCalendars(calendars, opportunities) {
    const list = document.querySelector("#calendar-list");
    list.innerHTML = calendars.map(calendar => {
        const [icon, description] = details[calendar.id];
        const calendarUrl = new URL(calendar.ics_url, window.location.href).href;
        const datasetLink = calendar.csv_url
            ? `<a href="${calendar.csv_url}" class="btn btn-download" aria-label="View ${calendar.name} dataset">View Dataset</a>`
            : "";

        return `
            <article class="card">
                <div class="card-header"><h2><span aria-hidden="true">${icon}</span> ${calendar.name}</h2></div>
                <p class="card-description">${description}</p>
                <h3>Upcoming highlights</h3>
                ${renderHighlights(opportunities, calendar.id)}
                <div class="subscription-url">
                    Calendar URL: <a href="${calendarUrl}">${calendarUrl}</a>
                </div>
                <div class="card-links">
                    <a href="${calendarUrl}" class="btn btn-subscribe" aria-label="Subscribe to ${calendar.name}">Subscribe Calendar</a>
                    <a href="${calendar.ics_url}" class="btn btn-download" aria-label="Download ${calendar.name}" download>Download .ics</a>
                    ${datasetLink}
                </div>
            </article>`;
    }).join("");
    list.setAttribute("aria-busy", "false");
}

function fetchJson(path) {
    return fetch(path).then(response => {
        if (!response.ok) throw new Error(`Could not load ${path}`);
        return response.json();
    });
}

Promise.all([
    fetchJson("calendars.json"),
    fetchJson("opportunities.json"),
])
    .then(([calendars, opportunities]) => {
        renderCalendars(calendars, opportunities);
        calendars.forEach(calendar => {
            const counter = document.querySelector(`[data-track="${calendar.id}"]`);
            if (counter) counter.textContent = calendar.event_count;
        });
    })
    .catch(() => {
        const list = document.querySelector("#calendar-list");
        list.setAttribute("aria-busy", "false");
        list.innerHTML = '<p class="load-status error">Calendars could not be loaded. Please try again later.</p>';
    });
