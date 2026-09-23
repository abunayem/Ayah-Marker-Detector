from PIL import Image
import sys
sys.path.append('ayah-detection')
from lines.lines import find_lines

for p in [1,2,3]:
    img = Image.open(f'D:\\Dev\\Temp\\EmdadiaPages\\page{p:03d}.png').convert('RGBA')
    lines = find_lines(img, 168, 35, 0)
    print(f"Page {p} has {len(lines)} lines")
