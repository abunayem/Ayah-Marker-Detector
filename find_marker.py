import cv2
import numpy as np

img = cv2.imread(r'D:\Dev\Temp\EmdadiaPages\page003.png', cv2.IMREAD_GRAYSCALE)
if img is None:
    print("Image not found")
    exit(1)

# Blur the image to reduce noise
img = cv2.medianBlur(img, 5)

circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 50,
                           param1=50, param2=30, minRadius=20, maxRadius=60)

if circles is not None:
    circles = np.uint16(np.around(circles))
    print(f"Found {len(circles[0])} circles")
    # Save the first circle as template
    for i, i_circle in enumerate(circles[0, :5]):
        x, y, r = i_circle[0], i_circle[1], i_circle[2]
        # Crop the bounding box of the circle
        roi = img[max(0, y-r-5):y+r+5, max(0, x-r-5):x+r+5]
        cv2.imwrite(f'template_candidate_{i}.png', roi)
        print(f"Saved template_candidate_{i}.png with radius {r}")
else:
    print("No circles found")
