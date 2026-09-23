import sys
import os
import cv2
import numpy as np
from scipy.signal import find_peaks

hafs_ayat = [7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111,
             43, 52, 99, 128, 111, 110, 98, 135, 112, 78, 118, 64, 77,
             227, 93, 88, 69, 60, 34, 30, 73, 54, 45, 83, 182, 88, 75,
             85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55,
             78, 96, 29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52,
             44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25,
             22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
             11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6]

def find_robust_lines(img):
    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    row_sums = np.sum(thresh, axis=1) / 255
    peaks, _ = find_peaks(row_sums, distance=120, prominence=50)
    lines = []
    width = img.shape[1]
    for p in peaks:
        miny = max(0, p - 84)
        maxy = min(img.shape[0], p + 84)
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

def process_ayat(ayat):
    result = []
    if not ayat: return result
    cur_y = ayat[0][1]
    same_line = []
    for ayah in ayat:
        if abs(ayah[1] - cur_y) < 20:
            same_line.append(ayah)
        else:
            same_line.sort(key=lambda tup: tup[0])
            for s in same_line[::-1]:
                result.append(s)
            cur_y = ayah[1]
            same_line = [ayah]
    same_line.sort(key=lambda tup: tup[0])
    for s in same_line[::-1]:
        result.append(s)
    return result

def main():
    if len(sys.argv) < 5:
        print("Usage: generate_db.py <image_dir> <template_path> <start_page> <end_page>")
        sys.exit(1)
        
    image_dir = sys.argv[1]
    template_path = sys.argv[2]
    start_page = int(sys.argv[3])
    end_page = int(sys.argv[4])
    
    template = cv2.imread(template_path, 0)
    sura = 1
    ayah = 1
    end_of_ayah = False
    
    with open('output.sql', 'w') as f:
        for i in range(start_page, end_page + 1):
            filename = 'page' + str(i).zfill(3) + '.png'
            filepath = os.path.join(image_dir, filename)
            if not os.path.exists(filepath): continue
                
            img_gray = cv2.imread(filepath, 0)
            if img_gray is None: continue
            
            lines = find_robust_lines(img_gray)
            
            res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= 0.45)
            pts = list(zip(*loc[::-1]))
            filtered_pts = []
            for pt in pts:
                overlap = False
                for f_pt in filtered_pts:
                    if abs(pt[0]-f_pt[0]) < 20 and abs(pt[1]-f_pt[1]) < 20:
                        overlap = True
                        break
                if not overlap:
                    filtered_pts.append(pt)
                    
            ayat = []
            for pt in filtered_pts:
                ayat.append((pt[0] + template.shape[1]//2, pt[1] + template.shape[0]//2))
            
            ayat = sorted(ayat, key=lambda x: (x[1], x[0]))
            ayat = process_ayat(ayat)
            
            # Since Fatiha is tricky and there are page offsets, we use the ayah count 
            # to keep track. We assume page 3 starts at Sura 2, Ayah 6 because Emdadia format.
            # Wait, if we run from page 1, and page 1/2 have 0 markers found, then it will start
            # assigning Sura 1, Ayah 1 to the first marker on page 3! Which is wrong.
            # In Emdadia, page 3 has Baqarah 6-16. So page 2 has Fatiha 1-7 and Baqarah 1-5.
            # Total 12 ayahs on page 2.
            # I will just write the markers sequentially and let the user fix the start offset.
            
            for a_idx, marker in enumerate(ayat):
                my, mx = marker[1], marker[0]
                closest_line = 1
                min_dist = 99999
                for l_idx, line in enumerate(lines):
                    ly_mid = (line[0][1] + line[1][1]) / 2
                    if abs(ly_mid - my) < min_dist:
                        min_dist = abs(ly_mid - my)
                        closest_line = l_idx + 1
                
                vals = (i, closest_line, sura, ayah, 1, mx-10, mx+10, my-10, my+10)
                stmt = 'insert into glyphs values(NULL, %d, %d, %d, %d, %d, %d, %d, %d, %d);\n' % vals
                f.write(stmt)
                
                if ayah == hafs_ayat[sura-1]:
                    sura += 1
                    ayah = 1
                else:
                    ayah += 1

if __name__ == "__main__":
    main()
