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



def getPiecesOfCategory(category, tag):

	pieces = cats_dir + category + "/pieces/"

	paths = os.listdir(pieces)
	obj_paths = []

	if paths is not None:
		for path in paths:
			if ".DS" not in path:
				newPath = pieces + path# + 
				
				if not os.path.exists(newPath):
					print("Input path not found")
					sys.exit()

				obj_paths.append(newPath)

	return obj_paths




parser = argparse.ArgumentParser()

'''
parser.add_argument('-f', '--folder', dest='folder', nargs='*',
                  required=False, 
                  help='Obj file path?')
'''

parser.add_argument('-c', '--cat', dest='cat',
				  required=True,
				  help='Category?')

parser.add_argument('-t', '--tag', dest='tag', required=True)


parser.add_argument("--dev", dest="dev", required=False, action='store_true')
parser.add_argument("--test", dest="test", required=False, action='store_true')
parser.add_argument("--train", dest="train", required=False, action='store_true')



args = parser.parse_args()

paths = [];

if (not args.train and not args.test and not args.dev):
	print("Train or test?")
	sys.exit()



'''
if (args.folder):
	folder = args.folder[0]
	paths.append('/Users/will/projects/legoproj/' + folder)
el'''

#piecetype = args.cat.split(".")[0]





paths = paths + getPiecesOfCategory(args.cat, args.tag)





output_path = '/Users/will/projects/legoproj/piecetypes/' + args.cat + "/records/"  


writestring = ""

for record_path in paths:
	'''
	if (not os.path.exists(record_path)):
	    print("Path not found: " + record_path)
	    sys.exit()


	if os.path.exists(record_path + "renders" + args.tag + ):
		print("Tag already recorded...")
		sys.exit()
	'''

	piece_name = record_path.split("/")[-1]


	tail = "/renders" + args.tag + ".tfrecord"

	record_path = record_path + tail
	out_path = output_path + piece_name + args.tag + ".tfrecord"

	writestring = writestring + (piece_name + args.tag) + "\n"


	#print("Source path: " + record_path)
	#print("Output path: " + out_path)# + (piece_name + tail.replace("/","")).replace(".tfrecord",""))
	
	os.system("cp {} {}".format(record_path, out_path))


dest = "test"
if args.dev:
	dest = "dev"

if not args.train:
	cmd = "echo \'{}\' > {}{}.txt".format(writestring[0:-1],output_path, dest)
	os.system(cmd)