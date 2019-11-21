import OpenEXR as oe 
import numpy as np
import cv2
import struct
import os
import Imath
import threading
import time



forma = 512 * 512 * "f"
flo = Imath.PixelType(Imath.PixelType.FLOAT)


def getNPFromEXR(dw,channelname):
    channel = dw.channel(channelname,flo)
    return (255 * np.frombuffer(channel, dtype=np.float32, count=-1, offset=0)).reshape((512,512))

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

        img = cv2.merge([b,g,r]).round().astype(np.uint8)

        cv2.imwrite(os.path.join(base,"{}.png".format(i)), img)



millis = lambda: int(round(time.time() * 1000))
timestart = millis()

runs = 20

thread1 = threading.Thread(target=parseEXRs, args=(0,5,))
thread2 = threading.Thread(target=parseEXRs, args=(5,10,))
thread3 = threading.Thread(target=parseEXRs, args=(10,15,))
thread4 = threading.Thread(target=parseEXRs, args=(15,20,))

thread1.start()
thread2.start()
thread3.start()
thread4.start()

thread1.join()
thread2.join()
thread3.join()
thread4.join()


print("Generated " + str(runs) + " images in " + str(float(millis() - timestart)/1000.0) + " seconds")

