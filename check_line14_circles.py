import cv2
import numpy as np

img = cv2.imread(r'D:\Dev\Workspace\Python\Ayah Marker Detector\crop_p601_line14.png', cv2.IMREAD_GRAYSCALE)
w = 1700 # page width
blurred = cv2.medianBlur(img, 5)
circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                           param1=50, param2=25, minRadius=20, maxRadius=45)

if circles is not None:
    for c in circles[0]:
        print(f"cx={c[0]:.1f} ({c[0]/w:.3f}), cy={c[1]:.1f}, r={c[2]:.1f}")
