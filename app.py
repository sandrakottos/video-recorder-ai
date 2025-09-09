"""
Video Recorder with AI Transcription

A Flask web application that records videos and automatically transcribes them
using Deepgram's Nova-3 AI model with multilingual support.
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
from deepgram import DeepgramClient, PrerecordedOptions
import ffmpeg

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.update({
    'UPLOAD_FOLDER': 'uploads',
    'MAX_CONTENT_LENGTH': 100 * 1024 * 1024,  # 100MB max file size
    'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-key-change-in-production')
})

# Get Deepgram API key
DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
if not DEEPGRAM_API_KEY or DEEPGRAM_API_KEY == 'your_api_key_here':
    logger.warning("DEEPGRAM_API_KEY not set or using placeholder value")

# Allowed file extensions
ALLOWED_EXTENSIONS = {'webm', 'mp4', 'avi', 'mov', 'mkv'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(base_name: str = "journal") -> Dict[str, str]:
    """Generate unique filenames with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_filename = f"{base_name}_{timestamp}"
    return {
        'base': base_filename,
        'video': f"{base_filename}.webm",
        'transcript': f"{base_filename}.txt"
    }


def extract_audio_from_video(video_path: str, audio_path: str) -> bool:
    """Extract and preprocess audio from video file using ffmpeg with noise reduction and normalization."""
    try:
        # First try with full processing including loudnorm
        (
            ffmpeg
            .input(video_path)
            .filter('highpass', f=80)  # High-pass filter to remove low-frequency noise
            .filter('loudnorm', I=-16, TP=-1.5, LRA=11, measured_I=-16, measured_TP=-1.5, measured_LRA=11)  # Audio normalization with measured values
            .output(
                audio_path,
                acodec='pcm_s16le',
                ac=1,
                ar='44100'  # Higher quality sample rate
            )
            .run(overwrite_output=True, quiet=True)
        )
        return True
    except ffmpeg.Error as e:
        logger.warning(f"FFmpeg error with loudnorm, trying without normalization: {e}")
        try:
            # Fallback to extraction with highpass filter only
            (
                ffmpeg
                .input(video_path)
                .filter('highpass', f=80)  # High-pass filter to remove low-frequency noise
                .output(
                    audio_path,
                    acodec='pcm_s16le',
                    ac=1,
                    ar='44100'
                )
                .run(overwrite_output=True, quiet=True)
            )
            return True
        except ffmpeg.Error as e2:
            logger.warning(f"FFmpeg error with highpass filter, trying basic extraction: {e2}")
            try:
                # Final fallback to basic audio extraction without any filters
                (
                    ffmpeg
                    .input(video_path)
                    .output(
                        audio_path,
                        acodec='pcm_s16le',
                        ac=1,
                        ar='44100'
                    )
                    .run(overwrite_output=True, quiet=True)
                )
                return True
            except ffmpeg.Error as e3:
                logger.error(f"FFmpeg error during basic audio extraction: {e3}")
                return False
    except Exception as e:
        logger.error(f"Unexpected error during audio extraction: {e}")
        return False


def transcribe_audio(audio_path: str) -> Optional[Dict[str, Any]]:
    """Transcribe audio using Deepgram API."""
    if not DEEPGRAM_API_KEY or DEEPGRAM_API_KEY == 'your_api_key_here':
        logger.error("Deepgram API key not configured")
        return None
    
    try:
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        
        with open(audio_path, 'rb') as audio_file:
            source = {'buffer': audio_file, 'mimetype': 'audio/wav'}
            options = PrerecordedOptions(
                model="nova-3",
                smart_format=True,
                punctuate=True,
                diarize=True,
                language="multi"
            )
            
            response = deepgram.listen.rest.v("1").transcribe_file(source, options)
            return response
            
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return None


def create_formatted_transcript(response: Any, transcript: str) -> str:
    """Create a formatted transcript with timestamps and speaker information."""
    formatted = f"TRANSCRIPT:\n{transcript}\n\n"
    
    # Add sentence-level timestamps if available
    try:
        if hasattr(response.results, 'utterances') and response.results.utterances:
            formatted += "TIMESTAMPS:\n"
            for utterance in response.results.utterances:
                speaker = getattr(utterance, 'speaker', 'Speaker')
                start_time = getattr(utterance, 'start', 0)
                end_time = getattr(utterance, 'end', 0)
                utterance_text = getattr(utterance, 'transcript', '')
                formatted += f"[{start_time:.2f}s - {end_time:.2f}s] {speaker}: {utterance_text}\n"
    except AttributeError as e:
        logger.warning(f"Could not extract timestamps: {e}")
    
    return formatted


@app.route('/')
def index():
    """Render the main application page."""
    return render_template('index.html')


@app.route('/videos')
def videos():
    """Render the past videos page."""
    try:
        # Get all video files with corresponding transcript files
        video_files = []
        uploads_dir = app.config['UPLOAD_FOLDER']
        
        if os.path.exists(uploads_dir):
            for filename in os.listdir(uploads_dir):
                if filename.endswith('.webm'):
                    # Check if corresponding transcript exists
                    base_name = filename.rsplit('.', 1)[0]
                    transcript_file = f"{base_name}.txt"
                    transcript_path = os.path.join(uploads_dir, transcript_file)
                    
                    if os.path.exists(transcript_path):
                        # Get file creation time
                        file_path = os.path.join(uploads_dir, filename)
                        creation_time = os.path.getctime(file_path)
                        
                        video_files.append({
                            'filename': filename,
                            'transcript_filename': transcript_file,
                            'base_name': base_name,
                            'creation_time': creation_time
                        })
        
        # Sort by creation time (newest first)
        video_files.sort(key=lambda x: x['creation_time'], reverse=True)
        
        return render_template('videos.html', videos=video_files)
        
    except Exception as e:
        logger.error(f"Error loading videos page: {e}")
        return render_template('videos.html', videos=[])


