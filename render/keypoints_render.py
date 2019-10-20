import bpy
import random
import math
import time
import numpy as np
import sys


from math import degrees


mode = "keypts"
write_path = "/Users/will/projects/legoproj/augdatatest/kps/"

PI = 3.1415

images = 4

millis = lambda: int(round(time.time() * 1000))
timestart = millis()

scene = bpy.context.scene
scene_objs = bpy.data.objects


def getMat(name):
    for mat in bpy.data.materials:
        if mat.name == name:
            return mat



'''
pole = scene_objs['Pole']
pole.data.materials.append(black)
pole.data.materials[0] = black 

brick = scene_objs['Brick']
brick.data.materials.append(gray)
brick.data.materials[0] = gray

wing = scene_objs['Wing']
wing.data.materials.append(lgray)
wing.data.materials[0] = lgray
'''

camera = bpy.data.objects['Camera']

#objs = {'Pole':[], 'Wing':[], 'Brick':[]}

random.seed()


black_shadeless = getMat("BlackShadeless")
white_shadeless = getMat("WhiteShadeless")
black = getMat("Black")

bck = bpy.data.objects['Background']
bck.data.materials.append(black_shadeless)
bck.data.materials.append(white_shadeless)

'''
def mltup(tup, num):
    return tuple(num * x for x in tup)

def add2tup(tup, num):
    return tuple(num + x for x in tup)

def addtups(tup1, tup2):
    return tuple(x + y for x,y in zip(tup1,tup2))

def objcopy(obj):
    newObj = obj.copy()
    newObj.data = obj.data.copy()
    scene.objects.link(newObj)
    return newObj
'''


'''
Rendering/masking methods
'''
'''
def shadeMasks(objects, mask_name, x):
    count = 0
    if len(objects[mask_name]) > 0:
        for key in objects:
            for obj in objects[key]:
                if key != mask_name:
                    mat = black_shadeless
                else:
                    mat = maskmats[count]
                    count = count + 1

                obj.hide = False
                obj.data.materials.append(mat)
                obj.active_material = mat
                obj.data.materials[0] = mat

        #scene.render.setBackgroundColor(0.0,0.0,0.0)
        bck.active_material = black_shadeless
        bck.data.materials[0] = black_shadeless

        scene.render.resolution_x = 64
        scene.render.resolution_y = 64
        scene.render.resolution_percentage = 100
                
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = write_path + str(x) + "_{}_".format(mode) + mask_name + ".png"
        bpy.ops.render.render(write_still = 1)
'''



"""
Wing generation and children placement

def gimme():
    return False if random.randint(0,2) == 0 else True

def genPiece(center, b):

    switch = random.randint(0,2)
    posm = (.7, .2, 0)
    obj = None

    #if (switch == 0):
    #    return '',None
    if not b:
        obj = objcopy(pole)# pole.duplicate()
        mult = random.randint(-1,1)
        obj.location = addtups( center , tuple(mult * x for x in posm) )
        pt = 90 if mult <= 0 else -90
        pt = pt + .7 * mult * 50
        obj.rotation_euler = (0,0, math.radians(pt))
        print("Generating pole")
        return 'Pole',obj
    else:
        obj = objcopy(brick)# brick.duplicate()
        pt = random.randint(0,20)/20
        obj.rotation_euler = (0,0,pt * PI)
        obj.location = addtups( center , mltup(posm,.6) )
        print("Generating brick")
        return 'Brick',obj

def genWing(center):

    print("Generating wing")
    b = False
    
    #if gimme() or gimme():
    newWing = objcopy(wing)# wing.copy()
    newWing.location = (0,0,0)
    newWing.rotation_euler = (0,0,0)
    objs["Wing"].append(newWing)
    newWing.parent = center

    ###region 1
    b = gimme()
    #if gimme():
    l, o = genPiece((0,2.6,.7),b)
    objs[l].append(o)
    o.parent = center

    ###region 2
    if gimme():
        l, o = genPiece((0,-1,.7))
        objs[l].append(o)
        o.parent = center
        
    ###region 3
    #if gimme():
    l, o = genPiece((-.9,-2.3,.7), not b)
    objs[l].append(o)
    o.parent = center
"""

pole = scene_objs["PolePts"]
studpts = []

print(pole)

for obj in bpy.data.objects:
    if obj.parent == pole:
        studpts.append(obj)


for pt in studpts:
    print(pt)
    pt.data.materials.append(white_shadeless)
    pt.data.materials[0] = white_shadeless
    pt.hide = True


for x in range(2000):
    for pt in studpts:
        pt.hide = True
        pt.hide_render = True

    
    pole.location = (random.randint(-1,1), random.randint(-1,1), 0)
    pole.rotation_euler = (0,0,PI/2*random.randint(-18,18)/18)

    camera.location = (random.randint(3,6) * -1 if random.randint(0,1) < 1 else 1, random.randint(3,6) * -1 if random.randint(0,1) < 1 else 1, random.randint(3,6))

    scene.render.resolution_x = 256
    scene.render.resolution_y = 256
    scene.render.resolution_percentage = 100

    bck.active_material = white_shadeless
    bck.data.materials[0] = white_shadeless

    pole.hide = False
    pole.hide_render = False
            
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = write_path + str(x) + "pole.png"
    bpy.ops.render.render(write_still = 1)

    scene.render.resolution_x = 256
    scene.render.resolution_y = 256
    scene.render.resolution_percentage = 100

    pole.hide = True
    pole.hide_render = True
    for pt in studpts:
        pt.hide = False
        pt.hide_render = False


    bck.active_material = black_shadeless
    bck.data.materials[0] = black_shadeless

    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = write_path + str(x) + "pts.png"
    bpy.ops.render.render(write_still = 1)

print("Generated " + str(x+1) + " images in " + str(float(millis() - timestart)/1000.0) + " seconds")