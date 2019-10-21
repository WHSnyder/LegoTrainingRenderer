import bpy
import random
import math
import time
import numpy as np
import json
import mathutils as mu
import os
from math import degrees


name = "combo1"
res = 512
write_path = "/Users/will/projects/legoproj/data/{}/".format(name)



scene = bpy.context.scene
scene_objs = bpy.data.objects



def getMat(name):
    for mat in bpy.data.materials:
        if mat.name == name:
            return mat


black_shadeless = getMat("BlackShadeless")
white_shadeless = getMat("WhiteShadeless")
black = getMat("Black")
gray = getMat("Gray")
lgray = getMat("LightGray")
blue = getMat("Blue")

bck = bpy.data.objects['Background']
camera = bpy.data.objects['Camera']


objs = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]

scenedata = {}
scenedata["objects"] = {}


for obj in objs:
    objdata = {}
    df = obj.data.materials[0].diffuse_color
    objdata["diffuse"] = (df[0],df[1],df[2])
    objdata["matname"] = obj.data.materials[0].name
    objdata["modelmat"] = str(obj.matrix_world)

    scenedata["objects"][obj.name] = objdata



scene.render.resolution_x = res
scene.render.resolution_y = res
scene.render.resolution_percentage = 100

bpy.context.scene.update()

projection_matrix = camera.calc_matrix_camera(
        bpy.context.scene.render.resolution_x,
        bpy.context.scene.render.resolution_y)

bpy.context.scene.update()




def shadeMasks():

    bck.data.materials[0] = black_shadeless

    for obj in objs:
        obj.data.materials[0] = black_shadeless

    for obj in objs:
        maskpath = write_path + "masks/" + obj.name.replace(".","_") + ".png"
        scenedata["objects"][obj.name]["maskpath"] = maskpath

        obj.data.materials[0] = white_shadeless
        
        scene.render.resolution_x = 64
        scene.render.resolution_y = 64
        scene.render.resolution_percentage = 100   
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = maskpath
        bpy.ops.render.render(write_still = 1)

        obj.data.materials[0] = black_shadeless





if not os.path.exists(write_path):
    os.mkdir(write_path)
else:
    os.system("rm " + write_path + "*")

if not os.path.exists(write_path + "masks/"):
    os.mkdir(write_path + "masks/")
else:
    os.system("rm " + write_path + "masks/*")


bck.data.materials[0] = white_shadeless
bpy.context.scene.update()


scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = write_path + name + ".png"
bpy.ops.render.render(write_still = 1)


scenedata["Camera"] = str(camera.matrix_world.copy().inverted())
scenedata["Projection"] = str(projection_matrix)


shadeMasks()


for obj in objs:
    mat = scenedata["objects"][obj.name]["matname"]
    obj.data.materials[0] = getMat(mat) 


with open(write_path + "{}.json".format(name), 'w') as fp:
    json.dump(scenedata, fp)