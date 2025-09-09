# 🎥 Video Recorder with AI Transcription

[![CI](https://github.com/your-username/video-recorder-ai/workflows/CI/badge.svg)](https://github.com/your-username/video-recorder-ai/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, secure web application that records videos directly in your browser and automatically transcribes them using Deepgram's Nova-3 AI model with multilingual support and speaker identification.

![Demo Screenshot](https://via.placeholder.com/800x400/f8b5c1/2c2c2c?text=Video+Recorder+with+AI+Transcription)

## ✨ Features

- 🎥 **Browser-based Recording**: Record high-quality videos directly in your browser
- 🤖 **AI-Powered Transcription**: Powered by Deepgram's Nova-3 model for accurate transcription
- 🌍 **Multilingual Support**: Supports 10+ languages with automatic detection
- ⏱️ **Precise Timestamps**: Sentence-level timestamps for easy navigation
- 👥 **Speaker Identification**: Automatically identifies and labels different speakers
- ✨ **Smart Formatting**: Automatic punctuation, capitalization, and formatting
- 📱 **Responsive Design**: Optimized for desktop and mobile devices
- 🔒 **Secure**: Built with security best practices and input validation
- 🎨 **Modern UI**: Beautiful, accessible interface with smooth animations

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Deepgram API Key** - [Get your free key](https://deepgram.com)
- **FFmpeg** - [Installation guide](https://ffmpeg.org/download.html)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/video-recorder-ai.git
   cd video-recorder-ai
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your configuration:
   ```env
   DEEPGRAM_API_KEY=your_deepgram_api_key_here
   FLASK_DEBUG=False
   FLASK_HOST=0.0.0.0
   FLASK_PORT=5001
   SECRET_KEY=your_secret_key_here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   Navigate to `http://localhost:5001`

### Alternative Setup

For a streamlined setup, use the provided setup script:
```bash
python setup.py
```

## How to Use

1. **Allow camera access** when prompted by your browser
2. **Click "Start Recording"** to begin recording
3. **Speak in any supported language** - the app will automatically detect and transcribe
4. **Click "Stop Recording"** when finished
5. **Wait for transcription** - the app will process and save both video and transcript
6. **Download your recording** using the provided link
7. **Find your transcript** in the `uploads/` folder

## 📁 Project Structure

```
video-recorder-ai/
├── 🐍 Backend
│   ├── app.py                    # Main Flask application
│   ├── requirements.txt          # Python dependencies
│   └── setup.py                  # Setup automation script
├── 🎨 Frontend
│   ├── templates/
│   │   └── index.html           # Main application page
│   └── static/
│       ├── style.css            # Modern CSS styling
│       └── script.js            # Enhanced JavaScript
├── ⚙️ Configuration
│   ├── .env.example             # Environment template
│   ├── .env                     # Your configuration (create this)
│   └── .gitignore               # Git ignore patterns
├── 📚 Documentation
│   ├── README.md                # This file
│   ├── CONTRIBUTING.md          # Contribution guidelines
│   └── LICENSE                  # MIT license
├── 🤖 CI/CD
│   └── .github/
│       └── workflows/
│           └── ci.yml           # GitHub Actions workflow
└── 📁 Runtime
    └── uploads/                 # Generated videos and transcripts
```

## Output Format

Your transcriptions are saved as `.txt` files with this format:

```
TRANSCRIPT:
Hello, this is a test recording. I'm speaking about various topics today.

TIMESTAMPS:
[0.00s - 2.50s] Speaker 0: Hello, this is a test recording.
[2.50s - 5.20s] Speaker 0: I'm speaking about various topics today.
```

## Supported Languages

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Hindi (hi)
- Russian (ru)
- Portuguese (pt)
- Japanese (ja)
- Italian (it)
- Dutch (nl)

## Troubleshooting

### Common Issues

**"Error accessing camera"**
- Make sure you allow camera/microphone access in your browser
- Try refreshing the page

**"Transcription failed"**
- Check that your Deepgram API key is correct in `.env`
- Ensure you have internet connection
- Verify your Deepgram account has credits

**"Port 5000 is in use"**
- On macOS, disable AirPlay Receiver in System Preferences
- Or change the port in `app.py` (last line)

### Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

## API Reference

### Endpoints

- `GET /` - Main application page
- `POST /upload` - Upload and transcribe video

### Request Format

```javascript
// Upload video
const formData = new FormData();
formData.append('video', videoBlob, 'recording.webm');

fetch('/upload', {
    method: 'POST',
    body: formData
});
```

### Response Format

```json
{
    "message": "File uploaded and transcribed successfully",
    "transcription_path": "uploads/recording.txt"
}
```

## 🔧 Development

### Development Setup

1. **Fork and clone** the repository
2. **Follow installation steps** above
3. **Set environment variables**:
   ```bash
   export FLASK_DEBUG=True
   export FLASK_ENV=development
   ```
4. **Run with hot reload**:
   ```bash
   python app.py
   ```

### Code Quality

We maintain high code standards:

- **Python**: Follow PEP 8, use type hints
- **JavaScript**: Modern ES6+, proper error handling
- **Security**: Input validation, secure defaults
- **Testing**: Comprehensive error handling

### Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Architecture

- **Backend**: Flask with proper error handling and logging
- **Frontend**: Vanilla JavaScript with modern browser APIs
- **Transcription**: Deepgram Nova-3 with multilingual support
- **Storage**: Local file system with secure path handling

## 🚀 Deployment

### Production Deployment

1. **Set production environment**:
   ```env
   FLASK_DEBUG=False
   SECRET_KEY=your-secure-secret-key
   ```

2. **Use a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5001 app:app
   ```

3. **Set up reverse proxy** (nginx recommended)

### Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5001
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "app:app"]
```

## 📈 Performance

- **File Size Limit**: 100MB per upload
- **Supported Formats**: WebM, MP4, AVI, MOV, MKV
- **Transcription Speed**: ~1:4 ratio (1 minute audio = ~15 seconds processing)
- **Languages**: Auto-detection for 10+ languages

## 🛡️ Security Features

- **Input Validation**: All file uploads validated
- **Path Traversal Protection**: Secure file handling
- **Environment Variables**: Sensitive data protected
- **Error Handling**: No sensitive information leaked
- **CORS Protection**: Secure cross-origin requests

## 📊 Browser Support

| Browser | Version | Recording | Transcription |
|---------|---------|-----------|---------------|
| Chrome  | 88+     | ✅        | ✅            |
| Firefox | 85+     | ✅        | ✅            |
| Safari  | 14+     | ✅        | ✅            |
| Edge    | 88+     | ✅        | ✅            |

## 🤝 Support

- **Documentation**: Check this README and [CONTRIBUTING.md](CONTRIBUTING.md)
- **Issues**: [Create an issue](https://github.com/your-username/video-recorder-ai/issues)
- **Deepgram Docs**: [developers.deepgram.com](https://developers.deepgram.com)
- **Community**: [Discussions](https://github.com/your-username/video-recorder-ai/discussions)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Deepgram** for the excellent Nova-3 transcription model
- **Flask** for the lightweight web framework
- **FFmpeg** for robust video processing
- **Contributors** who help improve this project

---

**Made with ❤️ using Flask, Deepgram Nova-3, and modern web technologies**

[![Star this repo](https://img.shields.io/github/stars/your-username/video-recorder-ai?style=social)](https://github.com/your-username/video-recorder-ai)
