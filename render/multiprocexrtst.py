import OpenEXR as oe 
import numpy as np
import cv2
import struct
import os
import Imath
import threading
import time
from multiprocessing import Process




forma = 512 * 512 * "f"
flo = Imath.PixelType(Imath.PixelType.FLOAT)


def getNPFromEXR(dw,channelname):
    channel = dw.channel(channelname,flo)
    return np.frombuffer(channel, dtype=np.float32, count=-1, offset=0).reshape((512,512))

def getFile(p):
    return oe.InputFile(p)

def parseEXRs(start,end):

    for i in range(start,end):
        print(i)
        name = "{:0>4}.exr".format(i+1)
        base = "/Users/will/projects/legoproj/data/exr_dset_{}/".format(0)

        fullpath = os.path.join(base,name)

        dw = getFile(fullpath)

        b = getNPFromEXR(dw,"image.B")
        g = getNPFromEXR(dw,"image.G")
        r = getNPFromEXR(dw,"image.R")

        img = (255*cv2.merge([b,g,r])).round().astype(np.uint8)
        cv2.imwrite(os.path.join(base,"{}.png".format(i)), img)

        depth = getNPFromEXR(dw,"masks.R")
        np.save(os.path.join(base,"{}_depth.npy".format(i)), depth)
        

        #cv2.imwrite(os.path.join(base,"{}_masks.png".format(i)), depth)



millis = lambda: int(round(time.time() * 1000))
timestart = millis()

runs = 100

threads = []

for i in range(4):
    threads.append( Process(target=parseEXRs, args=(i*25,(i+1)*25,)) )

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

'''
thread1 = Process(target=parseEXRs, args=(0,25,))
thread2 = Process(target=parseEXRs, args=(25,50,))
thread3 = Process(target=parseEXRs, args=(50,75,))
thread4 = Process(target=parseEXRs, args=(75,100,))

thread1.start()
thread2.start()
thread3.start()
thread4.start()

thread1.join()
thread2.join()
thread3.join()
thread4.join()
'''


print("Generated " + str(runs) + " images in " + str(float(millis() - timestart)/1000.0) + " seconds")

