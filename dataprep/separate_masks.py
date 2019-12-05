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

newdata = []

with open(args.path) as json_file:
        data = json.load(json_file)

abspath = os.path.abspath(args.path)
abspath = abspath.replace(abspath.split("/")[-1],"")

write_path = os.path.join(abspath,"masks")

if not os.path.exists(write_path):
    os.mkdir(write_path)
#else:
#    os.system("rm {}".format(os.path.join(write_path,"*")))


class_counts = {"Engine":0,"Wing":0,"Brick":0,"Pole":0}


def getObjFromHue(hue):
    hue = int(round(hue/5))
    return data["ids"][str(hue)]



def separate(imgpath,maskpath):
    
    img = cv2.imread(imgpath)
    mask = cv2.imread(maskpath)

    kernel = np.ones((2,2), np.uint8) 
    maskdict = {}

    hsvmask = cv2.cvtColor(mask,cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsvmask],[0],None,[180],[0,179])
    
    hues=[]
    for j,e in enumerate(hist):
        if e[0] > 500:
            hues.append(j)

    for hue in hues:

        threshed = cv2.inRange(hsvmask, (hue-1,0,100), (hue+1,255,255))
        threshed = cv2.medianBlur(threshed.astype(np.uint8), 3)
        threshed = cv2.dilate(threshed, kernel, iterations=1)

        if np.sum(threshed) <= 255*100:
            continue;

        maskdict[hue] = threshed

    return maskdict


count = 0
links = {}


for i in range(data["runs"]):
    
    print(i)

    tag = "{:0>4}".format(i)
    
    imgname = "{}_a.png".format(tag)
    imgpath = os.path.join(abspath,imgname) 
    maskpath = os.path.join(abspath,"{}_masks.png".format(tag))
    
    masks = separate(imgpath,maskpath)

    if masks: 
        links[imgname] = []
    else:
        continue

    for j,hue in enumerate(masks):

        objname = getObjFromHue(hue)
        objclass = data["objects"][objname]["class"]

        maskname = "{}_{}_{}_mask.png".format(tag,j,objclass)
        links[imgname].append({"class":objclass,"file":maskname})

        wmask = os.path.join(write_path,maskname)
        cv2.imwrite(wmask,masks[hue])


dumppath = os.path.join(abspath,"dset_withmasks.json")

with open(dumppath, 'w') as fp:
    json.dump(links,fp)
