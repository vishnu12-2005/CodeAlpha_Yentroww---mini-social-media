// Stories Logic - Full Implementation
let currentStoryUserId = null;
let currentStories = [];
let currentStoryIndex = 0;
let storyTimer = null;
let storyProgressTimer = null;
const STORY_DURATION = 5000; // 5 seconds per story

function openStoryViewer(userId) {
    currentStoryUserId = userId;
    currentStoryIndex = 0;
    
    const overlay = document.getElementById('story-viewer-overlay');
    overlay.style.display = 'block';
    
    // Fetch stories for this user via API
    fetch(`/stories/user/${userId}/`)
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success' && data.stories.length > 0) {
                currentStories = data.stories;
                
                // Set user info
                document.getElementById('story-avatar').src = data.avatar_url;
                document.getElementById('story-username').innerText = '@' + data.username;
                
                // Show/hide reply bar based on whether it's own story
                const replyBar = document.getElementById('story-reply-bar');
                if (data.is_self) {
                    replyBar.style.display = 'none';
                } else {
                    replyBar.style.display = 'flex';
                }
                
                // Build progress bars
                buildProgressBars(data.stories.length);
                
                // Show first story
                showStory(0);
            } else {
                closeStoryViewer();
            }
        })
        .catch(err => {
            console.error('Error fetching stories:', err);
            closeStoryViewer();
        });
}

function buildProgressBars(count) {
    const container = document.getElementById('story-progress-container');
    container.innerHTML = '';
    for (let i = 0; i < count; i++) {
        const bar = document.createElement('div');
        bar.style.cssText = 'flex: 1; height: 3px; background: rgba(255,255,255,0.3); border-radius: 2px; overflow: hidden;';
        const fill = document.createElement('div');
        fill.style.cssText = 'width: 0%; height: 100%; background: white; transition: none; border-radius: 2px;';
        fill.id = `story-progress-${i}`;
        bar.appendChild(fill);
        container.appendChild(bar);
    }
}

function showStory(index) {
    if (index < 0 || index >= currentStories.length) {
        // Move to next user's stories or close
        closeStoryViewer();
        return;
    }
    
    currentStoryIndex = index;
    const story = currentStories[index];
    const container = document.getElementById('story-media-container');
    
    // Remove old media (but keep navigation areas)
    const oldMedia = container.querySelector('.story-media-element');
    if (oldMedia) oldMedia.remove();
    
    // Set time
    document.getElementById('story-time').innerText = story.created_at;
    
    // Insert media
    if (story.media_type === 'video') {
        const video = document.createElement('video');
        video.className = 'story-media-element';
        video.src = story.media_url;
        video.style.cssText = 'max-width: 100%; max-height: 100%; object-fit: contain; position: absolute; top: 0; left: 0; width: 100%; height: 100%;';
        video.autoplay = true;
        video.muted = true;
        video.playsInline = true;
        container.insertBefore(video, container.firstChild);
    } else {
        const img = document.createElement('img');
        img.className = 'story-media-element';
        img.src = story.media_url;
        img.style.cssText = 'max-width: 100%; max-height: 100%; object-fit: contain; position: absolute; top: 0; left: 0; width: 100%; height: 100%;';
        container.insertBefore(img, container.firstChild);
    }
    
    // Mark as viewed
    fetch(`/stories/${story.id}/view/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrftoken }
    });
    
    // Update progress bars
    resetProgressBars(index);
    startProgress(index);
}

function resetProgressBars(upTo) {
    for (let i = 0; i < currentStories.length; i++) {
        const fill = document.getElementById(`story-progress-${i}`);
        if (fill) {
            if (i < upTo) {
                fill.style.transition = 'none';
                fill.style.width = '100%';
            } else if (i === upTo) {
                fill.style.transition = 'none';
                fill.style.width = '0%';
            } else {
                fill.style.transition = 'none';
                fill.style.width = '0%';
            }
        }
    }
}

function startProgress(index) {
    clearTimeout(storyTimer);
    
    const fill = document.getElementById(`story-progress-${index}`);
    if (fill) {
        // Small delay to allow the transition reset to take effect
        requestAnimationFrame(() => {
            fill.style.transition = `width ${STORY_DURATION}ms linear`;
            fill.style.width = '100%';
        });
    }
    
    storyTimer = setTimeout(() => {
        nextStory();
    }, STORY_DURATION);
}

function nextStory() {
    clearTimeout(storyTimer);
    if (currentStoryIndex + 1 < currentStories.length) {
        showStory(currentStoryIndex + 1);
    } else {
        // Try next user
        const currentIdx = storiesData.findIndex(s => s.user_id === currentStoryUserId);
        if (currentIdx >= 0 && currentIdx + 1 < storiesData.length) {
            const nextUser = storiesData[currentIdx + 1];
            if (nextUser.has_stories) {
                openStoryViewer(nextUser.user_id);
            } else {
                closeStoryViewer();
            }
        } else {
            closeStoryViewer();
        }
    }
}

function prevStory() {
    clearTimeout(storyTimer);
    if (currentStoryIndex > 0) {
        showStory(currentStoryIndex - 1);
    } else {
        // Try previous user
        const currentIdx = storiesData.findIndex(s => s.user_id === currentStoryUserId);
        if (currentIdx > 0) {
            const prevUser = storiesData[currentIdx - 1];
            if (prevUser.has_stories) {
                openStoryViewer(prevUser.user_id);
            }
        }
    }
}

function closeStoryViewer() {
    clearTimeout(storyTimer);
    const overlay = document.getElementById('story-viewer-overlay');
    if (overlay) overlay.style.display = 'none';
    
    // Clean up media
    const container = document.getElementById('story-media-container');
    const oldMedia = container.querySelector('.story-media-element');
    if (oldMedia) oldMedia.remove();
    
    // Clear reply input
    const replyInput = document.getElementById('story-reply-input');
    if (replyInput) replyInput.value = '';
    
    currentStories = [];
    currentStoryIndex = 0;
}

function sendStoryReply() {
    const input = document.getElementById('story-reply-input');
    const text = input.value.trim();
    if (!text || currentStories.length === 0) return;
    
    const story = currentStories[currentStoryIndex];
    
    fetch(`/stories/${story.id}/reply/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ text: text })
    }).then(r => r.json()).then(data => {
        if (data.status === 'success') {
            input.value = '';
            // Show brief confirmation
            input.placeholder = '✓ Reply sent!';
            setTimeout(() => {
                input.placeholder = 'Reply to story...';
            }, 2000);
        }
    });
}

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    const overlay = document.getElementById('story-viewer-overlay');
    if (overlay && overlay.style.display === 'block') {
        if (e.key === 'ArrowRight') nextStory();
        else if (e.key === 'ArrowLeft') prevStory();
        else if (e.key === 'Escape') closeStoryViewer();
    }
});
