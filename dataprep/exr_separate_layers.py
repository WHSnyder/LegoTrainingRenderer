import OpenEXR as oe 
import numpy as np
import cv2
import struct
import os
import Imath
import threading
import time
import json
import multiprocessing as mp
from multiprocessing import Process
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-p','--path',dest='path',required=True,help='JSON data path?')
parser.add_argument('-n','--num',dest='num',required=False,help='Number of files?')
args = parser.parse_args()

with open(args.path) as json_file:
    data = json.load(json_file)

flo = Imath.PixelType(Imath.PixelType.FLOAT)


def getEXRChannels(dw,channels):
    exr_channels = dw.channels(channels,flo)
    return [np.frombuffer(channel, dtype=np.float32, count=-1, offset=0).reshape((512,512)) for channel in exr_channels]


def parseEXRs(indices,basepath):

    for i in indices:
        
        print(i)

        name = "{:0>4}.exr".format(i)
        fullpath = os.path.join(base,name)

        dw = oe.InputFile(fullpath)
        [b,g,r,d,m] = getEXRChannels(dw,["image.B","image.G","image.R","depth.R","masks.R"])

        img = (255*cv2.merge([b,g,r])).round().astype(np.uint8)
        cv2.imwrite(os.path.join(base,"{}.png".format(i)), img)
        
        np.save(os.path.join(base,"depth_{}.npy".format(i)),d)

        h = 5 * (m.round().astype(np.uint8))
        mask = h > 0
        s = (200 * mask).astype(np.uint8)
        v = (200 * mask).astype(np.uint8)

        mask = cv2.cvtColor(cv2.merge([h,s,v]),cv2.COLOR_HSV2BGR)
        cv2.imwrite(os.path.join(base,"mask_{}.png".format(i)),mask)
      

millis = lambda: int(round(time.time() * 1000))
timestart = millis()


base = data["dataroot"]
runs = data["runs"] if not args.num else args.num
cores = mp.cpu_count()
num_procs = 1 if runs < cores else cores
indices = np.array_split( np.arange(runs), num_procs )

processes = []

for i in indices:
    processes.append( Process(target=parseEXRs, args=(i,base,)) )

for process in processes:
    process.start()

for process in processes:
    process.join()

print("Processed " + str(runs) + " files in " + str(float(millis() - timestart)/1000.0) + " seconds")