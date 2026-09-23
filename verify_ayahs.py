import sqlite3

# Load Emdadia DB
conn = sqlite3.connect(r'D:\Dev\Temp\ayahinfo_emdadia_perfect.db')
cursor = conn.cursor()
cursor.execute('SELECT sura_number, ayah_number, page_number FROM raw_markers ORDER BY page_number, sura_number, ayah_number')
emdadia = cursor.fetchall()
conn.close()

# Load Nasiha DB
conn = sqlite3.connect(r'D:\Dev\Temp\db\nasiha_v2.db')
cursor = conn.cursor()
cursor.execute('SELECT sura, ayah FROM ayah_highlights GROUP BY sura, ayah ORDER BY sura, ayah')
nasiha = cursor.fetchall()
conn.close()

emdadia_set = set([(s, a) for s, a, p in emdadia])
nasiha_set = set(nasiha)

print(f"Total Ayahs in Emdadia DB: {len(emdadia)}")
print(f"Total Ayahs in Nasiha DB: {len(nasiha_set)}")

missing_in_emdadia = nasiha_set - emdadia_set
if missing_in_emdadia:
    print("MISSING IN EMDADIA:")
    for s, a in sorted(list(missing_in_emdadia)):
        print(f"Sura {s}, Ayah {a}")
else:
    print("NO AYAHS MISSING! 100% MATCH!")

missing_in_nasiha = emdadia_set - nasiha_set
if missing_in_nasiha:
    print("EXTRA AYAHS IN EMDADIA (False Positives):")
    for s, a in sorted(list(missing_in_nasiha)):
        print(f"Sura {s}, Ayah {a}")
