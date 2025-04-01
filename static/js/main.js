// main.js
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 3 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s ease';
            setTimeout(() => {
                message.style.display = 'none';
            }, 500);
        }, 3000);
    });
    function formatArticlePreviews() {
    const previewContents = document.querySelectorAll('.preview-content');
    previewContents.forEach(content => {
        // Remove extra spaces and format text consistently
        let text = content.textContent;

        // Replace multiple spaces with a single space
        text = text.replace(/\s+/g, ' ');

        // Replace link texts with cleaner format
        text = text.replace(/apasa aici|click aici|aici/gi, '');

        // Clean up the text and maintain intentional line breaks
        text = text.trim();

        content.textContent = text;
    });
}

// Call the function after page loads
formatArticlePreviews();
    // YouTube link preview functionality for admin forms
    const youtubeInput = document.getElementById('youtube_link');
    if (youtubeInput) {
        // Check if there's already a value and show preview
        if (youtubeInput.value) {
            displayYouTubePreview(youtubeInput.value);
        }

        // Add event listener for changes
        youtubeInput.addEventListener('input', function() {
            displayYouTubePreview(this.value);
        });
    }

    // TinyMCE image upload preview
    const imageInput = document.getElementById('image');
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    let previewContainer = document.querySelector('.image-preview');

                    // Create preview container if it doesn't exist
                    if (!previewContainer) {
                        previewContainer = document.createElement('div');
                        previewContainer.className = 'image-preview';
                        previewContainer.innerHTML = '<p>Image preview:</p>';
                        imageInput.parentNode.appendChild(previewContainer);
                    }

                    // Create or update image preview
                    let previewImg = previewContainer.querySelector('img');
                    if (!previewImg) {
                        previewImg = document.createElement('img');
                        previewImg.style.maxWidth = '300px';
                        previewImg.style.marginTop = '10px';
                        previewContainer.appendChild(previewImg);
                    }

                    previewImg.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Mobile navigation toggle
    const navToggle = document.createElement('button');
    navToggle.className = 'nav-toggle';
    navToggle.innerHTML = '☰';
    navToggle.style.display = 'none';

    // Add responsive navigation for mobile
    const nav = document.querySelector('nav');
    if (nav && window.innerWidth <= 768) {
        navToggle.style.display = 'block';
        navToggle.style.position = 'absolute';
        navToggle.style.right = '20px';
        navToggle.style.top = '15px';
        navToggle.style.background = 'none';
        navToggle.style.border = 'none';
        navToggle.style.fontSize = '1.5rem';
        navToggle.style.color = '#d32f2f';
        navToggle.style.cursor = 'pointer';

        nav.parentNode.insertBefore(navToggle, nav);

        const navLinks = document.querySelector('.nav-links');
        if (navLinks) {
            navLinks.style.display = 'none';
            navLinks.style.flexDirection = 'column';
            navLinks.style.width = '100%';
            navLinks.style.position = 'absolute';
            navLinks.style.top = '60px';
            navLinks.style.left = '0';
            navLinks.style.background = '#fff';
            navLinks.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
            navLinks.style.zIndex = '999';

            navToggle.addEventListener('click', function() {
                if (navLinks.style.display === 'none') {
                    navLinks.style.display = 'flex';
                } else {
                    navLinks.style.display = 'none';
                }
            });
        }
    }

    // Article confirmation before delete
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this article? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Breaking news animation adjustments
    const breakingNewsContent = document.querySelector('.breaking-news-content');
    if (breakingNewsContent) {
        // Calculate animation duration based on content length
        const contentLength = breakingNewsContent.textContent.length;
        const duration = Math.max(15, contentLength * 0.15); // Min 15s, adjust based on text length
        breakingNewsContent.style.animationDuration = `${duration}s`;
    }

    // Helper function to extract YouTube ID and display preview
    function displayYouTubePreview(url) {
        // Remove any existing preview
        const previewContainer = document.querySelector('.youtube-preview');
        if (previewContainer) {
            previewContainer.remove();
        }

        if (url) {
            const videoId = extractYoutubeId(url);
            if (videoId) {
                const preview = document.createElement('div');
                preview.className = 'youtube-preview';
                preview.innerHTML = `
                    <p>Video preview:</p>
                    <div class="youtube-thumbnail">
                        <img src="https://img.youtube.com/vi/${videoId}/mqdefault.jpg" alt="YouTube Thumbnail">
                    </div>
                `;
                youtubeInput.parentNode.appendChild(preview);
            }
        }
    }

    function extractYoutubeId(url) {
        const pattern = /(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
        const match = url.match(pattern);
        return match ? match[1] : null;
    }

    // Handle window resize for responsive navigation
    window.addEventListener('resize', function() {
        const navLinks = document.querySelector('.nav-links');
        if (navLinks) {
            if (window.innerWidth > 768) {
                navLinks.style.display = 'flex';
                navLinks.style.flexDirection = 'row';
                navLinks.style.position = 'static';
                navLinks.style.boxShadow = 'none';
                navToggle.style.display = 'none';
            } else {
                navLinks.style.display = 'none';
                navToggle.style.display = 'block';
            }
        }
    });
});