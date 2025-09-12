/**
 * QR Code Scanner Module
 * Handles QR code scanning functionality for the Goondoi Wetlands app
 */

class QRScanner {
    constructor() {
        this.video = null;
        this.canvas = null;
        this.stream = null;
        this.scanning = false;
        this.isFullscreen = false;
        this.init();
    }

    init() {
        console.log('QRScanner initialized');
    }

    setupCameraModal() {
        if (document.getElementById('cameraModal')) {
            return; // Modal already exists
        }

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
                    <button class="camera-button" onclick="window.qrScanner.retryCamera()">Retry Camera</button>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        this.video = document.getElementById('qr-video');
        this.canvas = document.createElement('canvas');
        this.canvas.width = 640;
        this.canvas.height = 480;
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        const closeCameraBtn = document.getElementById('closeCamera');
        if (closeCameraBtn) {
            closeCameraBtn.addEventListener('click', () => this.closeCamera());
        }
        
        const cameraModal = document.getElementById('cameraModal');
        if (cameraModal) {
            cameraModal.addEventListener('click', (e) => {
                if (e.target.id === 'cameraModal') {
                    this.closeCamera();
                }
            });
        }
    }

    async startCamera() {
        try {
            if (!document.getElementById('cameraModal')) {
                this.setupCameraModal();
            }
            
            document.getElementById('cameraError').style.display = 'none';
            
            // Check HTTPS requirement
            if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
                this.showError('Camera access requires HTTPS. Please use https:// or localhost.');
                return;
            }
            
            // Check browser support
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                this.showError('Camera access is not supported in this browser.');
                return;
            }
            
            // Load jsQR library
            try {
                await this.loadJSQR();
            } catch (error) {
                console.error('Failed to load jsQR library:', error);
                this.showError('Failed to load QR scanning library.');
                return;
            }
            
            const constraints = {
                video: {
                    facingMode: 'environment',
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            };
            
            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.stream;
            
            this.video.addEventListener('loadedmetadata', () => {
                this.video.play();
                this.startScanning();
            });
            
            document.getElementById('cameraModal').style.display = 'flex';
            
        } catch (error) {
            console.error('Error accessing camera:', error);
            this.handleCameraError(error);
        }
    }

    async loadJSQR() {
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

    startScanning() {
        this.scanning = true;
        this.scanQRCode();
    }

    scanQRCode() {
        if (!this.scanning || !this.video || this.video.readyState !== this.video.HAVE_ENOUGH_DATA) {
            requestAnimationFrame(() => this.scanQRCode());
            return;
        }
        
        const context = this.canvas.getContext('2d');
        this.canvas.height = this.video.videoHeight;
        this.canvas.width = this.video.videoWidth;
        context.drawImage(this.video, 0, 0, this.canvas.width, this.canvas.height);
        
        const imageData = context.getImageData(0, 0, this.canvas.width, this.canvas.height);
        const code = window.jsQR(imageData.data, imageData.width, imageData.height);
        
        if (code) {
            console.log('QR Code detected:', code.data);
            this.onQRCodeScanned(code.data);
        } else {
            requestAnimationFrame(() => this.scanQRCode());
        }
    }

    onQRCodeScanned(qrData) {
        this.scanning = false;
        this.closeCamera();
        
        // Extract segment ID from QR data
        const segmentIdMatch = qrData.match(/\/story\/segment\/([a-f0-9-]+)/);
        if (segmentIdMatch) {
            const segmentId = segmentIdMatch[1];
            console.log('Extracted segment ID:', segmentId);
            
            // Navigate to the segment
            const segmentUrl = `/story/segment/${segmentId}`;
            console.log('Navigating to:', segmentUrl);
            window.location.href = segmentUrl;
        } else {
            console.log('QR code data does not contain a valid segment URL:', qrData);
            alert('Invalid QR code. Please scan a valid segment QR code.');
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
        
        const errorDiv = document.getElementById('cameraError');
        if (errorDiv) {
            errorDiv.style.display = 'block';
        }
        
        const cameraModal = document.getElementById('cameraModal');
        if (cameraModal) {
            cameraModal.style.display = 'flex';
        }
        
        this.showError(errorMessage);
    }

    showError(message) {
        console.error('Camera Error:', message);
        // Could implement a toast notification system here
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
        
        this.scanning = false;
        
        const cameraModal = document.getElementById('cameraModal');
        if (cameraModal) {
            cameraModal.style.display = 'none';
        }
        
        const errorDiv = document.getElementById('cameraError');
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }
}

// Initialize QR Scanner when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.qrScanner = new QRScanner();
});

// Global test function for development
window.testQRCode = function(qrData) {
    console.log('Testing QR code processing with:', qrData);
    if (window.qrScanner) {
        window.qrScanner.onQRCodeScanned(qrData);
    }
};
