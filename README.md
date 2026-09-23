# 📖 Ayah Marker Detector & Validator

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

An interactive, high-precision desktop workstation built with **Python**, **OpenCV**, and **Tkinter** for detecting, visually validating, and cataloging Ayah marker coordinates across custom Indo-Pak, Emdadia, and standard Mushaf scripts.

The generated coordinates serve as the foundational dataset for compilation into text-spanning highlight bounding boxes (`ayahinfo.db`) used in mobile Quran applications (such as [AyahMarker](https://github.com/abunayem/AyahMarker)).

---

## ✨ Features

### 🖥️ Modern Centered Workspace
- **Centered Canvas Layout**: The Quran page is dynamically centered in the viewing area on any display or widescreen resolution, eliminating awkward side voids.
- **High-Contrast Marker Badging**: Markers are rendered with a dual-ring contrast system (crisp outer white halo + inner red indicator + center dot) with an Ayah index badge visible on both dark borders and paper textures.
- **Smooth Zoom & Pan**: Support for `Ctrl + MouseWheel` zooming, `Shift + MouseWheel` horizontal scrubbing, and standard vertical scrolling with `Zoom +`, `Zoom -`, and `Fit` presets.

### 🎯 Multi-Algorithm Detection Engine
- **Hough Circles (Default)**: Classical radial gradient detection specifically tuned for Quranic marker medallions with text line boundary filtering.
- **Template Matching**: Normalized Cross-Correlation (`cv2.matchTemplate`) with Non-Maximum Suppression (NMS) for Mushafs with stylized floral medallions.
- **Combined Mode**: Runs Hough Circle detection and supplements it with template matching.
- **✂ On-Page Template Cropping**: Click `✂ Crop from Page` and select any Ayah marker on the page. The application immediately extracts a 50×50 patch, saves it as `template_custom.png`, loads it into memory, and switches detection to Template Matching.
- **Dynamic Sensitivity Slider**:
  - In *Hough Circles* mode: Adjusts circle detection strictness (`param2: 18 - 35`, default `25`).
  - In *Template Matching* mode: Adjusts correlation threshold (`0.40 - 0.85`, default `0.65`).
- **Auto-Detect Toggle**: Can be enabled or disabled per page to prevent false positives on title or ornamental pages.

### 🚀 Advanced Jump & Navigation Suite
- **Jump by Sura & Ayah**: Full dropdown of all 114 Surahs (with transliteration, Arabic names, and ayah counts) + Ayah spinbox. Automatically queries the database or uses standard 15-line Mushaf page mappings to locate the page.
- **Jump to Unmarked Pages**:
  - `Next Unmarked ▶` (`Ctrl+N`): Instantly advances to the next page in the Quran that has zero markers recorded in the database.
  - `◀ Prev Unmarked` (`Ctrl+P`): Jumps backward to any skipped unvalidated pages.
- **Page Scrubber**: Continuous slider and direct page jump with `|<< First`, `◀ Prev`, `Next ▶`, and `Last ⏭` buttons.
- **Sequence Tracker & Override**: Displays the active Sura and Ayah assignment and provides a manual override panel (`Assign Next As: Sura [X] Ayah [Y] [Set Sequence]`).
- **Page DB Status Badge**: Color-coded pill badge indicating `✔ SAVED (N markers)` (Green) or `● UNSAVED` (Amber).

### 🛡️ Safe Exit Confirmation
- Intercepts window closing (`X`, `Alt+F4`, `Ctrl+Q`, and `File -> Exit`) with a confirmation dialog to prevent accidental loss of unsaved marker annotations.

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/abunayem/Ayah-Marker-Detector.git
cd Ayah-Marker-Detector
```

### 2. Set Up Virtual Environment
```powershell
python -m venv env
.\env\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🚀 Usage

### Graphical Launch
You can launch without any flags and select your directories, template, and database directly through the GUI:
```powershell
.\env\Scripts\python.exe ayah_validator_ui.py
```

### Command Line Launch (Custom Flags)
```powershell
.\env\Scripts\python.exe ayah_validator_ui.py `
  --img_dir "D:\Dev\Temp\EmdadiaPages" `
  --out_db "D:\Dev\Temp\ayahinfo_emdadia_perfect.db" `
  --start_page 1 `
  --start_sura 1 `
  --start_ayah 1
```

#### Available CLI Arguments:
| Argument | Description | Default |
| :--- | :--- | :--- |
| `--img_dir` | Directory containing page images (`.png`, `.jpg`, etc.) | `D:\Dev\Temp\EmdadiaPages` |
| `--out_db` | SQLite database path to store `raw_markers` | `ayahinfo.db` |
| `--template` | Optional marker template image | None |
| `--start_page` | Starting page number | `1` |
| `--end_page` | Ending page number | `611` |
| `--start_sura` | Starting Sura number for marker sequencing | `1` |
| `--start_ayah` | Starting Ayah number for marker sequencing | `1` |

---

## ⌨️ Keyboard Shortcuts Reference

| Shortcut | Action |
| :--- | :--- |
| **Enter** | Save markers on current page and advance to next page |
| **Ctrl + S** | Save markers on current page without advancing |
| **Ctrl + Z** | Undo last marker addition / deletion |
| **Left Arrow** | Navigate to previous page |
| **Right Arrow** | Navigate to next page |
| **Ctrl + N** | Jump to Next Unmarked page |
| **Ctrl + P** | Jump to Previous Unmarked page |
| **F5** | Re-run marker detection on current page |
| **Ctrl + O** | Browse Quran Pages Folder |
| **Ctrl + T** | Browse Marker Template Image |
| **Ctrl + D** | Browse SQLite Database |
| **Ctrl + Q** | Exit with confirmation prompt |
| **Ctrl + MouseWheel** | Zoom in / Zoom out |
| **Shift + MouseWheel** | Horizontal canvas pan |

---

## 🔄 End-to-End Pipeline: From Markers to Android App

1. **Annotation**: Use `ayah_validator_ui.py` to verify or plot marker centers on every page.
2. **Storage**: Marker coordinates are saved in the `raw_markers` table:
   ```sql
   CREATE TABLE raw_markers (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       page_number INTEGER,
       sura_number INTEGER,
       ayah_number INTEGER,
       cx INTEGER,
       cy INTEGER
   );
   ```
3. **Compilation**: Run `compile_ayahinfo.py` to project marker center dots into full line-spanning bounding boxes (`ayah_highlights` and `page_lines`):
   ```powershell
   python compile_ayahinfo.py
   ```
4. **Deployment**: Copy the resulting `ayahinfo.db` directly into the Android application assets directory:
   `app/src/main/assets/ayahinfo.db`

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
