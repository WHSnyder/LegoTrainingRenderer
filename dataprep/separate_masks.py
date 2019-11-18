import os
import cv2
import argparse
import json
import numpy as np


parser = argparse.ArgumentParser()


parser.add_argument('-p', '--path', dest='path',
                  required=True,
                  help='Base data path?')

parser.add_argument('-t','--tag',dest='tag',required=True,type=int)

args = parser.parse_args()

newdata = []

jsonpath = os.path.join(args.path,"dset.json")
with open(jsonpath) as json_file:
        data = json.load(json_file)

write_path = os.path.join(args.path,"masks")

if not os.path.exists(write_path):
    os.mkdir(write_path)
#else:
#    os.system("rm {}".format(os.path.join(write_path,"*")))

huedict = {}

for obj in data["objects"]:
    hue = round(data["objects"][obj]["maskhue"],2)
    huedict[int(round(hue*179))] = obj

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
        if e[0] > 1000:
            hues.append(j)

    for hue in hues:

        threshed = cv2.inRange(hsvmask, (hue-1,0,100), (hue+1,255,255))

        if np.sum(threshed) <= 255*1000:
            continue;

        threshed = cv2.medianBlur(threshed.astype(np.uint8), 3)
        threshed = cv2.dilate(threshed, kernel, iterations=1) 
        maskdict[hue] = threshed

    return maskdict



tag = args.tag


count = 0
links = {}

for i in range(data["runs"]):
    
    print("On image {}".format(i))
    
    imgname = "{}.png".format(i)
    imgpath = os.path.join(args.path,imgname) 
    maskpath = os.path.join(args.path,"{}_mask.png".format(i))
    masks = separate(imgpath,maskpath)

    links[imgname] = [] if masks else continue

    for j,hue in enumerate(masks):

    	objname = findNearestHue(hue)
    	objclass = data["objects"][objname]["class"]

    	maskname = "{}_{}_{}_mask.png".format(i,j,objclass)
        links[i].append({"class":objclass,"file":maskname})

        wmask = os.path.join(write_path,maskname)
        cv2.imwrite(wmask,masks[hue])


dumppath = os.path.join(args.path,"dset_withmasks.json")

with open(dumppath, 'w') as fp:
    json.dump(links,fp)
