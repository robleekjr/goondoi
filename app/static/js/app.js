/**
 * Goondoi Wetlands - Main Application JavaScript
 * Simplified for direct page navigation
 */

class AppManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupFlashMessages();
    }

    setupFlashMessages() {
        // Auto-dismiss flash messages after 5 seconds
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(message => {
            setTimeout(() => {
                message.style.opacity = '0';
                setTimeout(() => message.remove(), 300);
            }, 5000);
        });
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new AppManager();
});
