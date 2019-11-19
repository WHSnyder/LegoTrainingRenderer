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


classes = ["Wing","Pole","Brick","Engine","Slope"]
write_path = ""

def getClass(name):
    for c in classes:
        if c in name:
            return c

objs = []

for obj in bpy.context.selected_objects:
    if obj.name !="Table":
        objs.append(obj)



print("Begining.....\n\n\n")


random.seed()



#bpy.context.scene.render.engine = 'CYCLES'




scene = bpy.context.scene
scene_objs = bpy.data.objects
camera = bpy.data.objects['Camera']



imgsdir = "/home/will/projects/training/surface_images/"
#imgpaths = os.listdir(imgsdir)
imgs = []

'''
for img in bpy.data.images:
    bpy.data.images.remove(img)
for path in imgpaths:
    img = bpy.data.images.load(filepath=imgsdir+path)
    imgs.append(img)

tablemat = bpy.data.materials["Table"]
nodes = tablemat.node_tree.nodes
imgnode = nodes.get("Image Texture")

def changeTable():
    imgnode.image = imgs[random.randint(0,80)]

table = scene_objs["Table"]
'''

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


#normalmat = bpy.data.materials["Normz"]


objmasks = {}


scenedata = {}
scenedata["objects"] = {}
scenedata["dataroot"] = write_path

for obj in objs:
    objdata = {}
    objdata["modelmat"] = str(obj.matrix_world)
    scenedata["objects"][obj.name] = objdata
    

bpy.context.scene.update()



black_shadeless = bpy.data.materials["BlackShadeless"]
#bck = bpy.data.objects['Background']
#bck.data.materials[0] = black_shadeless
#bck.active_material_index = 0



scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'

bpy.context.scene.update()
projection_matrix = camera.calc_matrix_camera(
        bpy.context.scene.render.resolution_x,
        bpy.context.scene.render.resolution_y)
bpy.context.scene.update()
scenedata["projection"] = str(projection_matrix)




def getObjSubset(percent,matchoices):

    numobjs = len(objs)
    choices = int(round(percent*numobjs))

    if choices == 0:
        choices = 1

    res = []

    for obj in objs:

        des = True if random.randint(0,numobjs) <= choices else False

        if True:
            res.append(obj)
            obj.hide_render = False
            obj.data.materials[0] = random.choice(matchoices)
        else:
            obj.hide_render = True

    return res




#world = bpy.data.worlds["World.001"]
#world.use_nodes = True
#bg = world.node_tree.nodes["Background"]
#renderer = bpy.data.scenes["LegoTest"].cycles

objslice = random.randint(4,10)*.05

matz = random.sample(mats,random.randint(1,math.floor(len(mats)/2)))
objectz = getObjSubset(objslice,matz)

