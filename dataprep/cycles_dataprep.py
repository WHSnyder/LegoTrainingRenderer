#!/usr/bin/env python3

import datetime
import json
import os
import re
import fnmatch
from PIL import Image
import numpy as np
from pycocotools import pycococreatortools
import argparse
import sys
import imgaug
from imgaug import augmenters as iaa
import random
import numpy as np
import time

seconds = int(time.time() % 60)
random.seed(seconds)

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--paths', dest='paths', nargs='+', required=True, help='JSON dset paths?')
parser.add_argument('-a', '--aug', dest='aug', action='store_true', help='Augment the data or not?', required=False)
parser.add_argument('-t', '--tag', dest='tag', action='store_true', help='Dset name?', required=True)
args = parser.parse_args()

INFO = {
    "description": "",
    "url": "",
    "version": "0.1.0",
    "year": 2019,
    "contributor": "parasite",
    "date_created": datetime.datetime.utcnow().isoformat(' ')
}
LICENSES = [
    {
        "id": 1,
        "name": "",
        "url": ""
    }
]
CATEGORIES = [
    {
        'id': 1,
        'name': 'Wing',
        'supercategory': 'Piece',
    },
    {
        'id': 2,
        'name': 'Brick',
        'supercategory': 'Piece',
    },
    {
        'id': 3,
        'name': 'Pole',
        'supercategory': 'Piece',
    },
    {
        'id': 4,
        'name': 'Engine',
        'supercategory': 'Piece',
    }
]

coco_output = {
    "info": INFO,
    "licenses": LICENSES,
    "categories": CATEGORIES,
    "images": [],
    "annotations": []
}

'''
seq = iaa.Sequential([
    iaa.GaussianBlur(sigma=(0, 4.0)),
    iaa.Sometimes(.7, iaa.Multiply((0.7, 1.3), per_channel=0.7)),
    #iaa.Add(per_channel=True, value=(random.randint(-40,40),random.randint(-40,40))),
    iaa.Sometimes(.8, iaa.AdditivePoissonNoise(lam=random.randint(19,32))),
    iaa.Sometimes(.3, iaa.GammaContrast(gamma=.5)),
    iaa.Sometimes(.5, iaa.GammaContrast(gamma=1.75))
])


def gimme():
    return False if random.randint(0,2) == 0 else True

def getClassAndNum(filename):
    parts = filename.split("_")
    num = int(parts[-1].split(".")[0])
    piecetype = parts[-2]
    return num, piecetype

def getNum(filename):
    return int(filename.split("_")[0])
'''


#mode 0 is normal aug, mode 1 is shadows, mode 2 is stud noise, mode 3 is simplex
'''
def runAug(img, filenum, augmode):

    filename = None

    if seq is not None and augmode == 0:

        img = np.reshape(np.array(img)[:,:,0:3],(1,512,512,3))
        img = Image.fromarray(np.reshape(seq(images=img), (512,512,3)))
        filename =  "{}_{}_b.png".format(filenum, mode)
        filepath = ROOT_DIR + IMAGE_DIR + filename
        img.save(filepath)

    return filename,img
'''

for path in args.paths
    if not os.path.exists(path):
        print("JSON file not found at {}".format(path))
        sys.exit()





i = j = 0

for path in args.paths:

	with open(path) as json_file:
    	data = json.load(json_file)

    	abspath = os.path.abspath(path)
    	imagedir = abspath.replace(abspath.split("/")[-1],"")
    	masksdir = os.path.join(imagedir,"masks")

		for imgfile,masks in data.items():

		    print("Img {}".format(i))

		    continue if not masks

		    imagepath = os.path.join(imagedir,imgfile)
		    image = Image.open(imagepath)

		    image_info = pycococreatortools.create_image_info(i, imagepath, image.size)
		    coco_output["images"].append(image_info)

		    
		    #for jindex in masks:
		    for mask in masks:
		        
		        maskclass = mask["class"]
		        maskname = mask["file"]
		        maskpath = os.path.join(masksdir,maskname)

		        print("\tAnno {} of class: {}".format(j, maskclass))

		        class_id = [x['id'] for x in CATEGORIES if x['name'] == maskclass][0]
		        category_info = {'id': class_id, 'is_crowd': False}

		        binary_mask = np.asarray(Image.open(maskpath).convert('1')).astype(np.uint8)
		        
		        annotation_info = pycococreatortools.create_annotation_info(
		            j, i, category_info, binary_mask,
		            image.size, tolerance=2)

		        if annotation_info is not None:
		            coco_output["annotations"].append(annotation_info)
		            j += 1

		    i+=1


with open('{}.json'.format(args.tag), 'w') as output_json_file:
    json.dump(coco_output, output_json_file)