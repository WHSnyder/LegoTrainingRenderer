import numpy as np
import json
import re
import math
from numpy import linalg as LA
import matplotlib.pyplot as plt

hf="/home"

expr = re.compile("([-]?[0-9]*\.[0-9]{4})")
dim = 512
stud_offset = np.array([0.096,0.0,0.0,0.0],dtype=np.float32)

def dictFromJson(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
    return data


def matrix_from_string(matstring):

    matches = expr.findall(matstring)

    nums = np.asarray(list(map(lambda x: float(x), matches)), dtype=np.float32)
    nums = np.reshape(nums, (4,4))

    return nums
    


def get_object_matrices(filename):

    data = dictFromJson(filename)

    for key in data:
        data[key] = matrix_from_string(data[key])
    return data



def get_circle_length(m,v,p,v1):

    v2 = v1 + stud_offset

    screenverts = verts_to_screen(m,v,p,[v1,v2],filter=False)
    screenverts[:,0:2] = toNDC(screenverts[:,0:2], (512,512))

    diff = screenverts[0,0:2] - screenverts[1,0:2]

    return int(round(LA.norm(diff)))



def get_object_studs(piece):
    file = hf+"/will/projects/training/piecedata/{}.json".format(piece)
    studs=dictFromJson(file)["studs"]
    return studs



def verts_to_screen(model,view,frust,verts,filter=True):
    
    screenverts = []
    mv = np.matmul(view,model)

    for i,vert in enumerate(verts):

        camvert = np.matmul(mv, vert)
        depth = LA.norm(camvert[0:3])

        screenvert = np.matmul(frust,camvert)
        screenvert = screenvert/screenvert[3]

        if filter and (abs(screenvert[0]) > 1 or abs(screenvert[1]) > 1):
            return None
            #continue
        
        screenvert[0:2] = (screenvert[0:2] + 1)/2
        screenvert[2] = depth
        screenvert[3] = i
        screenverts.append(screenvert)

    return np.array(screenverts,dtype=np.float32)


def toNDC(verts, dims):
    newverts = []
    for vert in verts:
        npcoord = tuple([round(vert[0] * dims[0]), round((1 - vert[1]) * dims[1])])
        
        #messy and likely unnecessary...
        vert[0] = dims[0] - 1 if vert[0] == dims[0] else vert[0]
        vert[0] = 0 if vert[0] == -1 else vert[0]

        vert[1] = dims[1] - 1 if vert[1] == dims[1] else vert[1]
        vert[1] = 0 if vert[1] == -1 else vert[1]

        newverts.append(npcoord)

    return np.asarray(newverts)

def fromNDC(verts,dims):
    newverts = []
    for vert in verts:
        clipcoord = 2 * np.array([ vert[0]/dims[0], 1 - (vert[1]/dims[1]) ] , dtype=np.float32) - 1
        #clipcoord = (2*clipcoord) - 1
        newverts.append(clipcoord)
    return newverts


def unproject_to_local(data,infodict,toworld,p,dims=(256,256),pr=False):

    mask = int(round(data[3]/5))

    if mask == 0:
        return np.array([0.0,0.0,0.0,1.0],dtype=np.float32)

    info = infodict[mask]
    tolocal = info["w2l"]
    lx,ly,lz = info["lows"]
    dx,dy,dz = info["dims"]

    depth = data[2]

    ndcs = data[0:2]
    ndcs = fromNDC([ndcs[::-1]],dims)[0]

    ndc_y = ndcs[0]
    ndc_x = ndcs[1]

    viewPos = np.zeros((4),dtype=np.float32)
    a = p[0,0]
    b = p[1,1]

    c1 = (ndc_x/a)**2
    c2 = (ndc_y/b)**2
    z = math.sqrt((depth**2)/(c1 + c2 + 1))

    x = 1 * (z * ndc_y/a)
    y = 1 * (z * ndc_x/b)

    viewPos[0] = x
    viewPos[1] = y
    viewPos[2] = -z
    viewPos[3] = 1.0

    worldPos = np.matmul(toworld,viewPos)
    localPos = np.matmul(tolocal,worldPos)

    localPos[0] = (localPos[0] - lx)/dx 
    localPos[1] = (localPos[1] - ly)/dy
    localPos[2] = (localPos[2] - lz)/dz

    localPos = np.absolute( localPos )

    return np.clip(localPos,0.0,1.0)





brickstuds = get_object_studs("Brick")
wingrstuds = get_object_studs("WingR")

def getCalibCorrs():
    path = hf+"/will/projects/legoproj/utils/calib_data/calibdata.txt"

    with open(path) as json_file:
        data = json.load(json_file)

    view = matrix_from_string(data["View"])
    model = matrix_from_string(data["Model"])
    proj = matrix_from_string(data["Projection"])

    verts = []
    for vert in np.asarray(data["ObjCoords"]):
        newvert = np.ones(4, dtype=np.float32)
        newvert[0:3] = vert[0:3]
        verts.append(newvert)

    verts = np.asarray(verts)

    screenverts = toNDC(verts_to_screen(model, view, proj, verts), (512,512))

    return np.delete(verts, 3, axis=1), screenverts




def getFeatureBoxes(width, height, centers):

    out = []

    for center in centers:
        x = center[1]
        y = center[0]

        x -= width/2
        y -= height/2

        out.append(tuple(np.int(np.asarray([x,y,width,height]))))

    return out



def toCV2bbox(points):

    out = []

    for point in points:
        [x,y,w,h] = point
        p1 = tuple([x,y])
        p2 = tuple([x + w, y + h]) 
        out.append([p1,p2])

    return out



def getTemplate(piece, num, plot=True):
    
    temppath = hf+"/will/projects/legoproj/data/{}_single/{}_{}_a.png".format(piece.lower(), num, piece.lower())
    tempjson = temppath.replace(".png", ".json")

    data = dictFromJson(tempjson)
    ostuds = get_object_studs(piece)

    img = cv2.imread(temppath)

    model = matrix_from_string(data["objects"][piece+".001"]["modelmat"])
    view = matrix_from_string(data["Camera"])
    proj = matrix_from_string(data["Projection"])

    screenverts = toNDC(verts_to_screen(model, view, proj, ostuds), (512,512))
    
    if plot:

        w = h = 20
        l = w/2

        imgboxes = cv2.copy(img)

        for vert in screenverts:

            x,y = screenverts[0], screenverts[1]
            x1,y1 = x - l, y - l
            x2,y2 = x + l, y + l

            cv2.rectangle(imgboxes, (x1,y1), (x2,y2), (0,0,0), 2)

        plt.imshow(imgboxes, cmap="rgb")
        plt.show()

    return img, np.delete(ostuds, 3, axis=1), screenverts