import bpy
import random
import math
import time
import numpy as np
import json
import mathutils as mu
import os
from math import degrees
import colorsys
import sys

bpy.context.scene.update()


runs = 300
classes = ["Wing","Pole","Brick","Engine","Slope"]


def getClass(name):
    for c in classes:
        if c in name:
            return c

objs = []

for obj in bpy.context.selected_objects:
    if obj.name !="Table":
        objs.append(obj)



print("Begining.....\n")

millis = lambda: int(round(time.time() * 1000))
timestart = millis()
random.seed()


mode = "exr"
num = 0
write_path = "/home/will/projects/legoproj/data/{}_dset_{}/".format(mode,num)
while os.path.exists(write_path):
    num += 1
    write_path = "/home/will/projects/legoproj/data/{}_dset_{}/".format(mode,num)
os.mkdir(write_path)


bpy.context.scene.render.engine = 'CYCLES'
outputnode = bpy.context.scene.node_tree.nodes["File Output"]
outputnode.base_path = write_path




scene = bpy.context.scene
scene_objs = bpy.data.objects
camera = bpy.data.objects['Camera']



imgsdir = "/home/will/projects/training/surface_images/"
imgpaths = os.listdir(imgsdir)
imgs = []

for img in bpy.data.images:
    bpy.data.images.remove(img)
for path in imgpaths:
    img = bpy.data.images.load(filepath=imgsdir+path)
    if img is not None:
        imgs.append(img)

tablemat = bpy.data.materials["Table"]
nodes = tablemat.node_tree.nodes
imgnode = nodes.get("Image Texture")


def changeTable():
    imgnode.image = random.choice(imgs)


gray = [.5,.5,.5,1.0]
lgray = [.8,.8,.8,1.0]
red = [1.0,1.0,1.0,1.0]
blue = [.1,.1,1.0,1.0]
black = [.2,.2,.2,1.0]
dirty = [.2,.3,.2,1.0]
dark=[0.0,0.0,0.0,1.0]



matnames = ["gray","lgray","red","blue","black","dirty","dark"]
matcolors = [gray, lgray, red, blue, black, dirty, dark]
mats = []

for i in range(0,len(matnames)):
    matname = matnames[i]
    if matname not in bpy.data.materials:
        mat = bpy.data.materials["Gray"].copy()
        mat.name = matname
    else:
        mat = bpy.data.materials[matname]

    color = matcolors[i]
    mat.use_nodes = True
    mat.node_tree.nodes["Diffuse BSDF"].inputs["Color"].default_value = color
    mats.append(mat)



scenedata = {}
scenedata["objects"] = {}
scenedata["dataroot"] = write_path

for obj in objs:
    objdata = {}
    objdata["modelmat"] = str(obj.matrix_world)
    scenedata["objects"][obj.name] = objdata

bpy.context.scene.update()



scenedata["ids"] = {0:None}
for i,obj in enumerate(objs):

    obj.active_material_index = 0
    obj.pass_index = i + 1

    scenedata["objects"][obj.name]["class"] = getClass(obj.name)
    scenedata["ids"][i + 1] = obj.name

scenedata["viewmats"] = []
scenedata["runs"] = runs


black_shadeless = bpy.data.materials["BlackShadeless"]
bck = bpy.data.objects['Background']
bck.data.materials[0] = black_shadeless
bck.active_material_index = 0


scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'

bpy.context.scene.update()
projection_matrix = camera.calc_matrix_camera(
        bpy.context.scene.render.resolution_x,
        bpy.context.scene.render.resolution_y)
bpy.context.scene.update()
scenedata["projection"] = str(projection_matrix)



#Main render
def shade(x,subset):

    changeTable()

    print(x)

    filename = "{}.exr".format(x)

    scenedata["viewmats"].append(str(camera.matrix_world.copy().inverted()))

    outputnode.base_path = write_path
    bpy.context.scene.frame_set(x)
    bpy.context.scene.update()

    bpy.ops.render.render(layer="RenderLayer")



def getObjSubset(percent,matchoices):

    numobjs = len(objs)
    choices = int(round(percent*numobjs))

    if choices == 0:
        choices = 1

    res = []

    for obj in objs:

        des = True if random.randint(0,numobjs) <= choices else False

        if des:
            res.append(obj)
            obj.hide_render = False
            obj.data.materials[0] = random.choice(matchoices)
        else:
            obj.hide_render = True

    return res


world = bpy.data.worlds["World.001"]
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
renderer = bpy.data.scenes["LegoTest"].cycles

for x in range(runs):

    renderer.samples = random.randint(10,15)

    strength = random.randint(2,10)*.1
    bg.inputs[1].default_value = strength

    objslice = random.randint(4,10)*.05

    matz = random.sample(mats,random.randint(1,math.floor(len(mats)/2)))
    objectz = getObjSubset(objslice,matz)

    camera.location = (random.randint(6,8) * -1 if random.randint(0,1) < 1 else 1, random.randint(6,8) * -1 if random.randint(0,1) < 1 else 1, random.randint(5,8))

    bpy.context.scene.update()
    shade(x,objectz)


with open(os.path.join(write_path,"dset.json"), 'w') as fp:
    json.dump(scenedata,fp)

print("Generated " + str(runs) + " images in " + str(float(millis() - timestart)/1000.0) + " seconds")

objectz = getObjSubset(objslice,matz)

for obj in objs:
    obj.hide = False
    obj.hide_render = False