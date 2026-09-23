import cv2
import numpy as np

def test_pages():
    for p in range(3, 10):
        img = cv2.imread(f'D:\\Dev\\Temp\\EmdadiaPages\\page{p:03d}.png', cv2.IMREAD_GRAYSCALE)
        if img is None: continue
        blurred = cv2.medianBlur(img, 5)
        circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                                   param1=50, param2=25, minRadius=20, maxRadius=45)
        count = len(circles[0]) if circles is not None else 0
        print(f"Page {p:03d}: found {count} circles")

if __name__ == '__main__':
    test_pages()
