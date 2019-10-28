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

jsonpath = os.path.join(args.path,"data.json")
with open(jsonpath) as json_file:
        data = json.load(json_file)

write_path = os.path.join(args.path,"normalz")

if not os.path.exists(write_path):
    os.mkdir(write_path)
#else:
    #os.system("rm {}".format(os.path.join(write_path,"*")))

huedict = {}

for obj in data["objects"]:
    hue = round(data["objects"][obj]["maskhue"],2)
    huedict[int(round(hue*179))] = obj




def separate(imgpath,maskpath,normpath,entry,ind):

    class_counts = {"Engine":0,"Wing":0,"Brick":0,"Pole":0}
    files = {}
    files["images"] = []
    files["masks"] = []
    kernel = np.ones((2,2), np.uint8) 
    pairs = []


    img = cv2.imread(imgpath)
    normsimg = cv2.imread(normpath)
    mask = cv2.imread(maskpath)
    hsvmask = cv2.cvtColor(mask,cv2.COLOR_BGR2HSV)

    hist = cv2.calcHist([hsvmask],[0],None,[180],[0,179])
    hues=[]

    for j,e in enumerate(hist):
        if e[0] > 1000:
            hues.append(j)
    masks = 0
    for hue in hues:

        threshed = cv2.inRange(hsvmask, (hue-1,0,100), (hue+1,255,255))

        if np.sum(threshed) <= 255*1000:
            continue;

        hu = hue
        m = -1
        n = 1
        while hu not in huedict:
            hu+=n*m
            n+=1
            m*=-1 

        masks+=1

        threshed = cv2.medianBlur(threshed.astype(np.uint8), 3)
        threshed = cv2.dilate(threshed, kernel, iterations=1) 

        masked = cv2.bitwise_and(img,img,mask=threshed)
        normsmasked = cv2.bitwise_and(normsimg,normsimg,mask=threshed)

        #masked = cv2.resize(masked, (256,256), interpolation=cv2.INTER_LINEAR)
        #normsmasked = cv2.resize(normsmasked, (256,256), interpolation=cv2.INTER_LINEAR)

        pairs.append((masked,normsmasked))

    return pairs

count = 0
tag = args.tag

for i,entry in enumerate(data["renders"]):
    
    print("On image {}".format(i))
    
    imgpath = os.path.join(args.path,entry["r"]) 
    maskpath = os.path.join(args.path,entry["m"])
    normpath = os.path.join(args.path,entry["n"])

    links = separate(imgpath,maskpath,normpath,entry,i)

    for pair in links:

        wmaskname = "{}_{}.png".format(tag,count)
        wnormname = "{}_{}_normz.png".format(tag,count)
        
        wmask = os.path.join(write_path,wmaskname)
        wnorm = os.path.join(write_path,wnormname)
        
        cv2.imwrite(wnorm,pair[1])
        cv2.imwrite(wmask,pair[0])

        count+=1