import argparse
import itertools
import json
import os
import random
import sys
import time
import copy
import json

py = '/anaconda3/bin/python3.7'
cats_dir = '/Users/will/projects/legoproj/piecetypes/'
render_script = '/Users/will/projects/legoproj/keypointnet/tools/gen_tfrecords.py'
command = '{} ./keypointnet/tools/gen_tfrecords.py --input={} --output={}'

def getCategoryColor(category):

    attr_path = cats_dir + category + "/attrs.json"
    data = (0.1,0.1,0.1)

    with open(attr_path) as f:
        data = json.load(f)

    return data["color"]



def getPiecesOfCategory(category, tag):

	paths = os.listdir(cats_dir + category + "/pieces/")
	obj_paths = []

	if paths is not None:
		for path in paths:
			if ".DS" not in path:
				parts = path.split('/')
				newPath = cats_dir + category + "/pieces/" + path + '/renders' + tag
				
				if not os.path.exists(newPath):
					print("Input path not found")
					sys.exit()

				obj_paths.append(newPath)

	return obj_paths




parser = argparse.ArgumentParser()

parser.add_argument('-f', '--folder', dest='folder', nargs='*',
                  required=False, 
                  help='Obj file path?')

parser.add_argument('-c', '--piece', dest='piece', nargs='*',
				  required=False,
				  help='Category?')

parser.add_argument('-t', '--tag', dest='tag', required=True)


args = parser.parse_args()

paths = [];

if (args.folder):
	folder = args.folder[0]
	paths.append('/Users/will/projects/legoproj/' + folder)
elif (args.piece):
	for form in args.piece:
		forms = form.split('.')
		if (len(forms) == 1):
			paths = paths + getPiecesOfCategory(forms[0], args.tag)
		else:
			print("Just record a category for now...")
			sys.exit()

else:
	print("No pieces specified...")
	sys.exit()

for render_path in paths:

	if (not os.path.exists(render_path)):
	    print("Folder not found: " + render_path)
	    sys.exit()

	'''parts = render_path.split("/")
	piece_dir = render_path.replace(parts[-1], "")
	output_dir = piece_dir #"/records" + args.tag + ".tfrecord"
	'''
	print(render_path)
	if os.path.exists(render_path + "records" + args.tag):
		print("Tag already recorded...")
		sys.exit()

	os.system(command.format(py, render_path, render_path + ".tfrecord"))