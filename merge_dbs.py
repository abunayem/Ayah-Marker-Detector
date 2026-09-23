import sqlite3
import glob
import os

def merge_dbs():
    if os.path.exists('ayahinfo_emdadia_final.db'):
        os.remove('ayahinfo_emdadia_final.db')
        
    conn_out = sqlite3.connect('ayahinfo_emdadia_final.db')
    cursor_out = conn_out.cursor()
    cursor_out.execute('''
    CREATE TABLE glyphs (
        glyph_id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_number INTEGER,
        line_number INTEGER,
        sura_number INTEGER,
        ayah_number INTEGER,
        position INTEGER,
        min_x INTEGER,
        max_x INTEGER,
        min_y INTEGER,
        max_y INTEGER
    );
    ''')
    
    # Get all chunk databases and sort them by the starting page number
    db_files = glob.glob('chunk_*_to_*.db')
    db_files.sort(key=lambda x: int(x.split('_')[1]))
    
    total_records = 0
    
    for db_file in db_files:
        print(f"Merging {db_file}...")
        conn_in = sqlite3.connect(db_file)
        cursor_in = conn_in.cursor()
        
        cursor_in.execute("SELECT page_number, line_number, sura_number, ayah_number, position, min_x, max_x, min_y, max_y FROM glyphs")
        rows = cursor_in.fetchall()
        
        cursor_out.executemany('''
            INSERT INTO glyphs (page_number, line_number, sura_number, ayah_number, position, min_x, max_x, min_y, max_y)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rows)
        
        total_records += len(rows)
        conn_in.close()
        
    conn_out.commit()
    conn_out.close()
    
    print(f"\nSuccessfully merged {len(db_files)} chunks into ayahinfo_emdadia_final.db")
    print(f"Total Ayahs imported: {total_records}")

if __name__ == '__main__':
    merge_dbs()
