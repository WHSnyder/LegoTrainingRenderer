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


hues_objdata = {}

for entry in data["ids"]:

    if entry == "0":
        continue

    objentry = data["objects"][data["ids"][entry]]

    l2w = fu.matrix_from_string(objentry["modelmat"])
    w2l = np.linalg.inv(l2w)

    bbl = np.array(objentry["bbl"])
    bbh = np.array(objentry["bbh"])

    dims = bbh - bbl

    info = {}
    info["w2l"] = w2l
    info["lows"] = bbl
    info["dims"] = dims

    hues_objdata[int(entry)] = info


rows = np.arange(512)
cols = np.arange(512)

r,c = np.meshgrid(rows,cols)
inds = np.stack((c,r),axis=-1).astype(np.float32)



abspath = os.path.abspath(args.path)
abspath = abspath.replace(abspath.split("/")[-1],"")



num=0
write_path = "/home/will/projects/legoproj/data/{}_geom/".format(num)
while os.path.exists(write_path):
    num += 1
    write_path = "/home/will/projects/legoproj/data/{}_geom/".format(num)
os.mkdir(write_path)




classes = ["WingR","WingL","Brick","Pole"]


def getClass(objname):
    for clss in classes:
        if clss in objname:
            return clss
    return None


def getObjFromHue(hue):
    hue = int(round(hue/5))
    name = data["ids"][str(hue)]
    
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



def overlay(i):

    print(i)

    tag = "{:0>4}".format(i)

    viewmat = fu.matrix_from_string(data["viewmats"][i])
    toworld = np.linalg.inv(viewmat)
    
    imgname = "{}_img.png".format(tag)
    imgpath = os.path.join(abspath,imgname)

    maskpath = os.path.join(abspath,"{}_masks.png".format(tag))
    mask = cv2.imread(maskpath)
    mask = cv2.cvtColor(mask,cv2.COLOR_BGR2HSV)[:,:,0]

    depthpath = os.path.join(abspath,"{}_npdepth.npy".format(tag))
    depthmap = np.load(depthpath,allow_pickle=False)

    projmat = fu.matrix_from_string(data["projection"])

    image = cv2.imread(imgpath)

    d = np.reshape(depthmap,(512,512,1))
    f = np.concatenate((inds,d),axis=-1)

    kernel = np.ones((3,3),np.uint8)

    mask = np.reshape(mask,(512,512,1))
    g = np.concatenate((f,mask),axis=-1)

    output = np.apply_along_axis(func1d=fu.unproject_to_local, axis=-1, arr=g, infodict=hues_objdata, toworld=toworld, p=projmat)

    output = (np.around(255 * output[:,:,2::-1])).astype(np.uint8)
    wr = os.path.join(abspath,"{}_geom.png".format(tag))
    cv2.imwrite(wr,output)


def iterOverlay(indices):
    for ind in indices:
        overlay(ind)


indices = np.arange(data["runs"]) if args.num is None else np.arange(args.num) 
cores = mp.cpu_count()
num_procs = 1 if len(indices) < cores else cores
indices_lists = np.array_split(indices, num_procs)

processes = []

#indices_lists=np.array([[1]])

for ilist in indices_lists:
    processes.append( Process(target=iterOverlay, args=(ilist,)) )

for process in processes:
    process.start()

for process in processes:
    process.join()
