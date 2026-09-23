import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

img = cv2.imread(r'D:\Dev\Temp\EmdadiaPages\page003', cv2.IMREAD_GRAYSCALE)
if img is None:
    print("Could not read image")
    exit(1)
_, thresh = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY_INV)

row_sums = np.sum(thresh, axis=1) / 255
plt.plot(row_sums)
plt.savefig('row_sums.png')
print("Non-zero rows:", np.count_nonzero(row_sums))

peaks, _ = find_peaks(row_sums, distance=100)
print(f"Found {len(peaks)} lines")
if len(peaks) > 1:
    diffs = np.diff(peaks)
    print(f"Average line height: {np.mean(diffs)}")
