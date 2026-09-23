import sqlite3

hafs_ayat = [7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111,
             43, 52, 99, 128, 111, 110, 98, 135, 112, 78, 118, 64, 77,
             227, 93, 88, 69, 60, 34, 30, 73, 54, 45, 83, 182, 88, 75,
             85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55,
             78, 96, 29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52,
             44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25,
             22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
             11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6]

conn = sqlite3.connect(r'D:\Dev\Temp\ayahinfo.db')
c = conn.cursor()

print("Auditing all 113 transitions in Backup DB:")
for s in range(1, 114):
    next_s = s + 1
    total_a = hafs_ayat[s-1]
    
    # Last segment of Sura s
    c.execute('SELECT page, line, "left", "right" FROM ayah_highlights WHERE sura = ? AND ayah = ? ORDER BY page DESC, line DESC, "right" ASC LIMIT 1', (s, total_a))
    end_s = c.fetchone()
    
    # First segment of Sura s+1
    c.execute('SELECT page, line, "left", "right" FROM ayah_highlights WHERE sura = ? AND ayah = 1 ORDER BY page ASC, line ASC, "right" DESC LIMIT 1', (next_s,))
    start_next = c.fetchone()
    
    if end_s[0] == start_next[0]:
        # Same page
        gap = start_next[1] - end_s[1]
        req_gap = 2 if next_s == 9 else 3
        if gap != req_gap:
            print(f"TRANSITION MISMATCH [SAME PAGE]: Sura {s}->{next_s} on Page {end_s[0]}: ends at line {end_s[1]}, next starts at line {start_next[1]} (gap={gap}, expected {req_gap})")
    else:
        # Different page
        # Expected: start_next[1] == 3 (or 2 for Sura 9)
        req_line = 2 if next_s == 9 else 3
        if start_next[1] != req_line:
            print(f"TRANSITION MISMATCH [NEW PAGE]: Sura {s}->{next_s}: ends page {end_s[0]} line {end_s[1]}, next starts page {start_next[0]} line {start_next[1]} (expected line {req_line})")