@app.route('/video/<base_name>')
def video_detail(base_name: str):
    """Render the video detail page with player and transcript."""
    try:
        # Security: Prevent directory traversal
        if '..' in base_name or '/' in base_name or '\\' in base_name:
            logger.warning(f"Suspicious base_name requested: {base_name}")
            return jsonify({'error': 'Invalid video name'}), 400
        
        uploads_dir = app.config['UPLOAD_FOLDER']
        video_file = f"{base_name}.webm"
        transcript_file = f"{base_name}.txt"
        
        video_path = os.path.join(uploads_dir, video_file)
        transcript_path = os.path.join(uploads_dir, transcript_file)
        
        # Check if both files exist
        if not os.path.exists(video_path) or not os.path.exists(transcript_path):
            logger.warning(f"Video or transcript not found: {base_name}")
            return jsonify({'error': 'Video not found'}), 404
        
        # Read transcript content
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript_content = f.read()
            # Remove duplicated heading if present for display purposes
            try:
                lines = transcript_content.splitlines()
                if lines and lines[0].strip().upper() == 'TRANSCRIPT:':
                    lines = lines[1:]
                    transcript_content = "\n".join(lines).lstrip()
            except Exception:
                # If anything goes wrong, fall back to original content
                pass
        except Exception as e:
            logger.error(f"Error reading transcript: {e}")
            transcript_content = "Transcript unavailable"
        
        # Get file creation time
        creation_time = os.path.getctime(video_path)
        
        return render_template('video_detail.html', 
                             base_name=base_name,
                             video_file=video_file,
                             transcript_file=transcript_file,
                             transcript_content=transcript_content,
                             creation_time=creation_time)
        
    except Exception as e:
        logger.error(f"Error loading video detail: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/upload', methods=['POST'])
def upload():
    """Handle video upload and transcription."""
    try:
        # Validate file upload
        if 'video' not in request.files:
            logger.warning("No video file in request")
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        if video_file.filename == '':
            logger.warning("Empty filename in request")
            return jsonify({'error': 'No selected file'}), 400

        # Generate unique filenames
        filenames = generate_unique_filename()
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filenames['video'])
        transcript_path = os.path.join(app.config['UPLOAD_FOLDER'], filenames['transcript'])
        temp_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_audio_{filenames['base']}.wav")
        
        # Save video file
        try:
            video_file.save(video_path)
            logger.info(f"Video saved: {filenames['video']}")
        except Exception as e:
            logger.error(f"Failed to save video file: {e}")
            return jsonify({'error': 'Failed to save video file'}), 500

        # Extract audio from video
        if not extract_audio_from_video(video_path, temp_audio_path):
            return jsonify({'error': 'Failed to extract audio from video'}), 500

        # Transcribe audio
        response = transcribe_audio(temp_audio_path)
        if response is None:
            return jsonify({'error': 'Transcription service unavailable'}), 503

        try:
            # Get transcript text
            transcript = response.results.channels[0].alternatives[0].transcript
            if not transcript.strip():
                logger.warning("Empty transcript received")
                transcript = "No speech detected in the recording."
            
            # Create formatted transcript
            formatted_transcript = create_formatted_transcript(response, transcript)
            
            # Save transcript
            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(formatted_transcript)
            
            logger.info(f"Transcript saved: {filenames['transcript']}")
            
        except (AttributeError, IndexError, KeyError) as e:
            logger.error(f"Error processing transcription response: {e}")
            return jsonify({'error': 'Failed to process transcription'}), 500
        
        except Exception as e:
            logger.error(f"Unexpected error during transcript processing: {e}")
            return jsonify({'error': 'Transcription processing failed'}), 500

        return jsonify({
            'success': True,
            'message': 'File uploaded and transcribed successfully',
            'video_filename': filenames['video'],
            'transcript_filename': filenames['transcript'],
            'base_filename': filenames['base']
        })

    except Exception as e:
        logger.error(f"Unexpected error in upload route: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    
    finally:
        # Clean up temporary audio file
        if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
                logger.debug("Temporary audio file cleaned up")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary audio file: {e}")


@app.route('/download/<filename>')
def download_file(filename: str):
    """Serve files for download with security checks."""
    try:
        # Security: Prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            logger.warning(f"Suspicious filename requested: {filename}")
            return jsonify({'error': 'Invalid filename'}), 400
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Check if file exists and is within upload folder
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {filename}")
            return jsonify({'error': 'File not found'}), 404
        
        # Verify the file is actually in the uploads directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
            logger.warning(f"Attempted access outside upload folder: {filename}")
            return jsonify({'error': 'Access denied'}), 403
        
        logger.info(f"Serving file: {filename}")
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Download error for {filename}: {e}")
        return jsonify({'error': 'Download failed'}), 500


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum size is 100MB.'}), 413


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Get configuration from environment
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5001'))
    
    logger.info(f"Starting application on {host}:{port} (debug={debug_mode})")
    app.run(host=host, port=port, debug=debug_mode)
