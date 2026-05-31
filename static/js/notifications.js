const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]') ? document.querySelector('[name=csrfmiddlewaretoken]').value : '';

function readNotif(id, redirectUrl) {
    fetch(`/notifications/read/${id}/`, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken}
    }).then(() => {
        window.location.href = redirectUrl;
    });
}

function markAllRead() {
    fetch(`/notifications/read-all/`, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken}
    }).then(() => {
        window.location.reload();
    });
}

// Poll every 30 seconds
setInterval(() => {
    fetch(`/notifications/poll/`)
    .then(r => r.json())
    .then(data => {
        if(data.status === 'success' && data.unread_count > 0) {
            // pulse badge logic
            const badge = document.getElementById('nav-bell');
            if (badge) {
                badge.style.color = 'var(--primary-red)';
                badge.classList.add('pulse-anim');
            }
        }
    });
}, 30000);
