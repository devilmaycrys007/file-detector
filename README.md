# 文件检测与复制工具 · File Detector

一个 Windows 桌面工具，用于检测文件夹中指定类型的新增/修改文件，并提供复制管理功能。

A Windows desktop tool for detecting new or modified files of specified types within a folder, with built-in copy management.

---

## 功能 · Features

- 选择需要检测的文件夹，按文件类型筛选
- 以参照文件的修改时间为基准，检测修改时间晚于它的文件
- 匹配结果展示在表格中，支持删除、全选等操作
- 一键将表格中的文件复制到目标文件夹
- 自动保存配置，下次打开直接恢复

---

- Select a source folder and filter by file extensions
- Use a reference file's modification time as the baseline to detect newer files
- Display matched results in a table with delete, select-all, and deselect-all support
- One-click copy of table files to a target folder
- Auto-save configuration for quick restore on next launch

---

## 使用方法 · Usage

| Step | Chinese | English |
|------|---------|---------|
| 1 | **检测文件夹** - 选择需要扫描的源文件夹 | **Source Folder** - Select the folder to scan |
| 2 | **文件类型** - 输入后缀名，逗号分隔，如 `.docx,.doc,.zip,.xls` | **File Types** - Enter extensions separated by commas, e.g. `.docx,.doc,.zip,.xls` |
| 3 | **参照文件** - 选择一个文件作为时间基准，检测修改时间晚于它的文件 | **Reference File** - Choose a file as the time baseline; detect files modified after it |
| 4 | **目标文件夹** - 选择文件复制目标路径 | **Target Folder** - Choose the destination folder for copied files |
| 5 | 点击 **开始检测文件** 扫描匹配的文件 | Click **Start Detection** to scan for matching files |
| 6 | 在表格中确认/删除文件后，点击 **复制到目标文件夹** | Review/delete files in the table, then click **Copy to Target Folder** |

---

## 打包 · Build

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "FileDetector" file_detector.py
```

生成的 exe 在 `dist/` 目录下。 · The generated exe is located in the `dist/` folder.

---

## 配置 · Configuration

程序会在 exe 同级目录自动生成 `file_detector_config.json`，保存上次的文件夹路径和参照文件信息。

The program automatically creates `file_detector_config.json` next to the exe to persist the last-used folder paths and reference file.
