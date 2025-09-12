/**
 * Goondoi Wetlands - Main Application JavaScript
 * Professional web application with clean, maintainable code
 */

class AppManager {
    constructor() {
        this.currentSection = null;
        this.currentPath = window.location.pathname;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeApp();
    }

    setupEventListeners() {
        // Menu tile and footer link click handlers
        document.addEventListener('click', (e) => {
            // Handle menu tiles
            if (e.target.closest('.menu-tile')) {
                const tile = e.target.closest('.menu-tile');
                const section = tile.dataset.section;
                if (section) {
                    e.preventDefault();
                    this.loadSectionContent(section);
                }
            }
            
            // Handle footer links
            if (e.target.closest('.footer-link[data-section]')) {
                const link = e.target.closest('.footer-link[data-section]');
                const section = link.dataset.section;
                if (section) {
                    e.preventDefault();
                    this.loadSectionContent(section);
                }
            }
        });
    }

    initializeApp() {
        console.log('App initialized - Current path:', this.currentPath);
        
        if (this.currentPath === '/' || this.currentPath === '/index') {
            this.resetToCenterView();
        } else if (this.currentPath === '/admin' || this.currentPath.startsWith('/admin/')) {
            console.log('Admin page detected - skipping app UI');
        } else {
            this.minimizeNavigation();
            this.loadPageSpecificContent();
        }
    }

    loadSectionContent(section) {
        this.currentSection = section;
        this.minimizeNavigation();
        
        switch (section) {
            case 'trails':
                this.loadTrailStories();
                break;
            case 'culture':
                this.loadCultureContent();
                break;
            case 'college':
                this.loadCollegeContent();
                break;
            case 'feedback':
                this.loadFeedbackContent();
                break;
            case 'camera-test':
                this.loadCameraTestContent();
                break;
            case 'admin':
                this.loadAdminContent();
                break;
        }
        
        this.setActiveTile(section);
    }

    minimizeNavigation() {
        const sideMenu = document.querySelector('.side-menu');
        const mainContent = document.getElementById('mainContent');
        const menuTiles = document.getElementById('menuTiles');
        
        if (sideMenu && mainContent) {
            if (menuTiles) {
                menuTiles.classList.remove('center-view');
            }
            sideMenu.classList.add('expanded');
            mainContent.classList.add('expanded');
            console.log('Navigation minimized');
        }
    }

    resetToCenterView() {
        const sideMenu = document.getElementById('sideMenu');
        const menuTiles = document.getElementById('menuTiles');
        const mainContent = document.getElementById('mainContent');
        
        if (sideMenu) {
            sideMenu.classList.remove('expanded');
        }
        if (menuTiles) {
            menuTiles.classList.add('center-view');
        }
        if (mainContent) {
            mainContent.classList.remove('expanded');
            // Don't clear the content - let the template content show
        }
        
        document.querySelectorAll('.menu-tile').forEach(tile => {
            tile.classList.remove('active');
        });
    }

    setActiveTile(section) {
        document.querySelectorAll('.menu-tile').forEach(tile => {
            tile.classList.remove('active');
        });
        
        const activeTile = document.querySelector(`[data-section="${section}"]`);
        if (activeTile) {
            activeTile.classList.add('active');
        }
    }

    loadPageSpecificContent() {
        if (this.currentPath === '/feedback') {
            this.loadFeedbackContent();
        } else if (this.currentPath === '/camera-test') {
            this.loadCameraTestContent();
        }
    }

    async loadTrailStories() {
        try {
            const response = await fetch('/api/stories');
            const stories = await response.json();
            
            const mainContent = document.getElementById('mainContent');
            mainContent.innerHTML = `
                <div class="content-card">
                    <div class="content-header">
                        <div class="content-icon">
                            <i class="fas fa-hiking"></i>
                        </div>
                        <div>
                            <h1 class="content-title">Dreamtime Bush Trail</h1>
                            <p class="content-subtitle">Explore the stories of the Goondoi Wetlands</p>
                        </div>
                    </div>
                    <div class="stories-grid">
                        ${stories.map(story => `
                            <div class="story-card" onclick="window.location.href='/story/${story.id}'">
                                <div class="story-image">
                                    ${story.image_path ? 
                                        `<img src="/static/${story.image_path}" alt="${story.title}" class="story-image-img" style="object-position: ${story.image_position || 'center'}">` :
                                        `<i class="fas fa-image"></i>`
                                    }
                                </div>
                                <div class="story-info">
                                    <h3 class="story-title">${story.title}</h3>
                                    <p class="story-description">${story.description || 'No description available'}</p>
                                    <div class="story-meta">
                                        <span class="segment-count">${story.segments_count} segments</span>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Error loading stories:', error);
            document.getElementById('mainContent').innerHTML = `
                <div class="content-card">
                    <div class="content-header">
                        <h1 class="content-title">Error Loading Stories</h1>
                    </div>
                    <p>Unable to load stories. Please try again later.</p>
                </div>
            `;
        }
    }

