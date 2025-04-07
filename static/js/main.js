// main.js
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 3 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        message.style.transition = 'opacity 0.5s ease';
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 500);
        }, 3000);
    });

    // Format article previews
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

    // Setup image previews
    setupImagePreviews();

    // Setup mobile navigation
    setupMobileNavigation();

    // Setup category dropdown
    setupCategoryDropdown();

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

    // Image preview setup function
    function setupImagePreviews() {
        const imageInput = document.getElementById('image');
        if (imageInput) {
            // Check if there's an existing image
            const currentImageContainer = document.querySelector('.current-image');

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
                            previewContainer.innerHTML = '<p>New image preview:</p>';
                            imageInput.parentNode.appendChild(previewContainer);
                        }

                        // Create or update image preview
                        let previewImg = previewContainer.querySelector('img');
                        if (!previewImg) {
                            previewImg = document.createElement('img');
                            previewImg.style.maxWidth = '100%';
                            previewImg.style.maxHeight = '300px';
                            previewImg.style.marginTop = '10px';
                            previewImg.style.borderRadius = '4px';
                            previewImg.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
                            previewContainer.appendChild(previewImg);
                        }

                        previewImg.src = e.target.result;

                        // Hide the current image if it exists
                        if (currentImageContainer) {
                            currentImageContainer.style.display = 'none';
                        }
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
    }

    // Mobile navigation setup function
    function setupMobileNavigation() {
        const nav = document.querySelector('nav');
        if (!nav) return;

        // Only create toggle for mobile view
        if (window.innerWidth <= 768) {
            // Create toggle button if it doesn't exist
            let navToggle = document.querySelector('.nav-toggle');
            if (!navToggle) {
                navToggle = document.createElement('button');
                navToggle.className = 'nav-toggle';
                navToggle.innerHTML = '☰';
                navToggle.style.position = 'absolute';
                navToggle.style.right = '20px';
                navToggle.style.top = '15px';
                navToggle.style.background = 'none';
                navToggle.style.border = 'none';
                navToggle.style.fontSize = '1.5rem';
                navToggle.style.color = '#e94842'; // Updated to match our primary color
                navToggle.style.cursor = 'pointer';
                navToggle.style.zIndex = '1001';

                nav.parentNode.insertBefore(navToggle, nav);
            }

            const navLinks = document.querySelector('.nav-links');
            if (navLinks) {
                // Setup mobile menu styling
                navLinks.style.display = 'none';
                navLinks.style.flexDirection = 'column';
                navLinks.style.width = '100%';
                navLinks.style.position = 'absolute';
                navLinks.style.top = '60px';
                navLinks.style.left = '0';
                navLinks.style.background = '#fff';
                navLinks.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
                navLinks.style.zIndex = '1000';
                navLinks.style.padding = '1rem 0';

                // Clear previous event listener
                navToggle.replaceWith(navToggle.cloneNode(true));
                navToggle = document.querySelector('.nav-toggle');

                // Add event listener
                navToggle.addEventListener('click', function() {
                    if (navLinks.style.display === 'none') {
                        navLinks.style.display = 'flex';
                    } else {
                        navLinks.style.display = 'none';
                    }
                });
            }
        }
    }

    // Category dropdown setup function
    function setupCategoryDropdown() {
        const categoryDropdowns = document.querySelectorAll('.categories-dropdown');

        categoryDropdowns.forEach(dropdown => {
            const toggle = dropdown.querySelector('.dropdown-toggle');
            const menu = dropdown.querySelector('.dropdown-menu');

            if (toggle && menu) {
                // On mobile, use click instead of hover
                if (window.innerWidth <= 768) {
                    toggle.addEventListener('click', function(e) {
                        e.preventDefault();
                        if (menu.style.display === 'block') {
                            menu.style.display = 'none';
                        } else {
                            menu.style.display = 'block';
                        }
                    });

                    // Close the dropdown when clicking elsewhere
                    document.addEventListener('click', function(e) {
                        if (!dropdown.contains(e.target)) {
                            menu.style.display = 'none';
                        }
                    });
                }
            }
        });
    }

    // Handle window resize for responsive navigation
    window.addEventListener('resize', function() {
        const navLinks = document.querySelector('.nav-links');
        const navToggle = document.querySelector('.nav-toggle');

        if (navLinks) {
            if (window.innerWidth > 768) {
                navLinks.style.display = 'flex';
                navLinks.style.flexDirection = 'row';
                navLinks.style.position = 'static';
                navLinks.style.boxShadow = 'none';
                navLinks.style.width = 'auto';
                navLinks.style.padding = '0';

                if (navToggle) {
                    navToggle.style.display = 'none';
                }
            } else {
                navLinks.style.display = 'none';

                if (navToggle) {
                    navToggle.style.display = 'block';
                } else {
                    setupMobileNavigation();
                }
            }
        }

        // Reinitialize category dropdown for the new screen size
        setupCategoryDropdown();
    });
});