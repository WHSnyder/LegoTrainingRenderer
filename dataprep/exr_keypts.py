import os
import cv2
import argparse
import json
import numpy as np
import sys
import multiprocessing as mp
from multiprocessing import Process
import random

random.seed()

sys.path.append("/home/will/projects/legoproj")


import cvscripts
from cvscripts import feature_utils as fu

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', dest='path',required=True,help='JSON data path?')
parser.add_argument('-n', '--num', dest='num',required=False,type=int,help='File num?')
args = parser.parse_args()

with open(args.path) as json_file:
    data = json.load(json_file)

abspath = os.path.abspath(args.path)
abspath = abspath.replace(abspath.split("/")[-1],"")

classes = ["WingR","WingL","Brick","Pole"]


def getClass(objname):
    for clss in classes:
        if clss in objname:
            return clss
    return None


def getObjFromHue(hue):
    hue = int(round(hue/5))
    name = data["ids"][str(hue)]

    if ("Pole" in name):
        return name
    return None


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


def overlay(i):

    print(i)
    
    imgname = "{}.png".format(i)
    imgpath = os.path.join(abspath,imgname) 
    maskpath = os.path.join(abspath,"mask_{}.png".format(i))

    depthpath = os.path.join(abspath,"depth_{}.npy".format(i))
    depthmap = np.load(depthpath,allow_pickle=False)

    projmat = fu.matrix_from_string(data["projection"])

    studmask = np.zeros((512,512),dtype=np.uint8)
    image = cv2.imread(imgpath)

    masks = separate(maskpath)
    verts = []
    p=False

    for hue in masks:

        objname = getObjFromHue(hue)
        
        if objname:
            objclass = objname.split(".")[0]
            studs = fu.get_object_studs(objclass)
            for stud in studs:
                stud.append(1.0)
        else:
            continue
        
        studs = np.array(studs,dtype=np.float32)

        modelmat = fu.matrix_from_string(data["objects"][objname]["modelmat"])
        viewmat = fu.matrix_from_string(data["viewmats"][i])

        screenverts = fu.verts_to_screen(modelmat, viewmat, projmat, studs)

        if screenverts.size == 0:
            continue

        screenverts[:,0:2] = fu.toNDC(screenverts[:,0:2], (512,512))
        visibleverts = [v for v in screenverts if depthmap[int(v[1]),int(v[0])] - abs(v[2]) > -0.05]
            
        if visibleverts:
            for v in visibleverts:
                circle_rad = fu.get_circle_length(modelmat,viewmat,projmat,studs[int(v[3])])
                x=int(v[0])
                y=int(v[1])
                cv2.circle(studmask, (x,y), circle_rad, (255,20,20),-1)
            cv2.bitwise_and(masks[hue],masks[hue],mask=masks[hue])


<<<<<<< HEAD
    print(abspath)
=======
>>>>>>> 8e92a49fa39e4fb5bc3a1073b1e27f0757ecd654
    cv2.imwrite(os.path.join(abspath,"studs_{}.png".format(i)),studmask)


def iterOverlay(indices):
    for ind in indices:
        overlay(ind)


indices = np.arange(data["runs"]) if args.num is None else [args.num] 
<<<<<<< HEAD
print(indices)
cores = mp.cpu_count()
num_procs = 1 if len(indices) < cores else cores
indices_lists = np.array_split(indices, num_procs)
print(indices_lists)

processes = []
'''
=======
cores = mp.cpu_count()
num_procs = 1 if len(indices) < cores else cores
indices_lists = np.array_split(indices, num_procs)

processes = []

>>>>>>> 8e92a49fa39e4fb5bc3a1073b1e27f0757ecd654
for ilist in indices_lists:
    processes.append( Process(target=iterOverlay, args=(ilist,)) )

for process in processes:
    process.start()

for process in processes:
<<<<<<< HEAD
    process.join()
'''
iterOverlay(indices)
=======
    process.join()
>>>>>>> 8e92a49fa39e4fb5bc3a1073b1e27f0757ecd654
