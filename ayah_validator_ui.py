import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import sqlite3
import os
import sys
import re
import argparse
from scipy.signal import find_peaks

# 114 Surahs Metadata: (Number, Transliteration, Arabic Name, Hafs Ayah Count)
SURAS = [
    (1, "Al-Fatihah", "الفاتحة", 7),
    (2, "Al-Baqarah", "البقرة", 286),
    (3, "Ali 'Imran", "آل عمران", 200),
    (4, "An-Nisa'", "النساء", 176),
    (5, "Al-Ma'idah", "المائدة", 120),
    (6, "Al-An'am", "الأنعام", 165),
    (7, "Al-A'raf", "الأعراف", 206),
    (8, "Al-Anfal", "الأنفال", 75),
    (9, "At-Tawbah", "التوبة", 129),
    (10, "Yunus", "يونس", 109),
    (11, "Hud", "هود", 123),
    (12, "Yusuf", "يوسف", 111),
    (13, "Ar-Ra'd", "الرعد", 43),
    (14, "Ibrahim", "إبراهيم", 52),
    (15, "Al-Hijr", "الحجر", 99),
    (16, "An-Nahl", "النحل", 128),
    (17, "Al-Isra'", "الإسراء", 111),
    (18, "Al-Kahf", "الكهف", 110),
    (19, "Maryam", "مريم", 98),
    (20, "Ta-Ha", "طه", 135),
    (21, "Al-Anbiya'", "الأنبياء", 112),
    (22, "Al-Hajj", "الحج", 78),
    (23, "Al-Mu'minun", "المؤمنون", 118),
    (24, "An-Nur", "النور", 64),
    (25, "Al-Furqan", "الفرقان", 77),
    (26, "Ash-Shu'ara'", "الشعراء", 227),
    (27, "An-Naml", "النمل", 93),
    (28, "Al-Qasas", "القصص", 88),
    (29, "Al-'Ankabut", "العنكبوت", 69),
    (30, "Ar-Rum", "الروم", 60),
    (31, "Luqman", "لقمان", 34),
    (32, "As-Sajdah", "السجدة", 30),
    (33, "Al-Ahzab", "الأحزاب", 73),
    (34, "Saba'", "سبأ", 54),
    (35, "Fatir", "فاطر", 45),
    (36, "Ya-Sin", "يس", 83),
    (37, "As-Saffat", "الصافات", 182),
    (38, "Sad", "ص", 88),
    (39, "Az-Zumar", "الزمر", 75),
    (40, "Ghafir", "غافر", 85),
    (41, "Fussilat", "فصلت", 54),
    (42, "Ash-Shura", "الشورى", 53),
    (43, "Az-Zukhruf", "الزخرف", 89),
    (44, "Ad-Dukhan", "الدخان", 59),
    (45, "Al-Jathiyah", "الجاثية", 37),
    (46, "Al-Ahqaf", "الأحقاف", 35),
    (47, "Muhammad", "محمد", 38),
    (48, "Al-Fath", "الفتح", 29),
    (49, "Al-Hujurat", "الحجرات", 18),
    (50, "Qaf", "ق", 45),
    (51, "Adh-Dhariyat", "الذاريات", 60),
    (52, "At-Tur", "الطور", 49),
    (53, "An-Najm", "النجم", 62),
    (54, "Al-Qamar", "القمر", 55),
    (55, "Ar-Rahman", "الرحمن", 78),
    (56, "Al-Waqi'ah", "الواقعة", 96),
    (57, "Al-Hadid", "الحديد", 29),
    (58, "Al-Mujadilah", "المجادلة", 22),
    (59, "Al-Hashr", "الحشر", 24),
    (60, "Al-Mumtahanah", "الممتحنة", 13),
    (61, "As-Saff", "الصف", 14),
    (62, "Al-Jumu'ah", "الجمعة", 11),
    (63, "Al-Munafiqun", "المنافقون", 11),
    (64, "At-Taghabun", "التغابن", 18),
    (65, "At-Talaq", "الطلاق", 12),
    (66, "At-Tahrim", "التحريم", 12),
    (67, "Al-Mulk", "الملك", 30),
    (68, "Al-Qalam", "القلم", 52),
    (69, "Al-Haqqah", "الحاقة", 52),
    (70, "Al-Ma'arij", "المعارج", 44),
    (71, "Nuh", "نوح", 28),
    (72, "Al-Jinn", "الجن", 28),
    (73, "Al-Muzzammil", "المزمل", 20),
    (74, "Al-Muddaththir", "المدثر", 56),
    (75, "Al-Qiyamah", "القيامة", 40),
    (76, "Al-Insan", "الإنسان", 31),
    (77, "Al-Mursalat", "المرسلات", 50),
    (78, "An-Naba'", "النبأ", 40),
    (79, "An-Nazi'at", "النازعات", 46),
    (80, "'Abasa", "عبس", 42),
    (81, "At-Takwir", "التكوير", 29),
    (82, "Al-Infitar", "الانفطار", 19),
    (83, "Al-Mutaffifin", "المطففين", 36),
    (84, "Al-Inshiqaq", "الانشقاق", 25),
    (85, "Al-Buruj", "البروج", 22),
    (86, "At-Tariq", "الطارق", 17),
    (87, "Al-A'la", "الأعلى", 19),
    (88, "Al-Ghashiyah", "الغاشية", 26),
    (89, "Al-Fajr", "الفجر", 30),
    (90, "Al-Balad", "البلد", 20),
    (91, "Ash-Shams", "الشمس", 15),
    (92, "Al-Layl", "الليل", 21),
    (93, "Ad-Duha", "الضحى", 11),
    (94, "Ash-Sharh", "الشرح", 8),
    (95, "At-Tin", "التين", 8),
    (96, "Al-'Alaq", "العلق", 19),
    (97, "Al-Qadr", "القدر", 5),
    (98, "Al-Bayyinah", "البينة", 8),
    (99, "Az-Zalzalah", "الزلزلة", 8),
    (100, "Al-'Adiyat", "العاديات", 11),
    (101, "Al-Qari'ah", "القارعة", 11),
    (102, "At-Takathur", "التكاثر", 8),
    (103, "Al-'Asr", "العصر", 3),
    (104, "Al-Humazah", "الهمزة", 9),
    (105, "Al-Fil", "الفيل", 5),
    (106, "Quraysh", "قريش", 4),
    (107, "Al-Ma'un", "الماعون", 7),
    (108, "Al-Kawthar", "الكوثر", 3),
    (109, "Al-Kafirun", "الكافرون", 6),
    (110, "An-Nasr", "النصر", 3),
    (111, "Al-Masad", "المسد", 5),
    (112, "Al-Ikhlas", "الإخلاص", 4),
    (113, "Al-Falaq", "الفلق", 5),
    (114, "An-Nas", "الناس", 6)
]

