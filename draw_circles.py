import cv2
import numpy as np
import os

for p in [1, 2, 3]:
    img_path = f'D:\\Dev\\Temp\\EmdadiaPages\\page{p:03d}.png'
    img = cv2.imread(img_path)
    if img is None: continue
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, 5)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                               param1=50, param2=25, minRadius=20, maxRadius=45)
                               
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            # draw the outer circle
            cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), 3)
            
    # resize to reasonable size for viewing
    img = cv2.resize(img, (0,0), fx=0.3, fy=0.3)
    out_path = f'C:\\Users\\abuna\\.gemini\\antigravity\\brain\\ecf660fd-5f86-443c-8de2-7bce1c816349\\page_annotated_{p:03d}.png'
    cv2.imwrite(out_path, img)
