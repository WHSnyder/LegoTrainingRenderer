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

write_path = os.path.join(abspath,"kpts")

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
    if ("WingR" in name):
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
    tag = "{:0>4}".format(i)
    global counter

    imgname = "{}_a.png".format(tag)
    imgpath = os.path.join(abspath,imgname)
    image = cv2.imread(imgpath)

    maskpath = os.path.join(abspath,"{}_masks.png".format(tag))

    #depthpath = os.path.join(abspath,"{}_npdepth.npy".format(tag))
    #depthmap = np.load(depthpath,allow_pickle=False)

    projmat = fu.matrix_from_string(data["projection"])

    masks = separate(maskpath)
    verts = []
    p=False

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
        
        studs = [[-.9,1.8,0.0,1.0], [-.9,-1.8,0.0,1.0], [-0.0,-1.8,0.0,1.0], [.9,.9,0.0,1.0], [.9,1.8,0.0,1.0]]
        studs = np.array(studs,dtype=np.float32)

        modelmat = fu.matrix_from_string(data["objects"][objname]["modelmat"])
        viewmat = fu.matrix_from_string(data["viewmats"][i])

        screenverts = fu.verts_to_screen(modelmat, viewmat, projmat, studs, filter=True)

        if screenverts is None:
            continue

        if screenverts.size == 0:
            continue

        screenverts[:,0:2] = fu.toNDC(screenverts[:,0:2], (512,512))
        visibleverts = screenverts[:,0:2] #[v for v in screenverts if depthmap[int(v[1]),int(v[0])] - abs(v[2]) > -0.05]
        
        """if visibleverts is not None:
            
            for v in visibleverts:
                
                circle_rad = 4 #fu.get_circle_length(modelmat,viewmat,projmat,studs[int(v[3])])
                x=int(v[0])
                y=int(v[1])
                cv2.circle(studmask, (x,y), circle_rad, (255,255,255),-1)
        """
        #cv2.imwrite(os.path.join(write_path,"{}_studs.png".format(j)), studmask)

        maskedimg = cv2.bitwise_and(image,image,mask=masks[hue])
        cv2.imwrite(os.path.join(write_path,"{}_masked.png".format(counter)), cv2.resize(maskedimg, (256,256), interpolation=cv2.INTER_LINEAR))

        outimg = np.zeros((256,256)).astype(np.uint8)

        finalverts = []

        for k in range(5):

            l = k+1 if k < 4 else 0
            cur,nex = visibleverts[k]/2,visibleverts[l]/2

            x,y=int(cur[0]),int(cur[1])
            xn,yn = int(nex[0]),int(nex[1])

            cv2.circle(outimg, (x,y), 4, (255,255,255),-1)
            cv2.line(outimg, (x,y), (xn,yn), (255,255,255), 2)

        # for v in visibleverts:
        #     val = masks[hue][int(v[1]),int(v[0])]
        #     r = v if val > 0 else [np.nan,np.nan]
        #     finalverts.append(r)

        #f = np.array(finalverts)/2
        #print(f.shape)
        #np.save(os.path.join(write_path,"{}_studs.npy".format(counter)), f)
        cv2.imwrite(os.path.join(write_path,"{}_outline.png".format(counter)), outimg)


        counter += 1



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