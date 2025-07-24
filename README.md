# 🎬 Video Compressor Pro

[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://python.org)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-required-red.svg)](https://ffmpeg.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> A comprehensive Python video compression tool featuring multiple codecs, intelligent quality presets, and both interactive and command-line interfaces.

## 🚀 Features

### Core Capabilities
- **Multiple Codec Support**: H.264/AVC, H.265/HEVC, and VP9 compression
- **Smart Quality Presets**: From ultra-high compression to lossless quality
- **Dual Interface**: Interactive mode for beginners, CLI for power users
- **Batch Processing**: Compress entire folders with a single command
- **Real-time Progress**: Visual progress tracking with detailed statistics
- **Intelligent Auto-mode**: Automatic codec selection based on file characteristics
- **Signal Handling**: Graceful cancellation and cleanup (Ctrl+C support)

### Advanced Features
- **Adaptive Scaling**: Automatic resolution adjustment for optimal compression
- **Metadata Preservation**: Maintains video information and streaming optimization
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Memory Efficient**: Optimized for large file processing
- **Error Recovery**: Robust error handling with informative messages

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher (developed with 3.13)
- **FFmpeg**: Must be installed and accessible via PATH
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Memory**: Minimum 4GB RAM (8GB+ recommended for 4K videos)
- **Storage**: Sufficient space for input and output files

### Python Dependencies
```txt
ffmpeg-python==0.2.0
opencv-python==4.8.1.78
tqdm==4.66.1
pathlib2==2.3.7
```

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/video-compressor-pro.git
cd video-compressor-pro
```

### 2. Install FFmpeg

#### Windows
Download from [FFmpeg official site](https://ffmpeg.org/download.html) or use package manager:
```powershell
# Using Chocolatey
choco install ffmpeg

# Using Scoop
scoop install ffmpeg
```

#### macOS
```bash
# Using Homebrew
brew install ffmpeg
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

### 3. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
python video.py --help
```

## 🎯 Usage

### Interactive Mode (Recommended for Beginners)
Simply run the script without arguments for a guided experience:
```bash
python video.py
```

The interactive mode will guide you through:
1. **File Selection**: Browse and select your input video
2. **Quality Settings**: Choose from 5 preset quality levels
3. **Output Configuration**: Automatic output naming or custom paths
4. **Compression Preview**: Review settings before processing

### Command Line Interface
For advanced users and automation:
```bash
python video.py <input_file> <output_file> [quality]
```

#### Examples
```bash
# Basic compression with default quality
python video.py input.mp4 output.mp4

# High-quality compression
python video.py movie.avi movie_compressed.mp4 high

# Maximum compression for sharing
python video.py large_video.mov small_video.mp4 ultra_low

# Lossless compression
python video.py source.mkv archive.mp4 lossless
```

### Batch Processing
Process multiple videos programmatically:
```python
from video import VideoCompressor

compressor = VideoCompressor()
compressor.batch_compress(
    input_folder="./input_videos/",
    output_folder="./compressed/",
    quality="medium"
)
```

## ⚙️ Quality Presets

| Preset | CRF | Preset Speed | Scale | Use Case | File Size |
|--------|-----|--------------|-------|----------|-----------|
| `ultra_low` | 35 | Fast | 50% | Maximum compression, sharing | ~90% smaller |
| `low` | 28 | Medium | 70% | High compression, mobile | ~70% smaller |
| `medium` | 23 | Medium | 100% | **Balanced (default)** | ~50% smaller |
| `high` | 18 | Slow | 100% | High quality, archival | ~30% smaller |
| `lossless` | 0 | Very Slow | 100% | No quality loss | Varies |

### Quality Selection Guide
- **Ultra Low**: Social media sharing, bandwidth-limited scenarios
- **Low**: Mobile devices, email attachments
- **Medium**: General purpose, balanced quality/size ratio
- **High**: Professional use, minimal quality loss acceptable
- **Lossless**: Archival, post-production, no quality compromise

## 🔧 Advanced Configuration

### Custom Codec Settings
```python
from video import VideoCompressor

compressor = VideoCompressor()

# Custom H.264 settings
compressor.compress_h264(
    input_path="input.mp4",
    output_path="output.mp4",
    custom_crf=20,           # Custom quality
    custom_preset="slower",   # Custom speed preset
    scale_factor=0.8         # Custom scaling
)

# H.265 for maximum efficiency
compressor.compress_h265(
    input_path="input.mp4",
    output_path="output.mp4",
    quality="high"
)

# VP9 for web delivery
compressor.compress_vp9(
    input_path="input.mp4",
    output_path="output.webm",
    quality="medium"
)
```

### Supported Input Formats
- **Video**: MP4, AVI, MOV, MKV, WMV, FLV, WEBM, M4V, 3GP
- **Codecs**: H.264, H.265, VP8, VP9, MPEG-4, and more
- **Audio**: AAC, MP3, AC3, DTS (automatically transcoded to AAC)

### Output Specifications
- **Container**: MP4 (H.264/H.265) or WEBM (VP9)
- **Video**: Maintains aspect ratio, optimized encoding settings
- **Audio**: AAC 128kbps, stereo (preserves original channels when possible)
- **Metadata**: Preserved and optimized for streaming

## 📊 Performance Benchmarks

### Typical Compression Results
| Original Size | Quality | Final Size | Reduction | Processing Time* |
|---------------|---------|------------|-----------|------------------|
| 1GB (1080p) | Ultra Low | ~100MB | 90% | 3-5 min |
| 1GB (1080p) | Medium | ~500MB | 50% | 8-12 min |
| 1GB (1080p) | High | ~700MB | 30% | 15-20 min |

*Processing times vary based on hardware and video complexity

### Hardware Recommendations
- **CPU**: Multi-core processor (Intel i5/AMD Ryzen 5 or better)
- **RAM**: 8GB+ for 4K content, 4GB for 1080p
- **Storage**: SSD recommended for faster I/O operations

## 🐛 Troubleshooting

### Common Issues

#### FFmpeg Not Found
```
⚠️ FFmpeg não encontrado. Instale o FFmpeg para usar todas as funcionalidades.
```
**Solution**: Install FFmpeg and ensure it's in your system PATH.

#### Permission Errors
**Solution**: Run with appropriate permissions or check file/folder access rights.

#### Memory Issues with Large Files
**Solution**: 
- Close other applications
- Use lower quality presets
- Process files in smaller batches

#### Slow Processing
**Solution**:
- Use faster presets (`fast`, `medium` instead of `slow`)
- Lower the CRF value
- Reduce scale factor

### Getting Help
1. Check the [FAQ section](#faq)
2. Review error messages for specific guidance
3. Verify FFmpeg installation: `ffmpeg -version`
4. Test with a small sample file first

## 🔍 FAQ

**Q: Which codec should I choose?**
A: H.264 for compatibility, H.265 for maximum compression, VP9 for web delivery.

**Q: How much space will I save?**
A: Typically 30-70% depending on quality settings and source material.

**Q: Can I process 4K videos?**
A: Yes, but ensure you have sufficient RAM (8GB+) and processing time.

**Q: Is batch processing supported?**
A: Yes, use the `batch_compress()` method for folder processing.

**Q: Can I cancel a running compression?**
A: Yes, press Ctrl+C to safely cancel and cleanup.

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
git clone https://github.com/yourusername/video-compressor-pro.git
cd video-compressor-pro
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Code Style
- Follow PEP 8 guidelines
- Use Portuguese for user-facing messages
- Include docstrings for all functions
- Add emoji prefixes for user feedback (✅ ❌ 🔄)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FFmpeg Team** - For the powerful multimedia framework
- **Python Community** - For excellent libraries and tools
- **Contributors** - Thank you for your improvements and feedback

## 📈 Project Status

- ✅ **Stable Release**: Core functionality complete and tested
- 🔄 **Active Development**: Regular updates and improvements
- 📋 **Planned Features**: GPU acceleration, additional codecs, GUI interface

---

<div align="center">

**Made with ❤️ by [Your Name]**

[⬆ Back to Top](#-video-compressor-pro)

</div>