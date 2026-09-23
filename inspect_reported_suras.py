import sqlite3

hafs_ayat = [7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111,
             43, 52, 99, 128, 111, 110, 98, 135, 112, 78, 118, 64, 77,
             227, 93, 88, 69, 60, 34, 30, 73, 54, 45, 83, 182, 88, 75,
             85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55,
             78, 96, 29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52,
             44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25,
             22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
             11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6]

conn = sqlite3.connect(r'D:\Dev\Temp\Backup\ayahinfo.db')
c = conn.cursor()

def inspect_sura_start(sura_num):
    print(f"\n==========================================")
    print(f"       INSPECTING SURA {sura_num}")
    print(f"==========================================")
    # Find page where Sura starts
    c.execute('SELECT DISTINCT page FROM ayah_highlights WHERE sura = ? AND ayah = 1', (sura_num,))
    pages = [r[0] for r in c.fetchall()]
    if not pages:
        print("  NO PAGE FOUND FOR AYAH 1!")
        return
    
    start_page = pages[0]
    print(f"Sura {sura_num} starts on Page {start_page}")
    
    # Print lines around the start
    # Get all highlights on start_page for previous sura, this sura ayahs 1..3
    c.execute('''
        SELECT line, sura, ayah, "left", "right" 
        FROM ayah_highlights 
        WHERE page = ? 
        ORDER BY line, "right" DESC
    ''', (start_page,))
    all_highlights = c.fetchall()
    
    # Filter to lines near the transition
    relevant_lines = set()
    for l, s, a, left, right in all_highlights:
        if s == sura_num and a <= 3:
            relevant_lines.add(l)
        if s == sura_num - 1 and a >= hafs_ayat[sura_num - 2] - 1:
            relevant_lines.add(l)
            
    # Also include intervening lines
    if relevant_lines:
        min_l = max(1, min(relevant_lines) - 1)
        max_l = min(15, max(relevant_lines) + 1)
    else:
        min_l, max_l = 1, 15
        
    for l, s, a, left, right in all_highlights:
        if min_l <= l <= max_l:
            tag = " ***" if s == sura_num and a == 1 else ""
            print(f"  Line {l:2d} | Sura {s:3d}:{a:<3d} | left: {left:.3f}, right: {right:.3f}{tag}")

check_list = [4, 5, 6, 8, 13, 16, 17, 18, 21, 24, 33, 34, 35, 36, 74, 81, 82, 88, 92, 98, 100, 104, 105, 107, 108]
for s in check_list:
    inspect_sura_start(s)
