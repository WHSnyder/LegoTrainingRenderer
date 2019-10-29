from __future__ import print_function

import argparse
import itertools
import json
from math import pi
import os
import random
import sys
import time
import copy
import json

cats_dir = '/Users/will/projects/legoproj/piecetypes/'
blend = '/Applications/Blender/blender.app/Contents/MacOS/blender'


def getCategoryColor(category):

    attr_path = cats_dir + category + "attrs.json"
    data = (0.1,0.1,0.1)

    with open(attr_path) as f:
        data = json.load(f)

    return data["color"]




parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', dest='file', nargs='*',
				  required=True, 
				  help='Zip file path?')
parser.add_argument('-c', '--cat', dest='cat',
				  required=True,
				  help='Piece category?')
args = parser.parse_args()


category = args.cat + "/"

r,g,b = getCategoryColor(category)

dest_root = cats_dir + category + "pieces/"


if not os.path.exists(dest_root):
	print("Category root not found...")
	sys.exit()


for source_path in args.file:

	if not os.path.exists(source_path):
		print("Source STL not found...")
		sys.exit()

	filename = source_path.split('/')[-1]
	name_dims = filename.split("_")[-1].replace(".stl", "")

	dest_obj_path =  dest_root + name_dims + "/" + name_dims + ".obj";

	print("Source path: " + source_path)
	print("Dest obj path: " + dest_obj_path)

	if not os.path.exists(dest_root + name_dims):
		os.mkdir(dest_root + name_dims)

	os.system("{} --background --python stl2obj.py -- {} {} {} {} {} {}".format(blend, source_path, dest_obj_path,r,g,b,str(0.0)))