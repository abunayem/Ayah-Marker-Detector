import cv2
import numpy as np
from scipy.signal import find_peaks

def find_robust_lines(filepath):
    img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)
    row_sums = np.sum(thresh, axis=1) / 255
    # distance=100 ensures we don't get multiple peaks for the same line
    # prominence=100 filters out noise
    peaks, _ = find_peaks(row_sums, distance=120, prominence=50)
    
    lines = []
    width = img.shape[1]
    
    for p in peaks:
        miny = max(0, p - 84)
        maxy = min(img.shape[0], p + 84)
        
        # find minx and maxx
        line_band = thresh[miny:maxy, :]
        col_sums = np.sum(line_band, axis=0)
        non_zero_cols = np.nonzero(col_sums)[0]
        if len(non_zero_cols) > 0:
            minx = non_zero_cols[0]
            maxx = non_zero_cols[-1]
        else:
            minx = 0
            maxx = width
            
        lines.append(((minx, miny), (maxx, maxy)))
        
    return lines

if __name__ == '__main__':
    for p in [1, 2, 3]:
        lines = find_robust_lines(f'D:\\Dev\\Temp\\EmdadiaPages\\page{p:03d}.png')
        print(f"Page {p} has {len(lines)} lines")
