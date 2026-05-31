// Feed interactions

function togglePostMenu(postId) {
    const menu = document.getElementById(`post-menu-${postId}`);
    if (menu.style.display === 'none') {
        menu.style.display = 'block';
    } else {
        menu.style.display = 'none';
    }
}

// Close post menus when clicking elsewhere
document.addEventListener('click', function(e) {
    if (!e.target.closest('.post-menu-wrapper')) {
        document.querySelectorAll('.post-menu').forEach(m => m.style.display = 'none');
    }
});

function reportPost(postId) {
    fetch(`/posts/${postId}/report/`, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken}
    }).then(() => {
        document.getElementById(`post-menu-${postId}`).style.display = 'none';
        showToast('Post reported successfully! 🚨');
    });
}

function muteUser(username) {
    fetch(`/settings/mute/${username}/`, {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken}
    }).then(() => {
        showToast(`Muted @${username} successfully! 🔇`);
        setTimeout(() => window.location.reload(), 1000);
    });
}

function toggleComments(postId) {
    const sec = document.getElementById(`comments-section-${postId}`);
    if (sec.style.display === 'none') sec.style.display = 'block';
    else sec.style.display = 'none';
}

function submitComment(postId) {
    const input = document.getElementById(`comment-input-${postId}`);
    const text = input.value.trim();
    if (!text) return;
    
    fetch(`/posts/${postId}/comment/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ text: text })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            const list = document.getElementById(`comments-list-${postId}`);
            const div = document.createElement('div');
            div.style.marginBottom = '10px';
            div.innerHTML = `<a href="/profile/${data.comment.username}/" style="font-weight: bold;">@${data.comment.username}</a> ${data.comment.text}`;
            list.appendChild(div);
            input.value = '';
            
            // update count
            const countSpan = document.getElementById(`comment-count-${postId}`);
            countSpan.innerText = parseInt(countSpan.innerText) + 1;
        }
    });
}

function sharePost(postId) {
    // Create a share modal dynamically
    let modal = document.getElementById('share-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'share-modal';
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-card">
                <div class="modal-header">
                    <h2 class="brand-text" style="color: var(--bright-yellow); margin:0;">Share Post</h2>
                    <span class="modal-close" onclick="document.getElementById('share-modal').style.display='none'">&#10005;</span>
                </div>
                <div class="modal-body">
                    <input type="text" id="share-search-input" class="comic-input" placeholder="Search for a user..." style="margin-bottom: 0.5rem;" oninput="searchUsersForShare(this.value)">
                    <div id="share-search-results" class="dm-search-results">
                        <div class="privacy-empty" style="padding: 20px;">Type a username to share with</div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        // Close on outside click
        modal.addEventListener('click', function(e) {
            if (e.target === modal) modal.style.display = 'none';
        });
    }
    
    modal.dataset.postId = postId;
    modal.style.display = 'flex';
    setTimeout(() => document.getElementById('share-search-input').focus(), 100);
}

let shareSearchTimeout = null;
function searchUsersForShare(query) {
    clearTimeout(shareSearchTimeout);
    const resultsDiv = document.getElementById('share-search-results');
    
    if (query.trim().length < 1) {
        resultsDiv.innerHTML = '<div class="privacy-empty" style="padding: 20px;">Type a username to share with</div>';
        return;
    }

    shareSearchTimeout = setTimeout(() => {
        fetch(`/settings/search-users/?q=${encodeURIComponent(query)}`)
        .then(r => r.json())
        .then(data => {
            if (data.users.length === 0) {
                resultsDiv.innerHTML = '<div class="privacy-empty" style="padding: 20px;">No users found</div>';
                return;
            }
            let html = '';
            data.users.forEach(u => {
                html += `
                    <div class="dm-search-item" onclick="confirmShare('${u.username}')" style="cursor:pointer;">
                        <img src="${u.avatar_url}" class="avatar-hex" style="width: 40px; height: 40px;">
                        <div style="font-weight: bold;">@${u.username}</div>
                    </div>
                `;
            });
            resultsDiv.innerHTML = html;
        });
    }, 300);
}

function confirmShare(username) {
    const modal = document.getElementById('share-modal');
    const postId = modal.dataset.postId;
    const reelId = modal.dataset.reelId;
    
    let url = '';
    if (postId) {
        url = `/posts/${postId}/share/`;
    } else if (reelId) {
        url = `/reels/${reelId}/share/`;
    }
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ username: username })
    }).then(r => r.json()).then(data => {
        modal.style.display = 'none';
        if (data.status === 'success') {
            showToast("Shared successfully! 🚀");
        }
    });
}

function shareReel(reelId) {
    let modal = document.getElementById('share-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'share-modal';
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-card" style="border: 3px solid black; box-shadow: 8px 8px 0 black;">
                <div class="modal-header" style="background: var(--primary-red); border-bottom: 3px solid black;">
                    <h2 class="brand-text" style="color: var(--bright-yellow); margin:0;">Share Reel</h2>
                    <span class="modal-close" onclick="document.getElementById('share-modal').style.display='none'" style="color:white; cursor:pointer;">✕</span>
                </div>
                <div class="modal-body" style="padding: 20px;">
                    <input type="text" id="share-search-input" class="comic-input" placeholder="Search for a user..." style="margin-bottom: 0.5rem; width: 100%;" oninput="searchUsersForShare(this.value)">
                    <div id="share-search-results" class="dm-search-results">
                        <div class="privacy-empty" style="padding: 20px; text-align:center;">Type a username to share with</div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        modal.addEventListener('click', function(e) {
            if (e.target === modal) modal.style.display = 'none';
        });
    }
    
    modal.dataset.postId = '';
    modal.dataset.reelId = reelId;
    modal.style.display = 'flex';
    setTimeout(() => {
        const searchInput = document.getElementById('share-search-input');
        if (searchInput) searchInput.focus();
    }, 100);
}
