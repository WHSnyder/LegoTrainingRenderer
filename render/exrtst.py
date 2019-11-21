import OpenEXR as oe 
import numpy as np
import cv2
import struct
import os
import Imath
#import imathnumpy



forma = 512 * 512 * "f"

#@profile
def getNPFromEXR(dw,channelname):
    #return (255 * np.array(struct.unpack_from(forma, dw.channel(channelname), offset=0))).round().astype(np.uint8).reshape((512,512))
    channel = dw.channel(channelname)
    print(type(channel))
    return (255 * np.frombuffer(channel, dtype=np.float32, count=-1, offset=0)).reshape((512,512))
    #buf = buf.round().astype(np.uint8).reshape((512,512))
    #return buf

#@profile
def getFile(p):
    return oe.InputFile(fullpath)


for i in range(3):

    name = "{:0>4}.exr".format(i+1)
    base = "/home/will/projects/legoproj/data/exr_dset_{}/".format(3)

    fullpath = os.path.join(base,name)

    dw = getFile(fullpath)

    b = getNPFromEXR(dw,"image.B")
    g = getNPFromEXR(dw,"image.G")
    r = getNPFromEXR(dw,"image.R")

    img = cv2.merge([b,g,r]).round().astype(np.uint8)

    cv2.imwrite(os.path.join(base,"{}.png".format(i)), img)

    print(i)
