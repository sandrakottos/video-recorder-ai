/**
 * Video Recorder with AI Transcription
 * 
 * A modern web application for recording videos and generating
 * AI-powered transcriptions with speaker identification and timestamps.
 */

class VideoRecorder {
    constructor() {
        this.preview = document.getElementById('preview');
        this.recordButton = document.getElementById('recordButton');
        this.statusDiv = document.getElementById('status');
        this.recordingLinkDiv = document.getElementById('recording-link');
        
        this.mediaRecorder = null;
        this.recordedChunks = [];
        this.stream = null;
        this.isRecording = false;
        
        this.config = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                frameRate: { ideal: 30 }
            },
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            }
        };
        
        this.init();
    }
    
    async init() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: this.config.video,
                audio: this.config.audio
            });
            
            this.preview.srcObject = this.stream;
            this.setupEventListeners();
            this.updateStatus('Ready to record');
            
        } catch (error) {
            this.handleError(`Camera access error: ${error.message}. Please allow camera and microphone access.`);
        }
    }
    
    setupEventListeners() {
        this.recordButton.addEventListener('click', () => this.toggleRecording());
    }
    
    updateStatus(message, isError = false) {
        this.statusDiv.textContent = message;
        this.statusDiv.className = `status-text ${isError ? 'error' : ''}`;
    }
    
    handleError(message) {
        console.error(message);
        this.updateStatus(message, true);
        if (this.isRecording) {
            this.stopRecording();
        }
    }
    
    toggleRecording() {
        if (this.isRecording) {
            this.stopRecording();
        } else {
            this.startRecording();
        }
    }
    
    startRecording() {
        if (!this.stream) {
            this.handleError("Camera stream not available.");
            return;
        }

        try {
            this.recordedChunks = [];
            const mimeType = this.getSupportedMimeType();
            
            this.mediaRecorder = new MediaRecorder(this.stream, { mimeType });
            
            this.mediaRecorder.ondataavailable = event => {
                if (event.data.size > 0) {
                    this.recordedChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                const blob = new Blob(this.recordedChunks, { type: mimeType });
                this.uploadVideo(blob);
            };
            
            this.mediaRecorder.onerror = event => {
                this.handleError(`Recording error: ${event.error.message}`);
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            this.updateButtonState();
            this.updateStatus('Recording...');
            
        } catch (error) {
            this.handleError(`Failed to start recording: ${error.message}`);
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.updateButtonState();
            this.updateStatus('Processing...');
        }
    }

    getSupportedMimeType() {
        const mimeTypes = [
            'video/webm; codecs=vp9,opus',
            'video/webm; codecs=vp8,opus',
            'video/webm',
            'video/mp4'
        ];
        for (const mimeType of mimeTypes) {
            if (MediaRecorder.isTypeSupported(mimeType)) {
                return mimeType;
            }
        }
        throw new Error('No supported video format found for recording.');
    }
    
    updateButtonState() {
        const icon = this.recordButton.querySelector('.button-icon svg');
        const text = this.recordButton.querySelector('.button-text');
        
        if (this.isRecording) {
            this.recordButton.classList.add('recording');
            icon.innerHTML = `<rect x="6" y="6" width="12" height="12" fill="currentColor"/>`;
            text.textContent = 'Stop Sharing';
        } else {
            this.recordButton.classList.remove('recording');
            icon.innerHTML = `
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <circle cx="12" cy="12" r="3" fill="currentColor"/>
            `;
            text.textContent = 'Share Your Thoughts';
        }
    }
    
    async uploadVideo(blob) {
        const formData = new FormData();
        const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
        formData.append('video', blob, `recording_${timestamp}.webm`);
        
        this.updateStatus('Uploading and transcribing...');
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 300000); // 5-minute timeout

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || `Server error: ${response.status}`);
            }
            
            if (result.success) {
                this.updateStatus('Transcription complete! Your thought has been saved.');
                this.displayActionLinks(result);
            } else {
                throw new Error(result.error || 'Upload failed due to an unknown server issue.');
            }
            
        } catch (error) {
            if (error.name === 'AbortError') {
                this.handleError('Upload timed out. Please try again with a shorter recording.');
            } else {
                this.handleError(`Upload failed: ${error.message}`);
            }
        }
    }
    
    displayActionLinks(result) {
        this.recordingLinkDiv.innerHTML = `
            <a href="/video/${result.base_filename}" class="nav-link">View Your Thought</a>
        `;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    try {
        new VideoRecorder();
    } catch (error) {
        console.error('Failed to initialize VideoRecorder:', error);
        const statusDiv = document.getElementById('status');
        if (statusDiv) {
            statusDiv.textContent = 'Failed to initialize the application. Please ensure you are using a modern browser and have granted camera permissions.';
            statusDiv.className = 'status-text error';
        }
    }
});
