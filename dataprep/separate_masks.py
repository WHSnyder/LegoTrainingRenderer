import os
import cv2
import argparse
import json
import numpy as np


parser = argparse.ArgumentParser()


parser.add_argument('-p', '--path', dest='path',
                  required=True,
                  help='BAse data path?')

parser.add_argument('-n','--num',dest='num',required=False,type=int)

args = parser.parse_args()

newdata = []

jsonpath = os.path.join(args.path,"data.json")
with open(jsonpath) as json_file:
        data = json.load(json_file)

write_path = os.path.join(args.path,"separations")

if not os.path.exists(write_path):
    os.mkdir(write_path)
else:
    os.system("rm {}".format(os.path.join(write_path,"*")))

huedict = {}

for obj in data["objects"]:
    hue = round(data["objects"][obj]["maskhue"],2)
    huedict[int(round(hue*179))] = obj




def separate(imgpath,maskpath,entry,ind):

    class_counts = {"Engine":0,"Wing":0,"Brick":0,"Pole":0}
    files = {}
    files["images"] = []
    files["masks"] = []
    kernel = np.ones((2,2), np.uint8) 


    img = cv2.imread(imgpath)

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

        piece = huedict[hu]
        piecetype = data["objects"][piece]["class"]
        class_counts[piecetype]+=1

        filename = "{}_mask_{}_{}.png".format(ind,piecetype,class_counts[piecetype])
        threshpath = os.path.join(write_path,filename)
        files["masks"].append(filename)

        cv2.imwrite(threshpath,threshed)

    if masks > 0:
        sepspath = os.path.join(write_path,entry["r"])
        cv2.imwrite(sepspath,img)

        files["images"].append(entry["r"])

        return files

    return None


if args.num:

    entry = data["renders"][args.num]
    imgpath = os.path.join(args.path,entry["r"]) 
    maskpath = os.path.join(args.path,entry["m"])
    separate(imgpath,maskpath)

else:

    for i,entry in enumerate(data["renders"]):
        print("On image {}".format(i))
        imgpath = os.path.join(args.path,entry["r"]) 
        maskpath = os.path.join(args.path,entry["m"])

        links = separate(imgpath,maskpath,entry,i)

        if links is not None:
            newdata.append(links)

    jsonpath = os.path.join(write_path,"data.json")

    with open(jsonpath, 'w') as fp:
        json.dump(newdata,fp)