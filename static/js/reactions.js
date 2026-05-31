// Reactions logic
function reactPost(postId, reactionType) {
    fetch(`/posts/${postId}/react/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ reaction_type: reactionType })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update counts
            document.getElementById(`count-yentroww-${postId}`).innerText = data.counts.yentroww;
            document.getElementById(`count-abboww-${postId}`).innerText = data.counts.abboww;
            document.getElementById(`count-sarlee-${postId}`).innerText = data.counts.sarlee;
            
            // Update active state of buttons
            const postCard = document.getElementById(`post-${postId}`);
            if (postCard) {
                postCard.querySelectorAll('.reaction-btn').forEach(btn => btn.classList.remove('active'));
                if (data.action === 'created' || data.action === 'updated') {
                    // find the clicked button and make it active
                    const btn = postCard.querySelector(`.reaction-btn[onclick="reactPost(${postId}, '${reactionType}')"]`);
                    if(btn) btn.classList.add('active');
                    
                    // Show animation
                    showReactionAnimation(`reaction-pop-${postId}`, reactionType);
                }
            }
        }
    });
}

function showReactionAnimation(popContainerId, reactionType) {
    const popContainer = document.getElementById(popContainerId);
    if (!popContainer) return;
    popContainer.innerHTML = ''; // clear existing
    
    let text = "";
    let color = "";
    let emoji = "";
    if (reactionType === 'yentroww') { text = 'YENTROWW'; color = 'var(--bright-yellow)'; emoji = '😯'; }
    else if (reactionType === 'abboww') { text = 'ABBOWW'; color = '#ff4500'; emoji = '😆'; }
    else if (reactionType === 'sarlee') { text = 'SARLEE'; color = '#4682b4'; emoji = '😏'; }
    
    popContainer.style.color = color;
    popContainer.style.animation = 'none'; // reset
    popContainer.offsetHeight; // trigger reflow
    popContainer.style.animation = 'reactionContainerAnim 1.8s forwards';
    
    // Add emoji span beside
    const emojiSpan = document.createElement('span');
    emojiSpan.innerText = emoji;
    emojiSpan.style.marginRight = '10px';
    emojiSpan.style.display = 'inline-block';
    emojiSpan.style.animation = `popLetter 0.4s forwards`;
    popContainer.appendChild(emojiSpan);
    
    // Add letters with delay
    for (let i = 0; i < text.length; i++) {
        const span = document.createElement('span');
        span.innerText = text[i];
        span.style.opacity = '0';
        span.style.display = 'inline-block';
        span.style.animation = `popLetter 0.4s forwards`;
        span.style.animationDelay = `${(i + 1) * 0.08}s`;
        popContainer.appendChild(span);
    }
    
    if (!document.getElementById('reaction-keyframes')) {
        const style = document.createElement('style');
        style.id = 'reaction-keyframes';
        style.innerHTML = `
            @keyframes popLetter {
                0% { transform: scale(0); opacity: 0; }
                60% { transform: scale(1.3); opacity: 1; }
                100% { transform: scale(1); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
}

function reactReel(reelId, reactionType) {
    fetch(`/reels/${reelId}/react/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ reaction_type: reactionType })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update counts
            const ySpan = document.getElementById(`count-reel-yentroww-${reelId}`);
            const aSpan = document.getElementById(`count-reel-abboww-${reelId}`);
            const sSpan = document.getElementById(`count-reel-sarlee-${reelId}`);
            
            if (ySpan) ySpan.innerText = data.counts.yentroww;
            if (aSpan) aSpan.innerText = data.counts.abboww;
            if (sSpan) sSpan.innerText = data.counts.sarlee;
            
            // Toggle active styling
            const activeBtn = document.querySelector(`.reaction-btn-reel[onclick="reactReel(${reelId}, '${reactionType}')"]`);
            if (activeBtn) {
                const parent = activeBtn.parentElement;
                if (parent) {
                    parent.querySelectorAll('.reaction-btn-reel').forEach(btn => btn.classList.remove('active'));
                    if (data.action === 'created' || data.action === 'updated') {
                        activeBtn.classList.add('active');
                    }
                }
            }
            
            // Show animation
            showReactionAnimation(`reaction-pop-reel-${reelId}`, reactionType);
        }
    });
}
