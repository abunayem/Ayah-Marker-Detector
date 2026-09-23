import sqlite3
import shutil

DB_TARGET = r'D:\Dev\Temp\ayahinfo.db'
ASSETS_DB = r'D:\Dev\Workspace\temp\AyahMarker\app\src\main\assets\ayahinfo.db'

conn = sqlite3.connect(DB_TARGET)
c = conn.cursor()

print("Applying fix for Page 564 (Sura 67 & 68)...")

# Delete existing highlights for Page 564
c.execute('DELETE FROM ayah_highlights WHERE page = 564')

# Correct highlights for Page 564:
# Page width is 1860, left margin 0.004, right margin 0.986
p564_rows = [
    # Line 1: Sura 67:23 full line
    (564, 67, 23, 1, 0.004, 0.986),
    
    # Line 2: 67:23 ends at 0.435, 67:24 starts left of 0.435
    (564, 67, 23, 2, 0.435, 0.986),
    (564, 67, 24, 2, 0.004, 0.435),
    
    # Line 3: 67:24 ends at 0.506, 67:25 starts left of 0.506
    (564, 67, 24, 3, 0.506, 0.986),
    (564, 67, 25, 3, 0.004, 0.506),
    
    # Line 4: 67:25 ends at 0.602, 67:26 starts left of 0.602
    (564, 67, 25, 4, 0.602, 0.986),
    (564, 67, 26, 4, 0.004, 0.602),
    
    # Line 5: 67:26 ends at 0.702, 67:27 starts left of 0.702
    (564, 67, 26, 5, 0.702, 0.986),
    (564, 67, 27, 5, 0.004, 0.702),
    
    # Line 6: 67:27 ends at 0.264, 67:28 starts left of 0.264
    (564, 67, 27, 6, 0.264, 0.986),
    (564, 67, 28, 6, 0.004, 0.264),
    
    # Line 7: 67:28 full line
    (564, 67, 28, 7, 0.004, 0.986),
    
    # Line 8: 67:28 ends at 0.613, 67:29 starts left of 0.613
    (564, 67, 28, 8, 0.613, 0.986),
    (564, 67, 29, 8, 0.004, 0.613),
    
    # Line 9: 67:29 ends at 0.176, 67:30 starts left of 0.176
    (564, 67, 29, 9, 0.176, 0.986),
    (564, 67, 30, 9, 0.004, 0.176),
    
    # Line 10: 67:30 ends at 0.111
    (564, 67, 30, 10, 0.111, 0.986),
    
    # Line 11: Sura 68 Header (no highlight)
    # Line 12: Bismillah (no highlight)
    
    # Line 13: Sura 68:1 ends at 0.473, 68:2 starts left of 0.473
    (564, 68, 1, 13, 0.473, 0.986),
    (564, 68, 2, 13, 0.004, 0.473),
    
    # Line 14: 68:2 ends at 0.724, 68:3 ends at 0.271, 68:4 starts left of 0.271
    (564, 68, 2, 14, 0.724, 0.986),
    (564, 68, 3, 14, 0.271, 0.724),
    (564, 68, 4, 14, 0.004, 0.271),
    
    # Line 15: 68:4 ends at 0.702, 68:5 ends at 0.373, 68:6 ends at 0.106, 68:7 starts left of 0.106
    (564, 68, 4, 15, 0.702, 0.986),
    (564, 68, 5, 15, 0.373, 0.702),
    (564, 68, 6, 15, 0.106, 0.373),
    (564, 68, 7, 15, 0.004, 0.106),
]

c.executemany('''
    INSERT INTO ayah_highlights (page, sura, ayah, line, "left", "right")
    VALUES (?, ?, ?, ?, ?, ?)
''', p564_rows)

conn.commit()
conn.close()

print(f"Successfully inserted {len(p564_rows)} corrected rows for Page 564.")

# Copy to assets
shutil.copyfile(DB_TARGET, ASSETS_DB)
print(f"Copied updated database to Android assets: {ASSETS_DB}")
