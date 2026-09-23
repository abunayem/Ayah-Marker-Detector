import cv2
import numpy as np
template = cv2.imread('template.png', 0)
for p in range(3, 8):
    img = cv2.imread(f'D:\\Dev\\Temp\\EmdadiaPages\\page{p:03d}.png', 0)
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
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
    print(f'Page {p:03d} matches: {len(filtered_pts)}')
