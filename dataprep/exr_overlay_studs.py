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

sys.path.append("/home/will/projects/legoproj/")

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
    #if ("Engine" in name) or ("Pole" in name):
    #    return None
    return name


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


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def overlay(i):

    #print(i)

    imgname = "{}.png".format(i)
    imgpath = os.path.join(abspath,imgname) 
    maskpath = os.path.join(abspath,"mask_{}.png".format(i))

    depthpath = os.path.join(abspath,"depth_{}.npy".format(i))
    depthmap = np.load(depthpath,allow_pickle=True)

    projmat = fu.matrix_from_string(data["projection"])

    masks = separate(maskpath)
    verts = []

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

        screenverts[:,0:2] = fu.toNDC(screenverts[:,0:2], (512,512)).astype(np.int_)
        #print(screenverts)

        visibleverts = [v for v in screenverts if depthmap[int(v[0]),int(v[1])] < abs(v[2])]

        if len(visibleverts) > 0 and i == 65:
            v = random.choice(visibleverts)
            d = v[2]
            print(depthmap)
            #near = find_nearest(np.absolute(depthmap),d)
            #dtrue = depthmap[int(v[0]),int(v[1])]
            #print("Depthmap value {}, cam dist {}".format(dtrue,d))
            
        verts += visibleverts

    img = cv2.imread(imgpath)

    for vert in verts:
        cv2.circle(img, tuple(vert[0:2].astype(np.int_)), 5, (200,50,50),3)

    cv2.imwrite(os.path.join(abspath,"studs_{}.png".format(i)),img)



def iterOverlay(indices):
    for ind in indices:
        overlay(ind)
        #print(ind)



runs = np.arange(data["runs"]) if args.num is None else [args.num] 
cores = mp.cpu_count()
num_procs = 1 if len(runs) < cores else cores
indices = np.array_split( runs, num_procs )

processes = []

for ilist in indices:
    processes.append( Process(target=iterOverlay, args=(ilist,)) )

for process in processes:
    process.start()

for process in processes:
    process.join()


    










