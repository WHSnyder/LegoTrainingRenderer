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

parser.add_argument('-t','--tag',dest='tag',required=False,type=int)

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

huedict = {}

for obj in data["objects"]:
    hue = round(data["objects"][obj]["maskhue"],2)
    huedict[int(round(hue*180))] = obj
print(len(data["objects"]))

#sys.exit()

class_counts = {"Engine":0,"Wing":0,"Brick":0,"Pole":0}



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



#tag = args.tag


count = 0
links = {}


for i in range(data["runs"]):
    
    print("On image {}".format(i))
    
    imgname = "{}.png".format(i)
    imgpath = os.path.join(abspath,imgname) 
    maskpath = os.path.join(abspath,"mask_{}.png".format(i))
    
    masks = separate(imgpath,maskpath)

    if masks: 
        links[imgname] = []
    else:
        continue

    for j,hue in enumerate(masks):

        objname = findNearestHue(hue)
        objclass = data["objects"][objname]["class"]

        maskname = "{}_{}_{}_mask.png".format(i,j,objclass)
        links[imgname].append({"class":objclass,"file":maskname})

        wmask = os.path.join(write_path,maskname)
        cv2.imwrite(wmask,masks[hue])


dumppath = os.path.join(abspath,"dset_withmasks.json")

with open(dumppath, 'w') as fp:
    json.dump(links,fp)
