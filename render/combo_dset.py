import bpy
import random
import math
import time
import numpy as np
import json
import mathutils as mu
import os


from math import degrees


mode = "test"

write_path = "/Users/will/projects/legoproj/data_oneofeach/{}_oneofeach/".format(mode)

PI = 3.1415

millis = lambda: int(round(time.time() * 1000))
timestart = millis()

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
pole = scene_objs['Pole']
brick = scene_objs['Brick']
wing = scene_objs['Wing']
camera = bpy.data.objects['Camera']

objs = {'Pole':[], 'Wing':[], 'Brick':[]}

random.seed()


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



scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.resolution_percentage = 100

bpy.context.scene.update()

projection_matrix = camera.calc_matrix_camera(
        bpy.context.scene.render.resolution_x,
        bpy.context.scene.render.resolution_y)

bpy.context.scene.update()



'''
Rendering/masking methods
'''

def shadeMasks(objects, x, objdata):

    bck.data.materials[0] = black_shadeless

    for key in objects:
        for obj in objects[key]:
            obj.data.materials[0] = black_shadeless

    for key in objects:
        count = 0
        for obj in objects[key]:
            obj.data.materials[0] = white_shadeless
            
            scene.render.resolution_x = 64
            scene.render.resolution_y = 64
            scene.render.resolution_percentage = 100
                    
            scene.render.image_settings.file_format = 'PNG'
            scene.render.filepath = write_path + str(x) + "_" + mode + "_" + obj.name.replace(".","_") + ".png"
            bpy.ops.render.render(write_still = 1)
            count+=1

            obj.data.materials[0] = black_shadeless

            objdata[obj.name] = str(obj.matrix_world)



'''
Wing generation and children placement
'''

def gimme():
    return False if random.randint(0,2) == 0 else True

def genPiece(center):

    switch = random.randint(0,2)
    posm = (.7, .2, 0)
    obj = None

    if gimme():
        obj = objcopy(pole)
        mult = random.randint(-1,1)
        obj.location = addtups( center , tuple(mult * x for x in posm) )
        
        pt = 90 if mult <= 0 else -90
        pt = pt + .7 * mult * 50
        
        obj.rotation_euler = (0,0, math.radians(pt))

        return 'Pole', obj

    else:
        obj = objcopy(brick)
        pt = random.randint(0,20)/20
        
        obj.rotation_euler = (0,0,pt * PI)
        obj.location = addtups( center , mltup(posm,.6) )

        return 'Brick', obj



def genWing(center):

    print("Generating wing")
    
    if True or gimme() or gimme():
        newWing = objcopy(wing)
        newWing.location = (0,0,0)
        newWing.rotation_euler = (0,0,0)
        objs["Wing"].append(newWing)
        newWing.parent = center  
        newWing.matrix_parent_inverse = center.matrix_world.inverted()
    
     
    
    if gimme():
        l, o = genPiece((0,1.6,.7))
        objs[l].append(o)
        o.parent = center
        o.matrix_parent_inverse = center.matrix_world.inverted()
        
    
    if gimme():
        l, o = genPiece((0,-.7,.7))
        objs[l].append(o)
        o.parent = center
        o.matrix_parent_inverse = center.matrix_world.inverted()

    if gimme():
        l, o = genPiece((-.6,-1.6,.7))
        objs[l].append(o)
        o.parent = center
        o.matrix_parent_inverse = center.matrix_world.inverted()
    

    bpy.context.scene.update()



c1 = bpy.data.objects.new("empty", None)
bpy.context.scene.objects.link(c1)

c2 = bpy.data.objects.new("empty", None)
bpy.context.scene.objects.link(c2)

num = 100



os.system("rm " + write_path + "*.png")

if not os.path.exists(write_path + "mats/"):
    os.mkdir(write_path + "mats/")
else:
    os.system("rm " + write_path + "mats/*")



for x in range(num):

    objdata = {}

    c1.location = (0,0,0)
    c2.location = (0,0,0)
    
    if gimme():
        w1 = genWing(c1)
        c1.rotation_euler = (0,0,PI/2*random.randint(-18,18)/18)
        c1.location = (-3, 2 * random.randint(-1,1), 0)

        w2 = genWing(c2)
        c2.rotation_euler = (0,0,PI/2*random.randint(-18,18)/18)
        c2.location = (3, 2 * random.randint(-1,1), .7)

        camera.location = (random.randint(6,11) * -1 if random.randint(0,1) < 1 else 1, random.randint(6,11) * -1 if random.randint(0,1) < 1 else 1, random.randint(12,13))
    
    else:
        w2 = genWing(c2)
        c2.location = (.3 * random.randint(-1,1), .3 * random.randint(-1,1), 0)
        c2.rotation_euler = (0,0,PI/2*random.randint(-18,18)/18)

    camera.location = (random.randint(5,7) * -1 if random.randint(0,1) < 1 else 1, random.randint(5,7) * -1 if random.randint(0,1) < 1 else 1, random.randint(6,7))

    bpy.context.scene.update()

    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100

    bck.data.materials[0] = white_shadeless

    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = write_path + str(x) + "_" + mode + "_a" + ".png"
    bpy.ops.render.render(write_still = 1)

    cammat = camera.matrix_world.copy()

    objdata["Camera"] = str(cammat.inverted())
    objdata["Projection"] = str(projection_matrix)

    shadeMasks(objs,x, objdata)
    
    for key in objs:
        for obj in objs[key]:
            print("wiping")
            scene_objs.remove(obj, do_unlink=True)
        objs[key].clear()
    

    with open(write_path + "mats/" + str(x) + ".txt", 'w') as fp:
        json.dump(objdata, fp)


print("Generated " + str(x+1) + " images in " + str(float(millis() - timestart)/1000.0) + " seconds")
scene_objs.remove(c1, do_unlink=True)
scene_objs.remove(c2, do_unlink=True)