    loadCultureContent() {
        document.getElementById('mainContent').innerHTML = `
            <div class="content-card">
                <div class="content-header">
                    <div class="content-icon">
                        <i class="fas fa-mask"></i>
                    </div>
                    <div>
                        <h1 class="content-title">Culture</h1>
                        <p class="content-subtitle">Discover the rich cultural heritage</p>
                    </div>
                </div>
                <p>Explore the cultural stories and traditions of the Goondoi Wetlands area.</p>
            </div>
        `;
    }

    loadCollegeContent() {
        document.getElementById('mainContent').innerHTML = `
            <div class="content-card">
                <div class="content-header">
                    <div class="content-icon">
                        <i class="fas fa-graduation-cap"></i>
                    </div>
                    <div>
                        <h1 class="content-title">Radiant Life College</h1>
                        <p class="content-subtitle">Educational partnerships and programs</p>
                    </div>
                </div>
                <p>Discover how Radiant Life College partners with the community to provide educational experiences in the Goondoi Wetlands.</p>
            </div>
        `;
    }

    loadFeedbackContent() {
        // Get CSRF token from the page
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
                         document.querySelector('input[name="csrf_token"]')?.value || '';
        
        document.getElementById('mainContent').innerHTML = `
            <div class="content-card">
                <div class="content-header">
                    <div class="content-icon">
                        <i class="fas fa-comment-dots"></i>
                    </div>
                    <div>
                        <h1 class="content-title">Feedback</h1>
                        <p class="content-subtitle">Share your experience with us</p>
                    </div>
                </div>
                <form action="/feedback" method="POST">
                    <input type="hidden" name="csrf_token" value="${csrfToken}"/>
                    <div class="mb-3">
                        <label for="name" class="form-label">Name</label>
                        <input type="text" class="form-control" id="name" name="name" required>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" class="form-control" id="email" name="email" required>
                    </div>
                    <div class="mb-3">
                        <label for="comments" class="form-label">Comments</label>
                        <textarea class="form-control" id="comments" name="comments" rows="4" required></textarea>
                    </div>
                    <button type="submit" class="btn-app">
                        <i class="fas fa-paper-plane me-2"></i>Submit Feedback
                    </button>
                </form>
            </div>
        `;
    }

    loadCameraTestContent() {
        document.getElementById('mainContent').innerHTML = `
            <div class="content-card">
                <div class="content-header">
                    <div class="content-icon">
                        <i class="fas fa-camera"></i>
                    </div>
                    <div>
                        <h1 class="content-title">Camera Test</h1>
                        <p class="content-subtitle">Test scanning functionality</p>
                    </div>
                </div>
                <div class="text-center">
                    <button class="btn-app" onclick="window.appManager.testCamera()">
                        <i class="fas fa-camera me-2"></i>Start Camera Test
                    </button>
                </div>
            </div>
        `;
    }

    loadAdminContent() {
        window.location.href = '/admin/';
    }

    testCamera() {
        console.log('Camera test button clicked');
        
        if (!window.qrScanner) {
            alert('Camera functionality not available. Please refresh the page.');
            return;
        }
        
        try {
            window.qrScanner.startCamera();
        } catch (error) {
            console.error('Error starting camera:', error);
            alert('Error starting camera: ' + error.message);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.appManager = new AppManager();
});

// Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/service-worker.js')
            .then(registration => console.log('Service Worker registered:', registration))
            .catch(error => console.log('Service Worker registration failed:', error));
    });
}
