import sqlite3
import cv2
import numpy as np
import os

# Load a clean template of the Ayah circle from page 609 (Sura 112, Ayah 1)
# We need to crop a template.
# Let's write a script to just find the bounding box of a marker in the DB and crop it!
