fetch("calendars.json")
    .then(response => response.json())
    .then(calendars => calendars.forEach(calendar => {
        const counter = document.querySelector(`[data-track="${calendar.id}"]`);
        if (counter) counter.textContent = calendar.event_count;
    }))
    .catch(() => {});
