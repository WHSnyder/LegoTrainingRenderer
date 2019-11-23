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
    if ("Engine" in name) or ("Pole" in name):
        return None
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

'''
def find_nearest(index,depth,dims):

    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]
'''

def overlay(i):

    #print(i)
    imgname = "{}.png".format(i)
    imgpath = os.path.join(abspath,imgname) 
    maskpath = os.path.join(abspath,"mask_{}.png".format(i))

    depthpath = os.path.join(abspath,"depth_{}.npy".format(i))
    depthmap = np.load(depthpath,allow_pickle=False)

    projmat = fu.matrix_from_string(data["projection"])

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
        #studs = np.array([[-1.95,1.95,0.0,1.0]],dtype=np.float32)

        modelmat = fu.matrix_from_string(data["objects"][objname]["modelmat"])
        viewmat = fu.matrix_from_string(data["viewmats"][i])

        screenverts = fu.verts_to_screen(modelmat, viewmat, projmat, studs)

        if screenverts.size == 0:
            continue

        screenverts[:,0:2] = fu.toNDC(screenverts[:,0:2], (512,512))
        visibleverts = [v for v in screenverts if depthmap[int(v[1]),int(v[0])] - abs(v[2]) > -0.1]
        #print(objname)
        for v in screenverts:
            #v = random.choice(visibleverts)
            d = abs(v[2])
            dtrue = depthmap[int(v[1]),int(v[0])]
            #print(dtrue-abs(d))
            #print("Depthmap value {}, Calculated value dist {}".format(dtrue,d))
            
        if visibleverts:
            verts+=visibleverts

    img = cv2.imread(imgpath)
    #print(verts)

    for v in verts:
        x=int(v[0])
        y=int(v[1])
        cv2.circle(img, (x,y), 2, (50,50,200),1)

    cv2.imwrite(os.path.join(abspath,"studs_{}.png".format(i)),img)


def iterOverlay(indices):
    for ind in indices:
        overlay(ind)


indices = np.arange(data["runs"]) if args.num is None else [args.num] 
cores = mp.cpu_count()
num_procs = 1 if len(indices) < cores else cores
indices_lists = np.array_split(indices, num_procs)

processes = []

for ilist in indices_lists:
    processes.append( Process(target=iterOverlay, args=(ilist,)) )

for process in processes:
    process.start()

for process in processes:
    process.join()