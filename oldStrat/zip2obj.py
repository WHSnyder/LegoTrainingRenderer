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


for zip_path in args.file:

	filename = zip_path.split('/')[-1]
	piecename = filename.split('.')[0]


	dest_path = cats_dir + category + "pieces/"
	piece_path = dest_path + piecename
	new_zip_path = piece_path + "/" + filename;


	if (not os.path.exists(dest_path)):
		print("Category does not exist yet..")
		sys.exit()	

	os.system("unzip {} -d {}".format(zip_path, dest_path))

	stl_path = dest_path + piecename + '/*.stl' 
	obj_path = dest_path + piecename + "/" + piecename + ".obj"

	os.system("{} --background --python stl2obj.py -- {} {} {} {} {}".format(blend, stl_path, obj_path,r,g,b))










