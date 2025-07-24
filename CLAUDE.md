# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive Python video compression application that utilizes FFmpeg and advanced compression techniques. The project provides a full-featured video compressor with multiple codec support (H.264, H.265/HEVC, VP9), various quality presets, and both CLI and interactive interfaces.

### Key Features

- **Multiple Codec Support**: H.264, H.265/HEVC, and VP9 compression
- **Quality Presets**: From ultra_low to lossless compression options
- **Interactive CLI**: User-friendly interface for non-technical users
- **Batch Processing**: Compress multiple videos from a folder
- **Progress Tracking**: Real-time progress display during compression
- **Signal Handling**: Proper cleanup and cancellation support
- **Auto Compression**: Intelligent codec selection based on file characteristics

## Environment Setup

- **Virtual Environment**: The project uses a Python virtual environment located in `venv/`
- **Python Version**: Python 3.13 (based on venv structure)
- **FFmpeg Dependency**: Requires FFmpeg to be installed on the system
- **Activation**: 
  - Windows: `venv\Scripts\activate.bat` or `venv\Scripts\Activate.ps1`
  - Unix/Linux: `source venv/bin/activate`

### Required Dependencies

The project uses the following Python packages:
- `ffmpeg-python` - Python wrapper for FFmpeg
- `opencv-python` - Computer vision library (cv2)
- `tqdm` - Progress bars for batch operations
- Standard library modules: `os`, `sys`, `pathlib`, `subprocess`, `threading`, `time`, `re`, `signal`, `atexit`

## Development Commands

- **Run interactive mode**: `python video.py`
- **Run CLI mode**: `python video.py <input> <output> [quality]`
- **Install dependencies**: `pip install ffmpeg-python opencv-python tqdm`
- **Generate requirements**: `pip freeze > requirements.txt`
- **Test FFmpeg**: Verify FFmpeg is installed and accessible

## Architecture

### Core Components

- `video.py` - Main entry point and complete application
- `VideoCompressor` class - Core compression functionality with the following methods:
  - `compress_h264()` - H.264/AVC compression with advanced settings
  - `compress_h265()` - H.265/HEVC compression for maximum efficiency
  - `compress_vp9()` - VP9 compression optimized for web
  - `compress_auto()` - Intelligent codec selection
  - `batch_compress()` - Process multiple files
  - `get_video_info()` - Extract video metadata

### Quality Presets

- **ultra_low**: CRF 35, fast preset, 50% scale - Maximum compression
- **low**: CRF 28, medium preset, 70% scale - High compression
- **medium**: CRF 23, medium preset, 100% scale - Balanced (default)
- **high**: CRF 18, slow preset, 100% scale - High quality
- **lossless**: CRF 0, veryslow preset, 100% scale - No quality loss

### Usage Patterns

1. **Interactive Mode**: Run without arguments for guided experience
2. **CLI Mode**: `python video.py input.mp4 output.mp4 medium`
3. **Batch Processing**: Use `batch_compress()` method for folder operations

## Coding Standards and Conventions

### Code Style
- **Language**: Python with Portuguese comments and user interface
- **Docstrings**: Portuguese documentation for all classes and methods
- **Error Handling**: Comprehensive try-catch blocks with user-friendly messages
- **Progress Feedback**: Visual progress indicators using emojis and progress bars
- **Signal Handling**: Proper cleanup on interruption (Ctrl+C)

### File Handling
- Use `pathlib.Path` for path operations
- Validate file existence before processing
- Generate output filenames automatically when not specified
- Support common video formats: `.mp4`, `.avi`, `.mov`, `.mkv`, `.wmv`, `.flv`, `.webm`

### FFmpeg Integration
- Use `ffmpeg-python` wrapper for stream building
- Validate FFmpeg availability at startup
- Apply codec-specific optimizations:
  - H.264: Profile high, level 4.1, faststart for streaming
  - H.265: HVC1 tag for compatibility
  - VP9: Deadline good, CPU-used 2 for balanced speed/quality

## Testing and Quality Assurance

- **Manual Testing**: Test with various video formats and quality settings
- **Error Scenarios**: Test with missing files, invalid formats, interrupted operations
- **Performance**: Monitor compression ratios and processing times
- **Cross-platform**: Ensure Windows/Linux compatibility

## Portuguese Interface

The application interface is entirely in Portuguese:
- Error messages use ❌ emoji prefix
- Success messages use ✅ emoji prefix
- Progress indicators use 🔄 and related emojis
- Interactive prompts are in Portuguese
- Quality descriptions are translated

## Deployment Notes

- Ensure FFmpeg is installed and in PATH
- Virtual environment should be activated before running
- Consider creating batch scripts for common operations
- Document FFmpeg installation instructions for end users