hafs_ayat = [s[3] for s in SURAS]

# Standard 15-line Mushaf starting pages for all 114 Surahs
SURA_START_PAGES = {
    1: 1, 2: 2, 3: 50, 4: 77, 5: 106, 6: 128, 7: 151, 8: 177, 9: 187,
    10: 208, 11: 221, 12: 235, 13: 249, 14: 255, 15: 261, 16: 267, 17: 282, 18: 293, 19: 305,
    20: 312, 21: 322, 22: 331, 23: 342, 24: 350, 25: 359, 26: 366, 27: 376, 28: 385, 29: 396,
    30: 404, 31: 411, 32: 415, 33: 418, 34: 428, 35: 434, 36: 440, 37: 445, 38: 452, 39: 458,
    40: 467, 41: 477, 42: 483, 43: 489, 44: 495, 45: 498, 46: 502, 47: 506, 48: 511, 49: 515,
    50: 518, 51: 520, 52: 523, 53: 526, 54: 528, 55: 531, 56: 534, 57: 537, 58: 542, 59: 545,
    60: 549, 61: 551, 62: 553, 63: 554, 64: 556, 65: 558, 66: 560, 67: 562, 68: 564, 69: 567,
    70: 569, 71: 571, 72: 573, 73: 576, 74: 578, 75: 580, 76: 582, 77: 584, 78: 586, 79: 587,
    80: 589, 81: 590, 82: 591, 83: 592, 84: 594, 85: 595, 86: 596, 87: 597, 88: 597, 89: 598,
    90: 600, 91: 600, 92: 601, 93: 602, 94: 602, 95: 603, 96: 603, 97: 604, 98: 604, 99: 605,
    100: 605, 101: 606, 102: 606, 103: 607, 104: 607, 105: 607, 106: 608, 107: 608, 108: 608,
    109: 608, 110: 609, 111: 609, 112: 609, 113: 610, 114: 610
}

def natural_keys(text):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', text)]

def find_page_files(img_dir):
    """Scans img_dir and returns dict of page_number -> full_path sorted naturally."""
    page_dict = {}
    if not os.path.exists(img_dir):
        return page_dict
        
    exts = ('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff')
    files = [f for f in os.listdir(img_dir) if f.lower().endswith(exts)]
    files.sort(key=natural_keys)
    
    for f in files:
        full_path = os.path.join(img_dir, f)
        digits = re.findall(r'\d+', f)
        if digits:
            page_num = int(digits[-1])
            page_dict[page_num] = full_path
            
    if not page_dict and files:
        for idx, f in enumerate(files, 1):
            page_dict[idx] = os.path.join(img_dir, f)
            
    return page_dict

def find_text_lines(img_gray):
    """Detect text line bands using horizontal projection peaks."""
    _, thresh = cv2.threshold(img_gray, 200, 255, cv2.THRESH_BINARY_INV)
    row_sums = np.sum(thresh, axis=1) / 255
    peaks, _ = find_peaks(row_sums, distance=120, prominence=50)
    lines = []
    width = img_gray.shape[1]
    for p in peaks:
        miny = max(0, int(p) - 84)
        maxy = min(img_gray.shape[0], int(p) + 84)
        line_band = thresh[miny:maxy, :]
        col_sums = np.sum(line_band, axis=0)
        non_zero_cols = np.nonzero(col_sums)[0]
        if len(non_zero_cols) > 0:
            minx = non_zero_cols[0]
            maxx = non_zero_cols[-1]
        else:
            minx = 0; maxx = width
        lines.append(((minx, miny), (maxx, maxy)))
    return lines

