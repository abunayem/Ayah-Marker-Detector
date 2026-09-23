import cv2
import numpy as np
from scipy.signal import find_peaks

def find_robust_lines(img):
    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    row_sums = np.sum(thresh, axis=1) / 255
    peaks, _ = find_peaks(row_sums, distance=120, prominence=50)
    lines = []
    for p in peaks:
        miny = max(0, int(p) - 84)
        maxy = min(img.shape[0], int(p) + 84)
        line_band = thresh[miny:maxy, :]
        col_sums = np.sum(line_band, axis=0)
        non_zero_cols = np.nonzero(col_sums)[0]
        if len(non_zero_cols) > 0:
            minx = non_zero_cols[0]
            maxx = non_zero_cols[-1]
        else:
            minx = 0; maxx = img.shape[1]
        lines.append(((minx, miny), (maxx, maxy)))
    return lines

for p in range(3, 10):
    img = cv2.imread(f'D:\\Dev\\Temp\\EmdadiaPages\\page{p:03d}.png', cv2.IMREAD_GRAYSCALE)
    if img is None: continue
    lines = find_robust_lines(img)
    
    global_min_x = min([l[0][0] for l in lines])
    global_max_x = max([l[1][0] for l in lines])
    
    blurred = cv2.medianBlur(img, 5)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                               param1=50, param2=25, minRadius=20, maxRadius=45)
                               
    if circles is not None:
        valid_circles = []
        for c in circles[0]:
            cx, cy, r = c
            # Only keep circles inside the main text block (ignoring margins)
            if global_min_x - 10 <= cx <= global_max_x + 10:
                valid_circles.append(c)
        print(f"Page {p:03d}: found {len(valid_circles)} valid circles (out of {len(circles[0])})")
