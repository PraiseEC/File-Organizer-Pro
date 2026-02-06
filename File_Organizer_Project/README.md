# File Organizer — Modern Desktop Application

A comprehensive file organization tool with advanced features, built as a student project demonstrating modern Python GUI development.

## Features

- **File Organization**: Automatically sort files into categorized folders based on file extensions
- **Search Functionality**: Find files by name within selected folders with real-time results
- **Statistics & Visualization**: View detailed folder statistics and interactive pie charts of file type distribution
- **Advanced Tools**:
  - Batch rename files with custom patterns (e.g., file_001, file_002)
  - Find and delete duplicate files based on content hash
  - Identify large files above configurable size thresholds
- **Undo Support**: Full undo functionality for organization operations
- **Modern UI**: Clean, responsive interface with sidebar navigation and status bar
- **Theme Support**: Multiple color themes (Blue, Green, Dark-Blue) - no light/dark toggle
- **Comprehensive Logging**: Detailed operation logs with built-in viewer
- **Configuration Persistence**: Saves settings, themes, and recent folders
- **Progress Tracking**: Real-time progress bars for long operations

## Requirements

- Python 3.13+
- Dependencies: customtkinter, matplotlib, pandas, numpy, watchdog, tkinter (bundled)

## Installation

1. Create and activate virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Fix Tcl/Tk issue (one-time setup):
   ```powershell
   setx TCL_LIBRARY "C:\Users\SURFACE\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"
   # Restart terminal after setx
   ```

## Usage

### Basic Operation
1. **Organize Files**:
   - Select folder using "Browse" button
   - Click "Start Organizing" to sort files
   - Monitor progress and use "Undo Last" if needed

2. **Search Files**:
   - Navigate to Search tab
   - Enter query and view results instantly

3. **View Statistics**:
   - Stats tab shows folder info
   - "Show Chart" displays file type distribution

4. **Advanced Tools**:
   - **Batch Rename**: Use patterns like "photo_###" for sequential naming
   - **Delete Duplicates**: Removes identical files safely
   - **Find Large Files**: Set MB threshold to identify space hogs

5. **Settings & Logs**:
   - Change themes and view/clear application logs

## File Categories

Organizes into: Images, Videos, Documents, Music, Archives, Executables, Code, Spreadsheets, Presentations, Others

## Technical Implementation

- **OOP Design**: Class-based architecture with proper separation
- **Error Handling**: Comprehensive try/catch with user feedback
- **Data Visualization**: Matplotlib integration for charts
- **File Operations**: Safe move operations with rollback capability
- **Configuration**: JSON-based settings persistence
- **Logging**: Structured logging for debugging and monitoring

## Project Structure

```
main.py (604+ lines) - Main application
requirements.txt - Dependencies
config.json - User settings
README.md - Documentation
file_organizer.log - Application logs
```

## Run

```powershell
.\.venv\Scripts\python.exe main.py
```

## Git Setup

```powershell
git init
git add .
git commit -m "Complete file organizer with advanced features"
```

## Design Philosophy

- Modern, accessible UI without unnecessary toggles
- Feature-rich yet intuitive for academic demonstration
- Robust error handling and user feedback
- Extensible architecture for future enhancements

This project exceeds 500 lines and demonstrates professional Python development practices suitable for academic submission and portfolio showcase.
