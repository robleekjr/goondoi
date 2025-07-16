// QR Code Scanner and Full Screen Story Management
class QRStoryManager {
    constructor() {
        this.video = null;
        this.canvas = null;
        this.stream = null;
        this.scanning = false;
        this.currentStoryId = null;
        this.currentSegmentId = null;
        this.isFullscreen = false;
        
        this.init();
    }
    
    init() {
        this.setupCameraModal();
        this.setupEventListeners();
    }
    
    setupCameraModal() {
        // Create camera modal HTML
        const modalHTML = `
            <div class="camera-modal" id="cameraModal">
                <div class="camera-container">
                    <video id="qr-video" autoplay playsinline></video>
                    <div class="camera-overlay"></div>
                </div>
                <div class="camera-controls">
                    <button class="camera-button" id="closeCamera">Close Camera</button>
                </div>
                <div id="cameraError" style="display: none; text-align: center; color: white; margin-top: 1rem;">
                    <p>Camera access denied. Please try the following:</p>
                    <ul style="text-align: left; max-width: 400px; margin: 0 auto;">
                        <li>Allow camera permissions in your browser</li>
                        <li>Use HTTPS (required for camera access)</li>
                        <li>Try a different browser (Chrome/Safari recommended)</li>
                        <li>Check if camera is being used by another app</li>
                    </ul>
                    <button class="camera-button" onclick="window.qrStoryManager.retryCamera()">Retry Camera</button>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        this.video = document.getElementById('qr-video');
        this.canvas = document.createElement('canvas');
        this.canvas.width = 640;
        this.canvas.height = 480;
    }
    
    setupEventListeners() {
        // Camera controls
        document.getElementById('closeCamera').addEventListener('click', () => {
            this.closeCamera();
        });
        
        // Close modal on background click
        document.getElementById('cameraModal').addEventListener('click', (e) => {
            if (e.target.id === 'cameraModal') {
                this.closeCamera();
            }
        });
        
        // Handle successful QR code scans
        this.onQRCodeScanned = this.onQRCodeScanned.bind(this);
        
        // Handle fullscreen change events
        document.addEventListener('fullscreenchange', () => {
            this.isFullscreen = !!document.fullscreenElement;
        });
        
        document.addEventListener('webkitfullscreenchange', () => {
            this.isFullscreen = !!document.webkitFullscreenElement;
        });
        
        document.addEventListener('mozfullscreenchange', () => {
            this.isFullscreen = !!document.mozFullScreenElement;
        });
        
        document.addEventListener('MSFullscreenChange', () => {
            this.isFullscreen = !!document.msFullscreenElement;
        });
        
        // Handle keyboard events
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isFullscreen) {
                this.exitBrowserFullscreen();
            }
        });
    }
    
    async startCamera() {
        try {
            // Show loading state
            document.getElementById('cameraError').style.display = 'none';
            
            // Check if we're on HTTPS (required for camera access)
            if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
                this.showError('Camera access requires HTTPS. Please use https:// or localhost.');
                return;
            }
            
            // Check if getUserMedia is supported
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                this.showError('Camera access is not supported in this browser.');
                return;
            }
            
            // Load jsQR library before starting camera
            try {
                await loadJSQR();
                console.log('jsQR library loaded successfully');
            } catch (error) {
                console.error('Failed to load jsQR library:', error);
                this.showError('Failed to load QR scanning library. Please refresh the page and try again.');
                return;
            }
            
            const constraints = {
                video: {
                    facingMode: 'environment', // Use back camera on mobile
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            };
            
            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.stream;
            this.video.play();
            
            // Start scanning after video loads
            this.video.addEventListener('loadedmetadata', () => {
                console.log('Video loaded, starting QR scanning...');
                this.startScanning();
            });
            
            document.getElementById('cameraModal').style.display = 'flex';

            // Show the Hide Browser UI button and attach click handler
            const hideBtn = document.getElementById('hideBrowserUIButton');
            if (hideBtn) {
                hideBtn.style.display = 'inline-block';
                hideBtn.onclick = () => this.enterBrowserFullscreen();
            }
        } catch (error) {
            console.error('Error accessing camera:', error);
            this.handleCameraError(error);
        }
    }
    
    handleCameraError(error) {
        let errorMessage = 'Camera access denied. ';
        
        if (error.name === 'NotAllowedError') {
            errorMessage += 'Please allow camera permissions in your browser settings.';
        } else if (error.name === 'NotFoundError') {
            errorMessage += 'No camera found on this device.';
        } else if (error.name === 'NotSupportedError') {
            errorMessage += 'Camera access is not supported in this browser.';
        } else if (error.name === 'NotReadableError') {
            errorMessage += 'Camera is already in use by another application.';
        } else {
            errorMessage += 'Please check your camera permissions and try again.';
        }
        
        // Show detailed error in modal
        const errorDiv = document.getElementById('cameraError');
        errorDiv.style.display = 'block';
        
        // Still show the modal so user can see the error
        document.getElementById('cameraModal').style.display = 'flex';
        
        this.showError(errorMessage);
    }
    
    retryCamera() {
        this.closeCamera();
        setTimeout(() => {
            this.startCamera();
        }, 500);
    }
    
    closeCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        if (this.scanning) {
            this.stopScanning();
        }
        
        document.getElementById('cameraModal').style.display = 'none';
        document.getElementById('cameraError').style.display = 'none';
    }
    
    startScanning() {
        this.scanning = true;
        this.scanQRCode();
    }
    
    stopScanning() {
        this.scanning = false;
    }
    
    async scanQRCode() {
        if (!this.scanning) return;
        
        try {
            const context = this.canvas.getContext('2d');
            context.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
            
            const imageData = context.getImageData(0, 0, this.canvas.width, this.canvas.height);
            
            // Check if jsQR is available
            if (typeof jsQR === 'undefined') {
                console.error('jsQR library not loaded');
                this.stopScanning();
                this.showError('QR scanning library not loaded. Please refresh and try again.');
                return;
            }
            
            console.log('Scanning frame...', new Date().toLocaleTimeString());
            const code = jsQR(imageData.data, imageData.width, imageData.height);
            
            if (code) {
                console.log('QR Code detected:', code.data);
                console.log('QR Code format:', code.format);
                console.log('QR Code version:', code.version);
                this.onQRCodeScanned(code.data);
                return;
            }
            
            // Continue scanning
            requestAnimationFrame(() => this.scanQRCode());
            
        } catch (error) {
            console.error('Error scanning QR code:', error);
            // Continue scanning even if there's an error
            requestAnimationFrame(() => this.scanQRCode());
        }
    }
    
    async onQRCodeScanned(qrData) {
        try {
            console.log('Processing QR code data:', qrData);
            
            // Handle different URL formats
            let segmentId = null;
            
            if (qrData.startsWith('http')) {
                // Full URL format
                const url = new URL(qrData);
                const pathParts = url.pathname.split('/');
                segmentId = pathParts[pathParts.length - 1];
            } else if (qrData.includes('/story/segment/')) {
                // Partial URL format
                const parts = qrData.split('/story/segment/');
                segmentId = parts[1];
            } else {
                // Direct segment ID
                segmentId = qrData;
            }
            
            if (segmentId) {
                console.log('Extracted segment ID:', segmentId);
                
                // Close camera
                this.closeCamera();
                
                // Navigate to the segment
                const segmentUrl = `/story/segment/${segmentId}`;
                console.log('Navigating to:', segmentUrl);
                window.location.href = segmentUrl;
            } else {
                console.error('Could not extract segment ID from QR code data:', qrData);
                this.showError('Invalid QR code format. Please try scanning a different QR code.');
            }
            
        } catch (error) {
            console.error('Error processing QR code:', error);
            this.showError('Invalid QR code. Please try again.');
        }
    }
    
    showError(message) {
        // Create error notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 59, 48, 0.9);
            color: white;
            padding: 1rem 2rem;
            border-radius: 10px;
            z-index: 3000;
            backdrop-filter: blur(10px);
            max-width: 90%;
            text-align: center;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    // Full screen story management
    enterFullscreenStory(storyId, segmentId) {
        this.currentStoryId = storyId;
        this.currentSegmentId = segmentId;
        
        // Hide main content
        const mainContent = document.querySelector('main');
        if (mainContent) {
            mainContent.style.display = 'none';
        }
        
        // Show fullscreen story
        const fullscreenStory = document.getElementById('fullscreenStory');
        if (fullscreenStory) {
            fullscreenStory.style.display = 'block';
        }
    }
    
    exitFullscreenStory() {
        // Exit browser fullscreen if active
        if (this.isFullscreen) {
            this.exitBrowserFullscreen();
        }
        
        // Show main content
        const mainContent = document.querySelector('main');
        if (mainContent) {
            mainContent.style.display = 'block';
        }
        
        // Hide fullscreen story
        const fullscreenStory = document.getElementById('fullscreenStory');
        if (fullscreenStory) {
            fullscreenStory.style.display = 'none';
        }
        
        // Navigate back to stories list
        window.location.href = '/';
    }
    
    // Browser fullscreen API methods
    enterBrowserFullscreen() {
        const fullscreenStory = document.getElementById('fullscreenStory');
        if (!fullscreenStory) return;
        
        try {
            // Try multiple times with different methods
            const requestFullscreen = fullscreenStory.requestFullscreen ||
                                    fullscreenStory.webkitRequestFullscreen ||
                                    fullscreenStory.mozRequestFullScreen ||
                                    fullscreenStory.msRequestFullscreen;
            
            if (requestFullscreen) {
                requestFullscreen.call(fullscreenStory);
            }
        } catch (error) {
            console.error('Error entering fullscreen:', error);
            // Fallback: try again after a short delay
            setTimeout(() => {
                try {
                    const requestFullscreen = fullscreenStory.requestFullscreen ||
                                            fullscreenStory.webkitRequestFullscreen ||
                                            fullscreenStory.mozRequestFullScreen ||
                                            fullscreenStory.msRequestFullscreen;
                    
                    if (requestFullscreen) {
                        requestFullscreen.call(fullscreenStory);
                    }
                } catch (retryError) {
                    console.error('Retry failed:', retryError);
                }
            }, 200);
        }
    }
    
    exitBrowserFullscreen() {
        try {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
        } catch (error) {
            console.error('Error exiting fullscreen:', error);
        }
    }
    
    updateProgress(currentSegment, totalSegments) {
        const progressFill = document.querySelector('.progress-fill');
        if (progressFill) {
            const percentage = (currentSegment / totalSegments) * 100;
            progressFill.style.width = `${percentage}%`;
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.qrStoryManager = new QRStoryManager();
    
    // Setup scan buttons
    const scanButtons = document.querySelectorAll('.scan-button');
    scanButtons.forEach(button => {
        button.addEventListener('click', () => {
            console.log('Scan button clicked');
            window.qrStoryManager.startCamera();
        });
    });
    
    // Setup exit buttons
    const exitButtons = document.querySelectorAll('.exit-button');
    exitButtons.forEach(button => {
        button.addEventListener('click', () => {
            window.qrStoryManager.exitFullscreenStory();
        });
    });
    
    // Add global test function
    window.testQRCode = function(qrData) {
        console.log('Testing QR code processing with:', qrData);
        if (window.qrStoryManager) {
            window.qrStoryManager.onQRCodeScanned(qrData);
        }
    };
});

// Load jsQR library dynamically
function loadJSQR() {
    return new Promise((resolve, reject) => {
        if (window.jsQR) {
            resolve(window.jsQR);
            return;
        }
        
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js';
        script.onload = () => resolve(window.jsQR);
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

// Initialize QR scanning when needed
async function initQRScanning() {
    try {
        await loadJSQR();
        console.log('QR scanning ready');
    } catch (error) {
        console.error('Failed to load QR scanning library:', error);
    }
}

// Call this when camera is opened
document.addEventListener('camera-opened', initQRScanning); 