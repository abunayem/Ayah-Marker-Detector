import cv2
import numpy as np

for p in range(3, 8):
    img = cv2.imread(f'D:\\Dev\\Temp\\EmdadiaPages\\page{p:03d}.png', cv2.IMREAD_GRAYSCALE)
    if img is None: continue
    
    # Pre-processing to improve circle detection
    # Ayah markers are distinct. Let's blur slightly.
    blurred = cv2.medianBlur(img, 5)
    
    # minDist: Minimum distance between the centers of the detected circles.
    # param1: Upper threshold for the internal Canny edge detector.
    # param2: Threshold for center detection.
    # minRadius, maxRadius: Min and max radius of the circles.
    
    # The markers had radius ~30 to 40.
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                               param1=50, param2=25, minRadius=20, maxRadius=45)
                               
    if circles is not None:
        print(f"Page {p:03d}: found {len(circles[0])} circles")
    else:
        print(f"Page {p:03d}: found 0 circles")
