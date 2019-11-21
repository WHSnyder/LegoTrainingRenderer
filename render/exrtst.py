import OpenEXR as oe 
import numpy as np
import cv2
import struct
import os



name = "000{}.exr".format(9)
base = "/home/will/projects/legoproj/data/exr_dset_{}/".format(1)

fullpath = os.path.join(base,name)
# Open the input file
dw = oe.InputFile(fullpath)

print(dw.header())

forma = 512 * 512 * "f"

floats = []

def getNPFromEXR(channelname):
	return (255 * np.array(struct.unpack_from(forma, dw.channel(channelname), offset=0))).round().astype(np.uint8).reshape((512,512))



b = getNPFromEXR("image.B")
g = getNPFromEXR("image.G")
r = getNPFromEXR("image.R")

# img = np.zeros((512,512,3),dtype="uint8")
# img[:,:,0] = b
# img[:,:,1] = g
# img[:,:,2] = r

img = cv2.merge([b,g,r])


cv2.imshow("tst", img)
cv2.waitKey(0)
