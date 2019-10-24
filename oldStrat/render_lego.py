import argparse
import itertools
import json
import os
import random
import sys
import time
import copy
import json


cats_dir = '/Users/will/projects/legoproj/piecetypes/'
blend = '/Applications/Blender/blender.app/Contents/MacOS/blender'
render_script = '/Users/will/projects/legoproj/keypointnet/tools/render.py'


def getCategoryColor(category):

    attr_path = cats_dir + category + "/attrs.json"
    data = (0.1,0.1,0.1)

    with open(attr_path) as f:
        data = json.load(f)

    return data["color"]



def getPiecesOfCategory(category):

	paths = os.listdir(cats_dir + category + "/pieces/")
	obj_paths = []

	if paths is not None:
		for path in paths:
			if ".DS" not in path:
				parts = path.split('/')
				newPath = cats_dir + category + "/pieces/" + path + '/' + parts[-1] + ".obj"
				obj_paths.append(newPath)

	return obj_paths






command = '{} -b --python {} -- -m {} -o {} -s 128 -n {} -fov 5 -c {} {} {} --roll'


parser = argparse.ArgumentParser()

parser.add_argument('-f', '--file', dest='file', nargs='*',
                  required=False, 
                  help='Obj file path?')

parser.add_argument('-c', '--cat', dest='piece', nargs='*',
				  required=False,
				  help='Piece code?')

parser.add_argument('-n', '--num', dest='num', required=False, default=1200, type=int)

parser.add_argument('-t', '--tag', dest='tag', required=True)


args = parser.parse_args()

paths = [];

if (args.file):
	paths.append(args.file[0])
elif (args.piece):
	for form in args.piece:
		forms = form.split('.')
		if (len(forms) == 1):
			paths = paths + getPiecesOfCategory(forms[0])
		else:
			print("Just render a category for now...")
			sys.exit()

else:
	print("No pieces specified...")
	sys.exit()

for obj_path in paths:

	if (not os.path.exists(obj_path)):
	    print("Obj file not found: " + obj_path)
	    sys.exit()


	parts = obj_path.split("/")

	piece_dir = obj_path.replace(parts[-1], "")
	category = parts[-4]

	'''
	count = 0
	for content in os.listdir(piece_dir):
	    if ("renders" in content):
	        tag = int(content[-1])
	        if (tag >= count):
	            count = tag + 1
	'''

	output_dir = piece_dir + "renders" + args.tag

	if not os.path.exists(output_dir):
		os.mkdir(output_dir)
		print("Tag already used...")
		#sys.exit()


	color = getCategoryColor(category)
	#print(color)


	
	os.system(command.format(blend, render_script, obj_path, output_dir, args.num, color[0], color[1], color[2]))