class AyahValidatorApp:
    def __init__(self, root, img_dir, db_path, template_path="",
                 start_page=1, end_page=611, start_sura=1, start_ayah=1):
        self.root = root
        self.root.title("Ayah Marker Detector & Validator (Pro Edition)")
        self.root.state('zoomed')
        
        self.img_dir = img_dir or ""
        self.db_path = db_path or "ayahinfo.db"
        self.template_path = template_path or ""
        self.current_page = start_page
        self.end_page = end_page
        self.sura = start_sura
        self.ayah = start_ayah
        
        self.page_files = {}
        self.total_pages = 611
        
        self.scale = 1.0
        self.base_scale = 1.0
        self.zoom_level = 1.0
        self.offset_x = 0
        self.offset_y = 15
        
        self.circles = [] 
        self.history = [] 
        self.lines = []
        self.full_img = None
        self.template_gray = None
        self.thumb_photo = None
        self.is_cropping_template = False
        
        # Intercept window close for confirmation dialog
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)
        
        self.build_ui()
        self.load_pages_folder(self.img_dir, initial=True)
        if self.template_path and os.path.exists(self.template_path):
            self.load_template(self.template_path)
        self.init_db()
        self.load_page()
        
    def build_ui(self):
        # 1. Top Menu Bar
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Quran Pages Directory... (Ctrl+O)", command=self.browse_pages_dir)
        file_menu.add_command(label="Open/Create Database... (Ctrl+D)", command=self.browse_database)
        file_menu.add_command(label="Open Template Image... (Ctrl+T)", command=self.browse_template)
        file_menu.add_separator()
        file_menu.add_command(label="Save Current Page (Ctrl+S)", command=lambda: self.save_page(advance=False))
        file_menu.add_command(label="Exit", command=self.confirm_exit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        nav_menu = tk.Menu(menubar, tearoff=0)
        nav_menu.add_command(label="Next Page (Enter / Right Arrow)", command=self.next_page)
        nav_menu.add_command(label="Previous Page (Left Arrow)", command=self.prev_page)
        nav_menu.add_command(label="First Page (Home)", command=lambda: self.jump_to_page(1))
        nav_menu.add_command(label="Last Page (End)", command=lambda: self.jump_to_page(self.total_pages))
        nav_menu.add_separator()
        nav_menu.add_command(label="Next Unmarked Page (Ctrl+N)", command=self.jump_next_unmarked)
        nav_menu.add_command(label="Previous Unmarked Page (Ctrl+P)", command=self.jump_prev_unmarked)
        menubar.add_cascade(label="Navigate", menu=nav_menu)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo Last Click (Ctrl+Z)", command=self.undo)
        edit_menu.add_command(label="Re-Detect Markers (F5)", command=self.run_detection)
        edit_menu.add_command(label="Crop Template from Page", command=self.start_crop_template)
        edit_menu.add_command(label="Clear Markers on Page", command=self.clear_markers)
        menubar.add_cascade(label="Markers", menu=edit_menu)
        
        self.root.config(menu=menubar)
        
        # 2. Modern Header Ribbon (Two Card Panels)
        top_container = tk.Frame(self.root, bg="#0f172a", bd=0)
        top_container.pack(fill=tk.X, padx=0, pady=0)
        
        # Panel 1: File & Setup Bar
        card1 = tk.Frame(top_container, bg="#1e293b", bd=1, relief=tk.FLAT)
        card1.pack(fill=tk.X, padx=6, pady=(4, 2))
        
        tk.Label(card1, text="📁 Pages Folder:", font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#1e293b").pack(side=tk.LEFT, padx=(8, 2), pady=4)
        self.pages_entry = tk.Entry(card1, font=("Segoe UI", 9), width=32, bg="#0f172a", fg="#f8fafc", insertbackground="white")
        self.pages_entry.pack(side=tk.LEFT, padx=3, pady=4)
        tk.Button(card1, text="Browse...", font=("Segoe UI", 8, "bold"), bg="#334155", fg="#f8fafc", activebackground="#475569", activeforeground="white", relief=tk.FLAT, command=self.browse_pages_dir).pack(side=tk.LEFT, padx=2, pady=4)
        
        tk.Label(card1, text="  💾 Database:", font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#1e293b").pack(side=tk.LEFT, padx=(10, 2), pady=4)
        self.db_entry = tk.Entry(card1, font=("Segoe UI", 9), width=28, bg="#0f172a", fg="#f8fafc", insertbackground="white")
        self.db_entry.pack(side=tk.LEFT, padx=3, pady=4)
        tk.Button(card1, text="Browse...", font=("Segoe UI", 8, "bold"), bg="#334155", fg="#f8fafc", activebackground="#475569", activeforeground="white", relief=tk.FLAT, command=self.browse_database).pack(side=tk.LEFT, padx=2, pady=4)
        
        self.folder_status_lbl = tk.Label(card1, text="", font=("Segoe UI", 9, "italic"), fg="#38bdf8", bg="#1e293b")
        self.folder_status_lbl.pack(side=tk.LEFT, padx=12, pady=4)
        
        # Panel 2: Detection Settings & Template
        card2 = tk.Frame(top_container, bg="#1e293b", bd=1, relief=tk.FLAT)
        card2.pack(fill=tk.X, padx=6, pady=(0, 4))
        
        # Auto-detect Checkbox
        self.auto_detect_var = tk.BooleanVar(value=True)
        tk.Checkbutton(card2, text="Auto-Detect", variable=self.auto_detect_var, font=("Segoe UI", 9, "bold"), fg="#f8fafc", bg="#1e293b", selectcolor="#0f172a", activebackground="#1e293b", activeforeground="#f8fafc").pack(side=tk.LEFT, padx=(8, 4), pady=4)
        
        tk.Label(card2, text="Method:", font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#1e293b").pack(side=tk.LEFT, padx=(4, 2), pady=4)
        self.det_method_var = tk.StringVar(value="Hough Circles")
        self.det_combo = ttk.Combobox(card2, textvariable=self.det_method_var, values=["Hough Circles", "Template Matching", "Combined"], state="readonly", width=16, font=("Segoe UI", 9))
        self.det_combo.pack(side=tk.LEFT, padx=2, pady=4)
        self.det_combo.bind("<<ComboboxSelected>>", self.on_method_changed)
        
        self.param_lbl = tk.Label(card2, text="Strictness (param2):", font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#1e293b")
        self.param_lbl.pack(side=tk.LEFT, padx=(8, 2), pady=4)
        self.thresh_var = tk.DoubleVar(value=25)
        self.thresh_slider = tk.Scale(card2, from_=18, to=35, resolution=1, orient=tk.HORIZONTAL, variable=self.thresh_var, length=90, showvalue=0, command=self.on_thresh_change, bg="#1e293b", fg="#f8fafc", highlightthickness=0, troughcolor="#0f172a")
        self.thresh_slider.pack(side=tk.LEFT, padx=2, pady=4)
        self.thresh_val_lbl = tk.Label(card2, text="25", font=("Segoe UI", 9, "bold"), fg="#f8fafc", bg="#1e293b", width=5)
        self.thresh_val_lbl.pack(side=tk.LEFT, pady=4)
        
        tk.Button(card2, text="⚡ Re-Detect (F5)", font=("Segoe UI", 8, "bold"), bg="#0284c7", fg="white", activebackground="#0369a1", activeforeground="white", relief=tk.FLAT, padx=6, command=self.run_detection).pack(side=tk.LEFT, padx=4, pady=4)
        tk.Button(card2, text="Clear", font=("Segoe UI", 8), bg="#991b1b", fg="white", activebackground="#7f1d1d", activeforeground="white", relief=tk.FLAT, padx=5, command=self.clear_markers).pack(side=tk.LEFT, padx=2, pady=4)
        
        tk.Label(card2, text="  🎯 Template:", font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#1e293b").pack(side=tk.LEFT, padx=(10, 2), pady=4)
        self.template_entry = tk.Entry(card2, font=("Segoe UI", 8), width=18, bg="#0f172a", fg="#f8fafc", insertbackground="white")
        self.template_entry.pack(side=tk.LEFT, padx=2, pady=4)
        tk.Button(card2, text="Browse...", font=("Segoe UI", 8), bg="#334155", fg="#f8fafc", activebackground="#475569", relief=tk.FLAT, command=self.browse_template).pack(side=tk.LEFT, padx=1, pady=4)
        
        self.crop_btn = tk.Button(card2, text="✂ Crop from Page", font=("Segoe UI", 8, "bold"), bg="#ea580c", fg="white", activebackground="#c2410c", relief=tk.FLAT, padx=4, command=self.start_crop_template)
        self.crop_btn.pack(side=tk.LEFT, padx=3, pady=4)
        
        self.template_thumb_lbl = tk.Label(card2, text="[No Template]", font=("Segoe UI", 8), bg="#334155", fg="#94a3b8", width=12, height=1)
        self.template_thumb_lbl.pack(side=tk.LEFT, padx=4, pady=4)
        
        # 3. Modern Navigation & Advanced Jump Bar
        nav_frame = tk.Frame(self.root, bg="#f8fafc", bd=1, relief=tk.FLAT)
        nav_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # Row 1 of Nav: Page scrubbing and controls
        n1 = tk.Frame(nav_frame, bg="#f8fafc")
        n1.pack(fill=tk.X, padx=8, pady=(4, 2))
        
        tk.Button(n1, text="⏮ First", font=("Segoe UI", 8, "bold"), bg="#e2e8f0", fg="#334155", relief=tk.FLAT, padx=4, command=lambda: self.jump_to_page(1)).pack(side=tk.LEFT, padx=1)
        tk.Button(n1, text="◀ Prev Page", font=("Segoe UI", 9, "bold"), bg="#e2e8f0", fg="#0f172a", relief=tk.FLAT, padx=6, command=self.prev_page).pack(side=tk.LEFT, padx=2)
        
        tk.Label(n1, text="Page:", font=("Segoe UI", 10, "bold"), fg="#1e293b", bg="#f8fafc").pack(side=tk.LEFT, padx=(8, 2))
        self.jump_entry = tk.Entry(n1, width=5, font=("Segoe UI", 10, "bold"), justify=tk.CENTER, bg="white", fg="#0f172a", relief=tk.SOLID, bd=1)
        self.jump_entry.pack(side=tk.LEFT, padx=2)
        self.total_page_lbl = tk.Label(n1, text="/ 611", font=("Segoe UI", 10), fg="#64748b", bg="#f8fafc")
        self.total_page_lbl.pack(side=tk.LEFT, padx=(1, 4))
        tk.Button(n1, text="Go", font=("Segoe UI", 8, "bold"), bg="#0284c7", fg="white", activebackground="#0369a1", relief=tk.FLAT, padx=6, command=self.on_jump_click).pack(side=tk.LEFT, padx=2)
        
        tk.Button(n1, text="Next Page ▶", font=("Segoe UI", 9, "bold"), bg="#e2e8f0", fg="#0f172a", relief=tk.FLAT, padx=6, command=self.next_page).pack(side=tk.LEFT, padx=2)
        tk.Button(n1, text="Last ⏭", font=("Segoe UI", 8, "bold"), bg="#e2e8f0", fg="#334155", relief=tk.FLAT, padx=4, command=lambda: self.jump_to_page(self.total_pages)).pack(side=tk.LEFT, padx=1)
        
        # Scrubber slider
        self.page_slider = tk.Scale(n1, from_=1, to=611, orient=tk.HORIZONTAL, showvalue=0, command=self.on_slider_move, bg="#f8fafc", troughcolor="#e2e8f0", highlightthickness=0, length=150)
        self.page_slider.pack(side=tk.LEFT, padx=8)
        
        # Unmarked Jump Buttons
        tk.Button(n1, text="◀ Prev Unmarked", font=("Segoe UI", 8, "bold"), bg="#fef08a", fg="#854d0e", relief=tk.FLAT, padx=5, command=self.jump_prev_unmarked).pack(side=tk.LEFT, padx=3)
        tk.Button(n1, text="Next Unmarked ▶", font=("Segoe UI", 8, "bold"), bg="#fef08a", fg="#854d0e", relief=tk.FLAT, padx=5, command=self.jump_next_unmarked).pack(side=tk.LEFT, padx=2)
        
        # Status Badge for Current Page
        self.page_db_badge = tk.Label(n1, text="● UNSAVED", font=("Segoe UI", 9, "bold"), bg="#d97706", fg="white", padx=10, pady=2)
        self.page_db_badge.pack(side=tk.RIGHT, padx=10)
        
        # Row 2 of Nav: Sura & Ayah Jump + Sequence Override + Zoom
        n2 = tk.Frame(nav_frame, bg="#f8fafc")
        n2.pack(fill=tk.X, padx=8, pady=(2, 4))
        
        tk.Label(n2, text="Jump by Surah:", font=("Segoe UI", 9, "bold"), fg="#1e293b", bg="#f8fafc").pack(side=tk.LEFT)
        sura_values = [f"{s[0]:03d}. {s[1]} ({s[2]}) - {s[3]} ayat" for s in SURAS]
        self.sura_combo = ttk.Combobox(n2, values=sura_values, state="readonly", width=34, font=("Segoe UI", 9))
        self.sura_combo.current(0)
        self.sura_combo.pack(side=tk.LEFT, padx=4)
        self.sura_combo.bind("<<ComboboxSelected>>", self.on_sura_selected)
        
        tk.Label(n2, text="Ayah:", font=("Segoe UI", 9, "bold"), fg="#1e293b", bg="#f8fafc").pack(side=tk.LEFT, padx=(6, 2))
        self.ayah_spinbox = tk.Spinbox(n2, from_=1, to=7, width=4, font=("Segoe UI", 9, "bold"), justify=tk.CENTER)
        self.ayah_spinbox.pack(side=tk.LEFT, padx=2)
        
        tk.Button(n2, text="Jump to Sura/Ayah", font=("Segoe UI", 8, "bold"), bg="#0284c7", fg="white", activebackground="#0369a1", relief=tk.FLAT, padx=6, command=self.jump_to_sura_ayah).pack(side=tk.LEFT, padx=4)
        
        # Sequence Tracker & Manual Override
        tk.Label(n2, text=" | Assign Next As: Sura", font=("Segoe UI", 9, "bold"), fg="#475569", bg="#f8fafc").pack(side=tk.LEFT, padx=(12, 2))
        self.seq_sura_entry = tk.Spinbox(n2, from_=1, to=114, width=3, font=("Segoe UI", 9, "bold"), justify=tk.CENTER)
        self.seq_sura_entry.pack(side=tk.LEFT, padx=2)
        tk.Label(n2, text="Ayah", font=("Segoe UI", 9, "bold"), fg="#475569", bg="#f8fafc").pack(side=tk.LEFT, padx=(4, 2))
        self.seq_ayah_entry = tk.Spinbox(n2, from_=1, to=286, width=4, font=("Segoe UI", 9, "bold"), justify=tk.CENTER)
        self.seq_ayah_entry.pack(side=tk.LEFT, padx=2)
        tk.Button(n2, text="Set Sequence", font=("Segoe UI", 8, "bold"), bg="#10b981", fg="white", activebackground="#059669", relief=tk.FLAT, padx=6, command=self.apply_sequence_override).pack(side=tk.LEFT, padx=4)
        
        # Zoom controls
        z_frame = tk.Frame(n2, bg="#f8fafc")
        z_frame.pack(side=tk.RIGHT, padx=5)
        tk.Button(z_frame, text="🔎 -", font=("Segoe UI", 8), bg="#e2e8f0", relief=tk.FLAT, padx=4, command=self.zoom_out).pack(side=tk.LEFT, padx=1)
        tk.Button(z_frame, text="🔍 Fit", font=("Segoe UI", 8, "bold"), bg="#e2e8f0", relief=tk.FLAT, padx=5, command=self.zoom_fit).pack(side=tk.LEFT, padx=1)
        tk.Button(z_frame, text="🔎 +", font=("Segoe UI", 8), bg="#e2e8f0", relief=tk.FLAT, padx=4, command=self.zoom_in).pack(side=tk.LEFT, padx=1)
        
        # 4. Canvas Frame with Centered View and Scrollbars
        canvas_container = tk.Frame(self.root, bg="#1e293b")
        canvas_container.pack(fill=tk.BOTH, expand=True)
        
        self.v_scroll = tk.Scrollbar(canvas_container, orient=tk.VERTICAL)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll = tk.Scrollbar(canvas_container, orient=tk.HORIZONTAL)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas = tk.Canvas(canvas_container, cursor="cross", bg="#334155",
                               xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)
        
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self.on_shift_mousewheel)
        self.canvas.bind("<Control-MouseWheel>", self.on_ctrl_mousewheel)
        
        # 5. Bottom Action & Status Bar
        btn_frame = tk.Frame(self.root, bg="#0f172a", bd=1)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.info_lbl = tk.Label(btn_frame, text="Ready", font=("Segoe UI", 11, "bold"), fg="#f8fafc", bg="#0f172a")
        self.info_lbl.pack(side=tk.LEFT, padx=15, pady=8)
        
        self.status_detail_lbl = tk.Label(btn_frame, text="", font=("Segoe UI", 9), fg="#94a3b8", bg="#0f172a")
        self.status_detail_lbl.pack(side=tk.LEFT, padx=10, pady=8)
        
        tk.Button(btn_frame, text="Undo (Ctrl+Z)", font=("Segoe UI", 9), bg="#334155", fg="#f8fafc", activebackground="#475569", relief=tk.FLAT, padx=8, command=self.undo).pack(side=tk.RIGHT, padx=6, pady=8)
        tk.Button(btn_frame, text="Save Only (Ctrl+S)", font=("Segoe UI", 9, "bold"), bg="#0284c7", fg="white", activebackground="#0369a1", relief=tk.FLAT, padx=10, command=lambda: self.save_page(advance=False)).pack(side=tk.RIGHT, padx=6, pady=8)
        
        self.next_btn = tk.Button(btn_frame, text="SAVE & NEXT PAGE (Enter) ➔", font=("Segoe UI", 11, "bold"), bg="#10b981", fg="white", activebackground="#059669", relief=tk.FLAT, padx=16, pady=2, command=self.next_page)
        self.next_btn.pack(side=tk.RIGHT, padx=15, pady=8)
        
        # Global Key Bindings
        self.root.bind('<Return>', lambda e: self.next_page())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-s>', lambda e: self.save_page(advance=False))
        self.root.bind('<Control-o>', lambda e: self.browse_pages_dir())
        self.root.bind('<Control-t>', lambda e: self.browse_template())
        self.root.bind('<Control-d>', lambda e: self.browse_database())
        self.root.bind('<Control-n>', lambda e: self.jump_next_unmarked())
        self.root.bind('<Control-p>', lambda e: self.jump_prev_unmarked())
        self.root.bind('<F5>', lambda e: self.run_detection())
        self.root.bind('<Left>', lambda e: self.prev_page())
        self.root.bind('<Right>', lambda e: self.next_page())
        self.root.bind('<Control-q>', lambda e: self.confirm_exit())

    def confirm_exit(self):
        msg = "Are you sure you want to exit Ayah Marker Detector?\n\nPlease make sure your work on the current page is saved."
        if messagebox.askyesno("Exit Confirmation", msg, icon="question", default="no"):
            self.root.destroy()

    def on_canvas_resize(self, event):
        # Dynamically re-center image when window or canvas resizes
        if self.full_img is not None:
            canvas_w = event.width
            new_w = int(self.full_img.shape[1] * self.scale)
            new_offset_x = max(20, (canvas_w - new_w) // 2) if canvas_w > new_w else 20
            if abs(new_offset_x - self.offset_x) > 5:
                self.offset_x = new_offset_x
                self.redraw()

    def on_method_changed(self, event=None):
        method = self.det_method_var.get()
        if method == "Hough Circles":
            self.param_lbl.config(text="Strictness (param2):")
            self.thresh_slider.config(from_=18, to=35, resolution=1)
            self.thresh_var.set(25)
            self.thresh_val_lbl.config(text="25")
        elif method == "Template Matching":
            self.param_lbl.config(text="Match Threshold:")
            self.thresh_slider.config(from_=0.40, to=0.85, resolution=0.01)
            self.thresh_var.set(0.65)
            self.thresh_val_lbl.config(text="0.65")
        elif method == "Combined":
            self.param_lbl.config(text="Combined Sensitivity:")
            self.thresh_slider.config(from_=0.40, to=0.85, resolution=0.01)
            self.thresh_var.set(0.65)
            self.thresh_val_lbl.config(text="0.65")

    def on_thresh_change(self, val):
        if self.det_method_var.get() == "Hough Circles":
            self.thresh_val_lbl.config(text=f"{int(float(val))}")
        else:
            self.thresh_val_lbl.config(text=f"{float(val):.2f}")

    def on_sura_selected(self, event=None):
        idx = self.sura_combo.current()
        if idx >= 0:
            total_ayat = SURAS[idx][3]
            self.ayah_spinbox.config(to=total_ayat)
            cur = int(self.ayah_spinbox.get()) if self.ayah_spinbox.get().isdigit() else 1
            if cur > total_ayat:
                self.ayah_spinbox.delete(0, tk.END)
                self.ayah_spinbox.insert(0, str(total_ayat))

    def load_pages_folder(self, folder, initial=False):
        if not folder or not os.path.exists(folder):
            if not initial:
                messagebox.showerror("Error", f"Folder not found: {folder}")
            return
            
        self.img_dir = folder
        self.pages_entry.delete(0, tk.END)
        self.pages_entry.insert(0, folder)
        
        self.page_files = find_page_files(folder)
        if self.page_files:
            self.total_pages = max(self.page_files.keys())
            self.total_page_lbl.config(text=f"/ {self.total_pages}")
            self.page_slider.config(to=self.total_pages)
            self.folder_status_lbl.config(text=f"Loaded {len(self.page_files)} pages (1-{self.total_pages})")
            if not initial:
                if self.current_page not in self.page_files:
                    self.current_page = min(self.page_files.keys())
                self.load_page()
        else:
            self.folder_status_lbl.config(text="No supported image files found in folder!")

    def browse_pages_dir(self):
        chosen = filedialog.askdirectory(title="Select Quran Pages Folder", initialdir=self.img_dir or os.getcwd())
        if chosen:
            self.load_pages_folder(chosen)

    def browse_database(self):
        chosen = filedialog.askopenfilename(title="Select or Create Ayah Markers SQLite Database",
                                            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
                                            initialdir=os.path.dirname(self.db_path) if self.db_path else os.getcwd())
        if chosen:
            self.db_path = chosen
            self.db_entry.delete(0, tk.END)
            self.db_entry.insert(0, chosen)
            self.init_db()
            self.load_page()

    def load_template(self, template_path):
        if not template_path or not os.path.exists(template_path):
            self.template_thumb_lbl.config(image="", text="[No Template]")
            self.template_gray = None
            return False
            
        self.template_path = template_path
        self.template_entry.delete(0, tk.END)
        self.template_entry.insert(0, template_path)
        self.template_gray = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        
        if self.template_gray is not None:
            th_img = cv2.resize(self.template_gray, (36, 36), interpolation=cv2.INTER_AREA)
            pil_thumb = Image.fromarray(th_img)
            self.thumb_photo = ImageTk.PhotoImage(pil_thumb)
            self.template_thumb_lbl.config(image=self.thumb_photo, text="")
            return True
        return False

    def browse_template(self):
        chosen = filedialog.askopenfilename(title="Select Marker Template Image",
                                            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.webp"), ("All Files", "*.*")],
                                            initialdir=os.path.dirname(self.template_path) if self.template_path else os.getcwd())
        if chosen:
            if self.load_template(chosen):
                if messagebox.askyesno("Template Loaded", f"Template successfully loaded:\n{chosen}\n\nSwitch detection method to 'Template Matching'?"):
                    self.det_method_var.set("Template Matching")
                    self.on_method_changed()

    def start_crop_template(self):
        self.is_cropping_template = True
        self.canvas.config(cursor="sizing")
        self.crop_btn.config(bg="#f87171", text="Click on Marker to Crop...")
        self.info_lbl.config(text="✂ TEMPLATE MODE: Click directly on the center of any Ayah marker on the page!")

    def init_db(self):
        self.db_entry.delete(0, tk.END)
        self.db_entry.insert(0, self.db_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_markers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            page_number INTEGER,
            sura_number INTEGER,
            ayah_number INTEGER,
            cx INTEGER,
            cy INTEGER
        );
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_raw_page ON raw_markers(page_number);')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_raw_sura_ayah ON raw_markers(sura_number, ayah_number);')
        
        cursor.execute('SELECT page_number, sura_number, ayah_number FROM raw_markers ORDER BY id DESC LIMIT 1')
        last_entry = cursor.fetchone()
        if last_entry:
            last_page, last_sura, last_ayah = last_entry
            if last_page >= self.current_page:
                self.current_page = last_page + 1
                if last_ayah >= hafs_ayat[last_sura - 1]:
                    self.sura = min(114, last_sura + 1)
                    self.ayah = 1
                else:
                    self.sura = last_sura
                    self.ayah = last_ayah + 1
                    
        conn.commit()
        conn.close()
        self.update_seq_display()

    def update_seq_display(self):
        self.seq_sura_entry.delete(0, tk.END)
        self.seq_sura_entry.insert(0, str(self.sura))
        self.seq_ayah_entry.delete(0, tk.END)
        self.seq_ayah_entry.insert(0, str(self.ayah))

    def apply_sequence_override(self):
        try:
            s = int(self.seq_sura_entry.get())
            a = int(self.seq_ayah_entry.get())
            if not (1 <= s <= 114):
                messagebox.showerror("Error", "Sura must be between 1 and 114")
                return
            if not (1 <= a <= hafs_ayat[s - 1]):
                messagebox.showerror("Error", f"Ayah must be between 1 and {hafs_ayat[s - 1]} for Sura {s}")
                return
            self.sura = s
            self.ayah = a
            self.update_status_label()
            messagebox.showinfo("Sequence Updated", f"Next marker sequence set to:\nSura {self.sura} ({SURAS[self.sura-1][1]}), Ayah {self.ayah}")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric Sura and Ayah")

    def on_slider_move(self, val):
        target = int(val)
        if target != self.current_page:
            self.jump_to_page(target)

    def on_jump_click(self):
        try:
            target = int(self.jump_entry.get())
            self.jump_to_page(target)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid page number")

    def jump_to_page(self, target_page, auto_calc_sura=True):
        if target_page < 1 or target_page > self.total_pages:
            messagebox.showerror("Error", f"Page must be between 1 and {self.total_pages}")
            return
            
        if auto_calc_sura and os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT sura_number, ayah_number FROM raw_markers WHERE page_number < ? ORDER BY id DESC LIMIT 1', (target_page,))
            last_entry = cursor.fetchone()
            if last_entry:
                last_sura, last_ayah = last_entry
                if last_ayah >= hafs_ayat[last_sura - 1]:
                    self.sura = min(114, last_sura + 1)
                    self.ayah = 1
                else:
                    self.sura = last_sura
                    self.ayah = last_ayah + 1
            else:
                self.sura = 1
                self.ayah = 1
            conn.close()
            self.update_seq_display()
            
        self.current_page = target_page
        self.load_page()

    def jump_to_sura_ayah(self):
        idx = self.sura_combo.current()
        if idx < 0:
            return
        target_sura = SURAS[idx][0]
        try:
            target_ayah = int(self.ayah_spinbox.get())
        except ValueError:
            target_ayah = 1
            
        target_page = None
        # 1. Search DB for raw_markers
        if os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('SELECT page_number FROM raw_markers WHERE sura_number = ? AND ayah_number = ? LIMIT 1', (target_sura, target_ayah))
            row = c.fetchone()
            if row:
                target_page = row[0]
            else:
                # Also check ayah_highlights if compiled DB opened
                try:
                    c.execute('SELECT page FROM ayah_highlights WHERE sura = ? AND ayah = ? LIMIT 1', (target_sura, target_ayah))
                    row2 = c.fetchone()
                    if row2:
                        target_page = row2[0]
                except Exception:
                    pass
            conn.close()
            
        # 2. Fallback to known standard 15-line page
        if not target_page:
            target_page = SURA_START_PAGES.get(target_sura, 1)
            
        self.sura = target_sura
        self.ayah = target_ayah
        self.update_seq_display()
        self.jump_to_page(target_page, auto_calc_sura=False)

    def jump_next_unmarked(self):
        if not os.path.exists(self.db_path):
            return
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT DISTINCT page_number FROM raw_markers')
        marked = set(r[0] for r in c.fetchall())
        conn.close()
        
        for p in range(self.current_page + 1, self.total_pages + 1):
            if p not in marked and p in self.page_files:
                self.jump_to_page(p)
                return
        messagebox.showinfo("Navigation", "No more unmarked pages found after current page!")

    def jump_prev_unmarked(self):
        if not os.path.exists(self.db_path):
            return
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT DISTINCT page_number FROM raw_markers')
        marked = set(r[0] for r in c.fetchall())
        conn.close()
        
        for p in range(self.current_page - 1, 0, -1):
            if p not in marked and p in self.page_files:
                self.jump_to_page(p)
                return
        messagebox.showinfo("Navigation", "No unmarked pages found before current page!")

    def save_state(self):
        self.history.append(list(self.circles))

    def undo(self, event=None):
        if self.history:
            self.circles = self.history.pop()
            self.redraw()

    def clear_markers(self):
        self.save_state()
        self.circles = []
        self.redraw()

    def run_detection(self):
        if self.full_img is None:
            return
        self.save_state()
        method = self.det_method_var.get()
        
        detected_pts = []
        if method == "Template Matching":
            if self.template_gray is not None:
                th = self.thresh_var.get()
                detected_pts = self.detect_with_template(self.full_img, self.template_gray, threshold=th, lines=self.lines)
            else:
                messagebox.showwarning("Template Missing", "No template image loaded! Please browse or crop a template first.")
                return
        elif method == "Combined":
            hough_pts = self.detect_with_hough(self.full_img, lines=self.lines)
            if self.template_gray is not None:
                th = self.thresh_var.get()
                tm_pts = self.detect_with_template(self.full_img, self.template_gray, threshold=th, lines=self.lines)
                min_dist_sq = 45 * 45
                for tx, ty in tm_pts:
                    if not any((tx - hx)**2 + (ty - hy)**2 < min_dist_sq for hx, hy in hough_pts):
                        hough_pts.append((tx, ty))
            detected_pts = hough_pts
        else:
            # Default: Hough Circles
            detected_pts = self.detect_with_hough(self.full_img, lines=self.lines)
                
        self.circles = detected_pts
        self.redraw()

    def detect_with_template(self, img_gray, template, threshold=0.65, min_dist=40, lines=None):
        if img_gray is None or template is None:
            return []
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        h, w = template.shape
        candidates = []
        for y, x in zip(*loc):
            candidates.append((float(res[y, x]), int(x + w // 2), int(y + h // 2)))
        candidates.sort(key=lambda item: item[0], reverse=True)
        
        min_x, max_x = 0, img_gray.shape[1]
        min_y, max_y = 0, img_gray.shape[0]
        if lines:
            min_x = min([l[0][0] for l in lines]) - 10
            max_x = max([l[1][0] for l in lines]) + 10
            min_y = min([l[0][1] for l in lines]) - 20
            max_y = max([l[1][1] for l in lines]) + 20
            
        min_dist_sq = min_dist * min_dist
        final_points = []
        for score, cx, cy in candidates:
            if cx < min_x or cx > max_x or cy < min_y or cy > max_y:
                continue
            if not any((cx - px)**2 + (cy - py)**2 < min_dist_sq for px, py in final_points):
                final_points.append((cx, cy))
        return final_points

    def detect_with_hough(self, img_gray, lines=None):
        blurred = cv2.medianBlur(img_gray, 5)
        p2 = int(self.thresh_var.get()) if self.det_method_var.get() == "Hough Circles" else 25
        detected = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                                   param1=50, param2=p2, minRadius=27, maxRadius=36)
        points = []
        if detected is not None:
            if lines:
                global_min_x = min([l[0][0] for l in lines])
                global_max_x = max([l[1][0] for l in lines])
                global_min_y = min([l[0][1] for l in lines]) - 20
                global_max_y = max([l[1][1] for l in lines]) + 20
                for c in detected[0]:
                    cx, cy = int(c[0]), int(c[1])
                    if (global_min_x - 10 <= cx <= global_max_x + 10) and (global_min_y <= cy <= global_max_y):
                        points.append((cx, cy))
            else:
                for c in detected[0]:
                    points.append((int(c[0]), int(c[1])))
        return points

    def load_page(self):
        if self.current_page > self.total_pages:
            messagebox.showinfo("Done", "Processed all pages! You can close this window.")
            return
            
        img_path = self.page_files.get(self.current_page)
        if not img_path or not os.path.exists(img_path):
            img_path = os.path.join(self.img_dir, f"page{self.current_page:03d}.png")
            if not os.path.exists(img_path):
                img_path = os.path.join(self.img_dir, f"{self.current_page}.png")
                
        if not os.path.exists(img_path):
            self.folder_status_lbl.config(text=f"Page {self.current_page} image not found in directory!")
            return
            
        self.full_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if self.full_img is None:
            messagebox.showerror("Error", f"Failed to load image: {img_path}")
            return
            
        self.lines = find_text_lines(self.full_img)
        self.circles = []
        
        # Check DB for existing markers
        existing_markers = []
        if os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT cx, cy FROM raw_markers WHERE page_number = ? ORDER BY id', (self.current_page,))
            existing_markers = cursor.fetchall()
            conn.close()
            
        if existing_markers:
            self.circles = [(cx, cy) for cx, cy in existing_markers]
            self.page_db_badge.config(text=f"✔ SAVED ({len(self.circles)} markers)", bg="#059669")
        else:
            self.page_db_badge.config(text="● UNSAVED", bg="#d97706")
            if self.auto_detect_var.get():
                if self.det_method_var.get() == "Template Matching" and self.template_gray is not None:
                    self.circles = self.detect_with_template(self.full_img, self.template_gray, threshold=self.thresh_var.get(), lines=self.lines)
                elif self.det_method_var.get() == "Combined":
                    hough_pts = self.detect_with_hough(self.full_img, lines=self.lines)
                    if self.template_gray is not None:
                        tm_pts = self.detect_with_template(self.full_img, self.template_gray, threshold=self.thresh_var.get(), lines=self.lines)
                        min_dist_sq = 45 * 45
                        for tx, ty in tm_pts:
                            if not any((tx - hx)**2 + (ty - hy)**2 < min_dist_sq for hx, hy in hough_pts):
                                hough_pts.append((tx, ty))
                    self.circles = hough_pts
                else:
                    # Default: Hough Circles
                    self.circles = self.detect_with_hough(self.full_img, lines=self.lines)
                
        self.history = []
        
        # Image scaling
        self.tk_img_orig = Image.open(img_path)
        w, h = self.tk_img_orig.size
        
        screen_h = self.root.winfo_screenheight()
        target_h = int(screen_h * 0.72)
        self.base_scale = target_h / h
        self.scale = self.base_scale * self.zoom_level
        
        self.update_canvas_image()
        
        self.jump_entry.delete(0, tk.END)
        self.jump_entry.insert(0, str(self.current_page))
        self.page_slider.set(self.current_page)
        
        self.redraw()

    def update_canvas_image(self):
        w, h = self.tk_img_orig.size
        new_w, new_h = int(w * self.scale), int(h * self.scale)
        self.tk_img = ImageTk.PhotoImage(self.tk_img_orig.resize((new_w, new_h), Image.Resampling.LANCZOS))
        
        canvas_w = self.canvas.winfo_width()
        self.offset_x = max(20, (canvas_w - new_w) // 2) if canvas_w > new_w else 20
        self.offset_y = 15
        
        scroll_w = max(canvas_w, self.offset_x + new_w + 40)
        scroll_h = self.offset_y + new_h + 40
        self.canvas.config(scrollregion=(0, 0, scroll_w, scroll_h))

    def zoom_in(self):
        self.zoom_level = min(3.0, self.zoom_level + 0.15)
        self.scale = self.base_scale * self.zoom_level
        self.update_canvas_image()
        self.redraw()

    def zoom_out(self):
        self.zoom_level = max(0.4, self.zoom_level - 0.15)
        self.scale = self.base_scale * self.zoom_level
        self.update_canvas_image()
        self.redraw()

    def zoom_fit(self):
        self.zoom_level = 1.0
        self.scale = self.base_scale
        self.update_canvas_image()
        self.redraw()

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_shift_mousewheel(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_ctrl_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def redraw(self):
        self.canvas.delete("all")
        # Draw image centered horizontally
        self.canvas.create_image(self.offset_x, self.offset_y, anchor=tk.NW, image=self.tk_img)
        
        for idx, (cx, cy) in enumerate(self.circles, 1):
            x = self.offset_x + cx * self.scale
            y = self.offset_y + cy * self.scale
            r = 18 * self.scale
            
            # 1. Subtle white outer glow ring for high contrast
            self.canvas.create_oval(x - r - 1, y - r - 1, x + r + 1, y + r + 1, outline="#ffffff", width=1)
            # 2. Main red marker circle
            self.canvas.create_oval(x - r, y - r, x + r, y + r, outline="#dc2626", width=2)
            # 3. Center dot
            self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="#dc2626", outline="#ffffff")
            # 4. Badge with Ayah number
            badge_r = max(8, int(9 * self.scale))
            bx, by = x + r + 12, y
            self.canvas.create_oval(bx - badge_r, by - badge_r, bx + badge_r, by + badge_r, fill="#1e3a8a", outline="#ffffff", width=1)
            self.canvas.create_text(bx, by, text=str(idx), fill="#ffffff", font=("Segoe UI", max(7, int(8 * self.scale)), "bold"))
            
        self.update_status_label()

    def update_status_label(self):
        sura_name = SURAS[self.sura - 1][1] if 1 <= self.sura <= 114 else "Unknown"
        self.info_lbl.config(
            text=f"Page {self.current_page} of {self.total_pages} | Markers: {len(self.circles)} | Next: Sura {self.sura} ({sura_name}), Ayah {self.ayah}"
        )
        self.status_detail_lbl.config(
            text=f"Zoom: {int(self.zoom_level*100)}% | Method: {self.det_method_var.get()}"
        )

    def on_click(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        orig_x = int((canvas_x - self.offset_x) / self.scale)
        orig_y = int((canvas_y - self.offset_y) / self.scale)
        
        # Guard against clicks outside image
        if self.full_img is not None:
            if orig_x < 0 or orig_x >= self.full_img.shape[1] or orig_y < 0 or orig_y >= self.full_img.shape[0]:
                return
                
        if self.is_cropping_template:
            r = 25
            min_y, max_y = max(0, orig_y - r), min(self.full_img.shape[0], orig_y + r)
            min_x, max_x = max(0, orig_x - r), min(self.full_img.shape[1], orig_x + r)
            cropped = self.full_img[min_y:max_y, min_x:max_x]
            
            save_path = "template_custom.png"
            cv2.imwrite(save_path, cropped)
            self.load_template(save_path)
            
            self.is_cropping_template = False
            self.canvas.config(cursor="cross")
            self.crop_btn.config(bg="#ea580c", text="✂ Crop from Page")
            self.det_method_var.set("Template Matching")
            self.on_method_changed()
            self.redraw()
            messagebox.showinfo("Template Captured", f"Template successfully cropped and saved as {save_path}!\nSwitched detection method to 'Template Matching'.")
            return
            
        self.save_state()
        
        # Check if clicking on an existing circle to delete
        threshold_dist = 40
        for i, (cx, cy) in enumerate(self.circles):
            if (cx - orig_x)**2 + (cy - orig_y)**2 < threshold_dist**2:
                self.circles.pop(i)
                self.redraw()
                return
                
        # Add new circle
        self.circles.append((orig_x, orig_y))
        self.redraw()

    def prev_page(self):
        if self.current_page > 1:
            self.jump_to_page(self.current_page - 1)

    def next_page(self):
        self.save_page(advance=True)

    def save_page(self, advance=True):
        if not self.lines:
            w = self.full_img.shape[1] if self.full_img is not None else 2000
            h = self.full_img.shape[0] if self.full_img is not None else 3000
            self.lines = [((0, 0), (w, h))]
            
        line_assigned = {i: [] for i in range(len(self.lines))}
        for cx, cy in self.circles:
            closest_idx = 0
            min_dist = float('inf')
            for idx, line in enumerate(self.lines):
                ly_mid = (line[0][1] + line[1][1]) / 2
                dist = abs(ly_mid - cy)
                if dist < min_dist:
                    min_dist = dist
                    closest_idx = idx
            line_assigned[closest_idx].append((cx, cy))
            
        insert_data = []
        cur_sura = self.sura
        cur_ayah = self.ayah
        
        for idx in range(len(self.lines)):
            line_circles = sorted(line_assigned[idx], key=lambda c: -c[0]) 
            for cx, cy in line_circles:
                insert_data.append((self.current_page, cur_sura, cur_ayah, cx, cy))
                if cur_ayah >= hafs_ayat[cur_sura - 1]:
                    if cur_sura < 114:
                        cur_sura += 1
                        cur_ayah = 1
                    else:
                        cur_ayah += 1
                else:
                    cur_ayah += 1
                    
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM raw_markers WHERE page_number = ?', (self.current_page,))
        cursor.executemany('''
            INSERT INTO raw_markers (page_number, sura_number, ayah_number, cx, cy)
            VALUES (?, ?, ?, ?, ?)
        ''', insert_data)
        conn.commit()
        conn.close()
        
        self.sura = cur_sura
        self.ayah = cur_ayah
        self.update_seq_display()
        self.page_db_badge.config(text=f"✔ SAVED ({len(self.circles)} markers)", bg="#059669")
        
        if advance:
            if self.current_page < self.total_pages:
                self.current_page += 1
                self.load_page()
            else:
                messagebox.showinfo("Done", "Reached the last page of the Quran!")
        else:
            self.update_status_label()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Ayah Marker Detector & Validator (Pro Edition)")
    parser.add_argument('--img_dir', type=str, default=r"D:\Dev\Temp\EmdadiaPages", help="Folder containing Quran page images")
    parser.add_argument('--out_db', type=str, default=r"D:\Dev\Temp\ayahinfo_emdadia_perfect.db", help="SQLite database output path")
    parser.add_argument('--template', type=str, default="", help="Optional template marker image path")
    parser.add_argument('--start_page', type=int, default=1, help="Starting page number")
    parser.add_argument('--end_page', type=int, default=611, help="Ending page number")
    parser.add_argument('--start_sura', type=int, default=1, help="Starting Sura number")
    parser.add_argument('--start_ayah', type=int, default=1, help="Starting Ayah number")
    args = parser.parse_args()
    
    root = tk.Tk()
    app = AyahValidatorApp(
        root=root,
        img_dir=args.img_dir,
        db_path=args.out_db,
        template_path=args.template,
        start_page=args.start_page,
        end_page=args.end_page,
        start_sura=args.start_sura,
        start_ayah=args.start_ayah
    )
    root.mainloop()
