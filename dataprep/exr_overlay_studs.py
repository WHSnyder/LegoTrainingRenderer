import os
import cv2
import argparse
import json
import numpy as np
import sys
import multiprocessing as mp
from multiprocessing import Process
import random

from scipy.stats import multivariate_normal as mv

random.seed()

#sys.path.append("/home/will/projects/legoproj")

#import cvscripts
#from cvscripts import feature_utils as fu
import feature_utils as fu

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', dest='path',required=True,help='JSON data path?')
parser.add_argument('-n', '--num', dest='num',required=False,type=int,help='File num?')
args = parser.parse_args()

with open(args.path) as json_file:
    data = json.load(json_file)

abspath = os.path.abspath(args.path)
abspath = abspath.replace(abspath.split("/")[-1],"")

write_path = os.path.join(abspath,"kpts_total")

if not os.path.exists(write_path):
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
    if ("WingR" in name or "WingL" in name):
        return name
    #if "Slope" in name:
    #    return name
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


def generate_heatmap(inp,sigma):
    #heatmap[int(pt[1])][int(pt[0])] = 1
    # heatmap = 
    # m = np.amax(heatmap)
    # heatmap = heatmap/m
    # return heatmap
    return cv2.blur(inp,sigma)



def overlay(i):

    print(i)
    tag = "{:0>4}".format(i)
    global counter

    imgname = "{}_a.png".format(tag)
    imgpath = os.path.join(abspath,imgname)
    image = cv2.imread(imgpath)

    maskpath = os.path.join(abspath,"{}_masks.png".format(tag))

    depthpath = os.path.join(abspath,"{}_npdepth.npy".format(tag))
    depthmap = np.load(depthpath,allow_pickle=False)

    projmat = fu.matrix_from_string(data["projection"])

    masks = separate(maskpath)
    verts = []
    p=False

    #totalimg = np.zeros((256,256)).astype(np.uint8)

    outimg = np.zeros((256,256)).astype(np.uint8)


    for hue in masks:

        objname = getObjFromHue(hue)
        
        # if objname:
        #     objclass = objname.split(".")[0]
        #     studs = fu.get_object_studs(objclass)
        #     for stud in studs:
        #         stud.append(1.0)
        # else:
        #     continue

        if not objname:
            continue

        #studmask = np.zeros((512,512),dtype=np.uint8)
        #maskedimg = np.zeros((512,512,3),dtype=np.uint8)
        inds={0:30,1:60,2:90,3:120,4:150}
        if "WingR" in objname:
            studs = [[-.94,1.86,0.0,1.0], [-.94,-1.86,0.0,1.0], [-0.0,-1.86,0.0,1.0], [.94,1.86,0.0,1.0]]#[.9,.9,0.0,1.0], [.9,1.8,0.0,1.0]]
        elif "WingL" in objname:
            studs = [[-.94,-1.86,0.03,1.0] , [-.94,1.86,0.03,1.0], [-0.0,1.86,0.03,1.0], [.94,-1.86,0.03,1.0]]#[.9,-.9,0.032,1.0], [.9,-1.8,0.032,1.0]]
        elif 
        """if "Slope1" in objname:
            studs = [[0.0,0.0,0.95487,1.0]]
        elif "Slope3" in objname:
            studs = [[0.0,0.579934,1.17411,1.0],[0.0,-0.579934,1.17411,1.0]]
        else:
            studs = [[-0.579934,-0.579934,0.579934,1.0],[-0.579934,0.579934,0.579934,1.0],[0.579934,-0.579934,0.579934,1.0],[0.579934,0.579934,0.579934,1.0]]
        """
        studs = np.array(studs,dtype=np.float32)
        #studs[0:3] = .95 * studs[0:3]

        modelmat = fu.matrix_from_string(data["objects"][objname]["modelmat"])
        viewmat = fu.matrix_from_string(data["viewmats"][i])

        screenverts = fu.verts_to_screen(modelmat, viewmat, projmat, studs, filter=True)

        if screenverts is None:
            continue

        screenverts[:,0:2] = fu.toNDC(screenverts[:,0:2], (512,512))
        visibleverts = screenverts# [v for v in screenverts if depthmap[int(v[1]),int(v[0])] - abs(v[2]) > -0.05]

        #maskedimg = cv2.bitwise_and(image,image,mask=masks[hue])
        #cv2.imwrite(os.path.join(write_path,"{}_{}_masked.png".format(tag,counter)), cv2.resize(maskedimg, (256,256), interpolation=cv2.INTER_LINEAR))

        #outimg = np.zeros((256,256,3)).astype(np.uint8)
        #outimg = np.zeros((256,256)).astype(np.uint8)

        finalverts = []

        for v in visibleverts:
            x= int(v[0])
            y=int(v[1])
            val = masks[hue][y,x]

            x= int(v[0]/2)
            y=int(v[1]/2)
            if val > 0:
                pos = np.dstack(np.mgrid[0:256:1, 0:256:1])
                rv = mv(mean=[y,x], cov=7)
                pd = rv.pdf(pos)
                
                img = pd/np.amax(pd)
                gimg = np.rint(255 * img)
                gimg = gimg.astype(np.uint8)

                #cv2.circle(outimg, (x,y), 3, (255,255,255),-1)
                #outimg[y,x] = 255
                outimg = outimg + gimg
                #totalimg = totalimg + gimg
            #coord = np.array([x,y],dtype=np.float32)
            #else:
            #    coord = np.array([np.nan,np.nan])
            #finalverts.append(coord)

        #f = np.array(finalverts)
        #print(f.shape)
        #np.save(os.path.join(write_path,"{}_kpts.npy".format(counter)), f)

        #cv2.imwrite(os.path.join(write_path,"{}_{}_kpts.png".format(tag,counter)), outimg)
        #counter += 1
    cv2.imwrite(os.path.join(write_path,"{}_img.png".format(tag)), image)
    cv2.imwrite(os.path.join(write_path,"{}_kpts.png".format(tag)), outimg)




def iterOverlay(indices):
    for ind in indices:
        overlay(ind)


indices = np.arange(data["runs"]) if args.num is None else [args.num] 
cores = mp.cpu_count()
num_procs = 1 if len(indices) < cores else cores
indices_lists = np.array_split(indices, num_procs)
#print(indices_lists)

processes = []

counter = 0
iterOverlay(indices)


'''
for ilist in indices_lists:
    processes.append( Process(target=iterOverlay, args=(ilist,)) )

for process in processes:
    process.start()

for process in processes:
    process.join()
'''