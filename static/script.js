/**
 * Video Recorder with AI Transcription
 * 
 * A modern web application for recording videos and generating
 * AI-powered transcriptions with speaker identification and timestamps.
 */

class VideoRecorder {
    constructor() {
        // DOM elements
        this.preview = document.getElementById('preview');
        this.recordButton = document.getElementById('recordButton');
        this.statusDiv = document.getElementById('status');
        this.recordingLinkDiv = document.getElementById('recording-link');
        
        // Recording state
        this.mediaRecorder = null;
        this.recordedChunks = [];
        this.stream = null;
        this.isRecording = false;
        
        // Configuration
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
    
    /**
     * Initialize the video recorder
     */
    async init() {
        try {
            // Request media access with enhanced configuration
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: this.config.video,
                audio: this.config.audio
            });
            
            this.preview.srcObject = this.stream;
            this.setupEventListeners();
            this.updateStatus('Ready to record');
            
        } catch (error) {
            this.handleError(`Camera access error: ${error.message}`);
        }
    }
    
    /**
     * Set up event listeners
     */
    setupEventListeners() {
        this.recordButton.addEventListener('click', () => this.toggleRecording());
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.isRecording) {
                this.updateStatus('Recording paused (tab hidden)');
            } else if (!document.hidden && this.isRecording) {
                this.updateStatus('Recording...');
            }
        });
    }
    
    /**
     * Update status message
     */
    updateStatus(message, isError = false) {
        this.statusDiv.textContent = message;
        this.statusDiv.className = `status-text ${isError ? 'error' : ''}`;
    }
    
    /**
     * Handle errors with consistent logging
     */
    handleError(message) {
        console.error(message);
        this.updateStatus(message, true);
    }
    
    /**
     * Toggle recording state
     */
    toggleRecording() {
        if (!this.isRecording) {
            this.startRecording();
        } else {
            this.stopRecording();
        }
    }
    
    /**
     * Start video recording
     */
    startRecording() {
        try {
            this.recordedChunks = [];
            
            // Check for supported MIME types
            const mimeTypes = [
                'video/webm; codecs=vp9',
                'video/webm; codecs=vp8',
                'video/webm',
                'video/mp4'
            ];
            
            let selectedMimeType = null;
            for (const mimeType of mimeTypes) {
                if (MediaRecorder.isTypeSupported(mimeType)) {
                    selectedMimeType = mimeType;
                    break;
                }
            }
            
            if (!selectedMimeType) {
                throw new Error('No supported video format found');
            }
            
            this.mediaRecorder = new MediaRecorder(this.stream, {
                mimeType: selectedMimeType
            });
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.recordedChunks.push(event.data);
                }
            };
            
            this.mediaRecorder.onstop = () => {
                const blob = new Blob(this.recordedChunks, { type: selectedMimeType });
                this.processRecording(blob);
            };
            
            this.mediaRecorder.onerror = (event) => {
                this.handleError(`Recording error: ${event.error}`);
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            this.updateButtonState();
            this.updateStatus('Recording...');
            
        } catch (error) {
            this.handleError(`Failed to start recording: ${error.message}`);
        }
    }
    
    /**
     * Stop video recording
     */
    stopRecording() {
        try {
            if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
                this.mediaRecorder.stop();
                this.isRecording = false;
                this.updateButtonState();
                this.updateStatus('Processing...');
            }
        } catch (error) {
            this.handleError(`Failed to stop recording: ${error.message}`);
        }
    }
    
    /**
     * Process the recorded video
     */
    processRecording(blob) {
        this.createDownloadLink(blob);
        this.uploadVideo(blob);
    }
    
    /**
     * Update button state and appearance
     */
    updateButtonState() {
        const button = this.recordButton;
        const icon = button.querySelector('.button-icon svg');
        const text = button.querySelector('.button-text');
        
        if (this.isRecording) {
            button.classList.add('recording');
            button.disabled = false;
            
            // Change icon to stop (square)
            icon.innerHTML = `
                <rect x="6" y="6" width="12" height="12" fill="currentColor"/>
            `;
            text.textContent = 'Stop Recording';
        } else {
            button.classList.remove('recording');
            button.disabled = false;
            
            // Change icon back to record (circle)
            icon.innerHTML = `
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <circle cx="12" cy="12" r="3" fill="currentColor"/>
            `;
            text.textContent = 'Start Recording';
        }
    }
    
    /**
     * Create download link for the recorded video
     */
    createDownloadLink(blob) {
        try {
            const url = URL.createObjectURL(blob);
            const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
            const filename = `recording_${timestamp}.webm`;
            
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            link.textContent = 'Download Recording';
            link.className = 'download-link';
            
            this.recordingLinkDiv.innerHTML = '';
            this.recordingLinkDiv.appendChild(link);
            
            // Clean up URL after some time to prevent memory leaks
            setTimeout(() => {
                URL.revokeObjectURL(url);
            }, 60000);
            
        } catch (error) {
            this.handleError(`Failed to create download link: ${error.message}`);
        }
    }
    
    /**
     * Upload video to server for transcription
     */
    async uploadVideo(blob) {
        try {
            const formData = new FormData();
            const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
            const filename = `recording_${timestamp}.webm`;
            formData.append('video', blob, filename);
            
            this.updateStatus('Uploading and transcribing...');
            
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minute timeout
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (response.ok) {
                const result = await response.json();
                
                if (result.success) {
                    this.updateStatus('Transcription complete! Files saved successfully.');
                    this.displayDownloadLinks(result);
                } else {
                    throw new Error(result.error || 'Upload failed');
                }
            } else {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }
            
        } catch (error) {
            if (error.name === 'AbortError') {
                this.handleError('Upload timeout. Please try again with a shorter recording.');
            } else {
                this.handleError(`Upload failed: ${error.message}`);
            }
        }
    }
    
    /**
     * Display download links for video and transcript
     */
    displayDownloadLinks(result) {
        const linksContainer = document.createElement('div');
        linksContainer.className = 'download-links-container';
        linksContainer.style.marginTop = '20px';
        
        const videoLink = document.createElement('a');
        videoLink.href = `/download/${result.video_filename}`;
        videoLink.download = result.video_filename;
        videoLink.textContent = 'Download Video';
        videoLink.className = 'download-link';
        
        const transcriptLink = document.createElement('a');
        transcriptLink.href = `/download/${result.transcript_filename}`;
        transcriptLink.download = result.transcript_filename;
        transcriptLink.textContent = 'Download Transcript';
        transcriptLink.className = 'download-link';
        
        linksContainer.appendChild(videoLink);
        linksContainer.appendChild(document.createTextNode(' | '));
        linksContainer.appendChild(transcriptLink);
        
        this.recordingLinkDiv.innerHTML = '';
        this.recordingLinkDiv.appendChild(linksContainer);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        new VideoRecorder();
    } catch (error) {
        console.error('Failed to initialize VideoRecorder:', error);
        document.getElementById('status').textContent = 
            'Failed to initialize application. Please refresh the page.';
    }
});
