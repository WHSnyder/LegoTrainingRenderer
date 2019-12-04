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
    #if ("Engine" in name) or ("Pole" in name):
    #    return None
    #return name

    if "WingL" in name:
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

    rows = np.arange(512)
    cols = np.arange(512)

    r,c = np.meshgrid(rows,cols)
    inds = np.stack((c,r),axis=-1).astype(np.float32)
    d = np.reshape(depthmap,(512,512,1))
    f = np.concatenate((inds,d),axis=-1)

    kernel = np.ones((5,5),np.uint8)

    #vfunc = np.vectorize(fu.unproject_to_local,signature="(4),(4,4),(4,4)->(3)")

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

        #fu.toProjCoords(studs,modelmat,viewmat,projmat)

        #screenverts = fu.verts_to_screen(modelmat, viewmat, projmat, studs)
        #screenverts[:,0:2] = fu.toNDC(screenverts[:,0:2], (512,512))

        toworld = np.linalg.inv(viewmat)
        tolocal = np.linalg.inv(modelmat)

        mask = cv2.erode(masks[hue],kernel,iterations=1)
        mask = np.reshape(mask,(512,512,1))
        g = np.concatenate((f,mask),axis=-1)
        #print(g.shape)

        #output = np.zeros((512,512,4),dtype=np.float32)

        output = np.apply_along_axis(func1d=fu.unproject_to_local, axis=-1, arr=g, tolocal=tolocal, toworld=toworld, p=projmat)

        # for row in range(512):
        #     for col in range(512):
        #         #print(col)
        #         pri=False
        #         if (col - row)%8 == 0:
        #             pri=True
        #         output[row,col] = fu.unproject_to_local(g[row,col],tolocal,toworld,projmat,pr=pri)

        output = (np.around(255 * output[:,:,2::-1])).astype(np.uint8)
        wr = os.path.join(abspath,"geom_{}_{}.png".format(i,hue))
        cv2.imwrite(wr,output)
        



def iterOverlay(indices):
    for ind in indices:
        overlay(ind)


indices = np.arange(data["runs"]) if args.num is None else np.arange(args.num) 
cores = mp.cpu_count()
num_procs = 1 if len(indices) < cores else cores
indices_lists = np.array_split(indices, num_procs)

processes = []

print(indices_lists)

for ilist in indices_lists:
    processes.append( Process(target=iterOverlay, args=(ilist,)) )

for process in processes:
    process.start()

for process in processes:
    process.join()
