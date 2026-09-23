import os
import subprocess

def run_chunk(start_page, end_page, start_sura, start_ayah, param1=50, param2=25, min_r=20, max_r=45):
    db_name = f"chunk_{start_page}_to_{end_page}.db"
    cmd = [
        r".\env\Scripts\python.exe", "generate_imdadia_db.py",
        "--img_dir", r"D:\Dev\Temp\EmdadiaPages",
        "--out_db", db_name,
        "--start_page", str(start_page),
        "--end_page", str(end_page),
        "--start_sura", str(start_sura),
        "--start_ayah", str(start_ayah),
        "--param1", str(param1),
        "--param2", str(param2),
        "--min_r", str(min_r),
        "--max_r", str(max_r),
        "--skip_pages", "" # Don't skip any pages inside chunks by default
    ]
    
    print(f"\n--- Running Pages {start_page} to {end_page} ---")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse the output to find where it ended
    out_lines = result.stdout.split('\n')
    last_sura, last_ayah = None, None
    error = None
    
    if result.returncode != 0:
        error = result.stderr or result.stdout
    else:
        for line in reversed(out_lines):
            if "Next is Sura" in line:
                # Format: Page 022: Processed 14 Ayahs. Next is Sura 2, Ayah 142
                parts = line.split("Next is Sura ")[1].split(", Ayah ")
                last_sura = int(parts[0])
                last_ayah = int(parts[1])
                break
                
    return db_name, last_sura, last_ayah, error, result.stdout

def main():
    print("Welcome to the Interactive Chunk Runner!")
    start_page = 3
    end_page = 22
    start_sura = 2
    start_ayah = 6
    
    param2 = 25
    min_r = 20
    
    while start_page <= 611:
        actual_end = min(start_page + 19, 611)
        db_name, next_sura, next_ayah, error, stdout = run_chunk(start_page, actual_end, start_sura, start_ayah, param2=param2, min_r=min_r)
        
        if error:
            print(f"ERROR OCCURRED in this chunk (Pages {start_page}-{actual_end}):")
            print(error)
            print("\nWhat would you like to do?")
            print("1. Retry with stricter parameters (less false positives)")
            print("2. Retry with looser parameters (catch missing markers)")
            print("3. Quit")
            choice = input("Choice: ")
            if choice == '1':
                param2 += 5
                min_r += 2
                print(f"-> Changed param2 to {param2}, min_r to {min_r}")
            elif choice == '2':
                param2 -= 5
                min_r -= 2
                print(f"-> Changed param2 to {param2}, min_r to {min_r}")
            else:
                break
        else:
            print(f"\nSUCCESS! Chunk {start_page}-{actual_end} completed.")
            print(f"The next chunk will start at: Sura {next_sura}, Ayah {next_ayah}")
            print("\nOptions:")
            print("Press ENTER to accept and process the next 20 pages.")
            print("Type 'retry' to re-run this chunk with different parameters.")
            print("Type 'quit' to exit.")
            
            choice = input("Choice: ").strip().lower()
            
            if choice == 'retry':
                print("Enter new param2 (current: {}):".format(param2))
                try: param2 = int(input() or param2)
                except: pass
                print("Enter new min_r (current: {}):".format(min_r))
                try: min_r = int(input() or min_r)
                except: pass
            elif choice == 'quit':
                break
            else:
                # Proceed to next chunk
                start_page = actual_end + 1
                start_sura = next_sura
                start_ayah = next_ayah
                
if __name__ == '__main__':
    main()
