from PIL import Image
import sys
sys.path.append('ayah-detection')
from lines.lines import find_lines
img = Image.open(r'D:\Dev\Temp\EmdadiaPages\page003').convert('RGBA')
lines = find_lines(img, 110, 35, 0)
print(f"Found {len(lines)} lines")
