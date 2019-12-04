import os
import cv2
import argparse
import json
import numpy as np
import sys


parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', dest='path',
                  required=True,
                  help='JSON data path?')
args = parser.parse_args()


if not os.path.exists(args.path):
    print("Path not found....")

files = os.listdir(args.path)

ilist = []

for f in files:
    if "img" in f:
        ilist.append(f)


for i,f in enumerate(ilist):
    tag = f.replace("img_","")
    
    imgsrc = os.path.join(args.path,"img_{}".format(tag))
    imgdest = os.path.join(args.path,"{}.png".format(i))

    geomsrc = os.path.join(args.path,"geom_{}".format(tag))
    geomdest = os.path.join(args.path,"{}_geom.png".format(i))

    os.rename(geomsrc,geomdest)
    os.rename(imgsrc,imgdest)
