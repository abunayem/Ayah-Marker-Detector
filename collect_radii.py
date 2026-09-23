import cv2
import numpy as np
import os
from collections import Counter

radii = []
for p in range(3, 50):
    img = cv2.imread(f'D:\\Dev\\Temp\\EmdadiaPages\\page{p:03d}.png', cv2.IMREAD_GRAYSCALE)
    if img is None: continue
    blurred = cv2.medianBlur(img, 5)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                               param1=50, param2=25, minRadius=15, maxRadius=55)
    if circles is not None:
        for c in circles[0]:
            radii.append(int(c[2]))

c = Counter(radii)
for r, count in sorted(c.items()):
    print(f"Radius {r}: {count} circles")
