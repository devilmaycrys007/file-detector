[中文](./README.md) | English

# File Detector

A Windows desktop tool for detecting new or modified files of specified types within a folder, with built-in copy management.

## Features

- Select a source folder and filter by file extensions
- Use a reference file's modification time as the baseline to detect newer files
- Display matched results in a table with delete, select-all, and deselect-all support
- One-click copy of table files to a target folder
- Auto-save configuration for quick restore on next launch

## Usage

| Step | Description |
|------|-------------|
| 1 | **Source Folder** - Select the folder to scan |
| 2 | **File Types** - Enter extensions separated by commas, e.g. `.docx,.doc,.zip,.xls` |
| 3 | **Reference File** - Choose a file as the time baseline; detect files modified after it |
| 4 | **Target Folder** - Choose the destination folder for copied files |
| 5 | Click **Start Detection** to scan for matching files |
| 6 | Review/delete files in the table, then click **Copy to Target Folder** |

## Build

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "FileDetector" file_detector.py
```

The generated exe is located in the `dist/` folder.

## Configuration

The program automatically creates `file_detector_config.json` next to the exe to persist the last-used folder paths and reference file.
