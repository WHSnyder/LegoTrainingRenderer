import os
import cv2
import argparse
import json
import numpy as np
import sys

sys.path.append("/Users/will/projects/legoproj/")

import cvscripts
from cvscripts import feature_utils as fu

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', dest='path',required=True,help='JSON data path?')
parser.add_argument('-n', '--num', dest='num',required=True,type=int,help='File num?')
args = parser.parse_args()

with open(args.path) as json_file:
    data = json.load(json_file)

abspath = os.path.abspath(args.path)
abspath = abspath.replace(abspath.split("/")[-1],"")

huedict = {}

for obj in data["objects"]:
    hue = round(data["objects"][obj]["maskhue"],2)
    huedict[int(round(hue*180))] = obj

classes = ["WingR","WingL","Brick","Pole"]


def getClass(objname):
    for clss in classes:
        if clss in objname:
            return clss
    return None



#yes this is lazy
def findNearestHue(hue):

    hu = hue
    m = -1
    n = 1
    while hu not in huedict:
        hu+=n*m
        n+=1
        m*=-1 

    return huedict[hu]


def separate(maskpath):
    
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


i = args.num
    
imgname = "{}.png".format(i)
imgpath = os.path.join(abspath,imgname) 
maskpath = os.path.join(abspath,"mask_{}.png".format(i))

projmat = fu.matrix_from_string(data["projection"])

masks = separate(maskpath)
verts = []

for hue in masks:

    objname = findNearestHue(hue)
    objclass = getClass(objname)

    if objclass is not None:
        studs = fu.get_object_studs(objclass)
        for stud in studs:
            stud.append(1.0)
    else:
        continue

    modelmat = fu.matrix_from_string(data["objects"][objname]["modelmat"])
    viewmat = fu.matrix_from_string(data["viewmats"][i])

    screenverts = fu.toNDC(fu.verts_to_screen(modelmat, viewmat, projmat, studs), (512,512))

    screenverts = [vert for vert in screenverts if ((0 < vert[0] < 512) and (0<vert[1]<512))]
    verts += screenverts

img = cv2.imread(imgpath)

for vert in verts:
    cv2.circle(img, tuple(vert), 5, (200,50,50),3)

cv2.imshow("image",img)
cv2.waitKey(0)










