#!/usr/bin/env python3

import datetime
import json
import os
import re
import fnmatch
from PIL import Image
import numpy as np
from pycococreatortools import pycococreatortools
import argparse
import sys



parser = argparse.ArgumentParser()

parser.add_argument('-m', '--mode', dest='mode', 
                  required=True, 
                  help='test, train, or val?')
args = parser.parse_args()

mode = args.mode

if not (mode == 'test' or mode == 'val' or mode == 'train'):
	print("Invalid mode supplied...")
	sys.exit()









ROOT_DIR = './'
IMAGE_DIR = os.path.join(ROOT_DIR, "data_oneofeach/{}_oneofeach/".format(mode))
ANNOTATION_DIR = os.path.join(ROOT_DIR, "annotations")

INFO = {
    "description": "One-of-each Dataset",
    "url": "https://github.com/waspinator/pycococreator",
    "version": "0.1.0",
    "year": 2019,
    "contributor": "parasite",
    "date_created": datetime.datetime.utcnow().isoformat(' ')
}

LICENSES = [
    {
        "id": 1,
        "name": "Attribution-NonCommercial-ShareAlike License",
        "url": "http://creativecommons.org/licenses/by-nc-sa/2.0/"
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
]


def getAttrs(filename):
    parts = filename.split("_")
    piecetype = parts[2].split(".")[0]
    num = parts[0]
    
    return num, piecetype


def getNum(filename):
    return filename.split("_")[0]


def main():

    coco_output = {
        "info": INFO,
        "licenses": LICENSES,
        "categories": CATEGORIES,
        "images": [],
        "annotations": []
    }

    image_id = 1
    segmentation_id = 1


    filelist = sorted(os.listdir(ROOT_DIR + IMAGE_DIR), key=lambda s: s.casefold())
    numfiles = len(filelist)

    #print(filelist)

    go = True

    i = 0
    j = 0
    k = 0
    while go:

        k = i + j

        if k >= numfiles:
            break

        curfile = filelist[k]

        print("On image: {}".format(curfile) + "\n====================================================")

        image = Image.open(ROOT_DIR + IMAGE_DIR + curfile)

        image_info = pycococreatortools.create_image_info(i, os.path.basename(ROOT_DIR + IMAGE_DIR + curfile), image.size)
        coco_output["images"].append(image_info)

        go = True
        i += 1

        curnum = getNum(curfile)


        while go:

            if i + j >= numfiles:
                break
            
            nextfile = filelist[i + j]
            nextnum, nextype = getAttrs(nextfile)

            if nextnum != curnum:
                break

            print("\tOn annotation: {}".format(nextfile))

            j += 1

            class_id = [x['id'] for x in CATEGORIES if x['name'] == nextype][0]

            category_info = {'id': class_id, 'is_crowd': False}

            binary_mask = np.asarray(Image.open(ROOT_DIR + IMAGE_DIR + nextfile).convert('1')).astype(np.uint8)
            
            annotation_info = pycococreatortools.create_annotation_info(
                j, i-1, category_info, binary_mask,
                image.size, tolerance=2)

            if annotation_info is not None:
                coco_output["annotations"].append(annotation_info)
        print("===================================================")

        if i+j >= numfiles:
            break

    print("Loaded {} images, {} annotations...".format(i,j))


    with open('{}/{}.json'.format(ROOT_DIR, mode), 'w') as output_json_file:
        json.dump(coco_output, output_json_file)


if __name__ == "__main__":
    main()