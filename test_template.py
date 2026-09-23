import cv2
import numpy as np

img = cv2.imread(r'D:\Dev\Temp\EmdadiaPages\page609.png', cv2.IMREAD_GRAYSCALE)
template = cv2.imread('template.png', cv2.IMREAD_GRAYSCALE)

res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
threshold = 0.55
loc = np.where(res >= threshold)

# group close matches
points = []
for pt in zip(*loc[::-1]):
    matched = False
    for p in points:
        if abs(p[0] - pt[0]) < 20 and abs(p[1] - pt[1]) < 20:
            matched = True
            break
    if not matched:
        points.append(pt)

print(f"Found {len(points)} markers using threshold {threshold}")
