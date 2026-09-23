import cv2
import numpy as np

img = cv2.imread(r'D:\Dev\Temp\EmdadiaPages\page003.png', cv2.IMREAD_GRAYSCALE)

for i in range(5):
    template = cv2.imread(f'template_candidate_{i}.png', 0)
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    
    # Try different thresholds
    for thresh in [0.5, 0.6, 0.7, 0.8]:
        loc = np.where(res >= thresh)
        pts = list(zip(*loc[::-1]))
        
        # filter overlapping points
        filtered_pts = []
        for pt in pts:
            overlap = False
            for f_pt in filtered_pts:
                if abs(pt[0]-f_pt[0]) < 20 and abs(pt[1]-f_pt[1]) < 20:
                    overlap = True
                    break
            if not overlap:
                filtered_pts.append(pt)
        
        print(f"Candidate {i} with threshold {thresh}: {len(filtered_pts)} matches")
