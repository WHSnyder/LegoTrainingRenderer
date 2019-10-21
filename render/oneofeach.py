import bpy
import random
import math
import time
import numpy as np


from math import degrees



mode = "orbtest"
write_path = "/Users/will/projects/legoproj/orb_matching/"#data_oneofeach/{}_oneofeach/".format(mode)



PI = 3.1415



images = 4

millis = lambda: int(round(time.time() * 1000))
timestart = millis()

scene = bpy.context.scene
scene_objs = bpy.data.objects


black = bpy.data.materials.new(name="Black")
black.diffuse_color = (.1,.1,.1)

gray = bpy.data.materials.new(name="Gray")
gray.diffuse_color = (.5,.5,.5)

lgray = bpy.data.materials.new(name="LightGray")
lgray.diffuse_color = (.8,.8,.8)

blue = bpy.data.materials.new(name="Blue")
blue.diffuse_color = (0.0,0.0,1.0)

maskmats = []
for x in range(0,10):
    m = 1 - (x/5)
    mask = bpy.data.materials.new(name="White" + str(x))
    mask.diffuse_color = (m,m,m)
    mask.use_shadeless = True
    maskmats.append(mask)

white_shadeless = bpy.data.materials.new(name="WhiteShadeless")
white_shadeless.diffuse_color=(1.0,1.0,1.0)
white_shadeless.use_shadeless = True


black_shadeless = bpy.data.materials.new(name="BlackShadeless")
black_shadeless.diffuse_color = (0.0,0.0,0.0)
black_shadeless.use_shadeless = True

#pole = scene.data.objects['Pole']
pole = scene_objs['Pole']
pole.data.materials.append(black)
pole.data.materials[0] = black 
#pole.active_material = black

#brick = bpy.data.objects['Brick']
brick = scene_objs['Brick']
brick.data.materials.append(gray)
brick.data.materials[0] = gray
#pole.active_material = gray 

#wing = bpy.data.objects['Wing']
wing = scene_objs['Wing']
wing.data.materials.append(lgray)
wing.data.materials[0] = lgray
#wing.active_material = lgray

camera = bpy.data.objects['Camera']

objs = {'Pole':[], 'Wing':[], 'Brick':[]}

random.seed()

bck = bpy.data.objects['Background']
bck.data.materials.append(black_shadeless)
bck.data.materials.append(maskmats[0])


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
Rendering/masking methods
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
Wing generation and children placement
'''

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
    """
    ###region 1
    b = gimme()
    #if gimme():
    l, o = genPiece((0,2.6,.7),b)
    objs[l].append(o)
    o.parent = center
    '''###region 2
    if gimme():
        l, o = genPiece((0,-1,.7))
        objs[l].append(o)
        o.parent = center
        '''
    ###region 3
    #if gimme():
    l, o = genPiece((-.9,-2.3,.7), not b)
    objs[l].append(o)
    o.parent = center
    """



c1 = bpy.data.objects.new("empty", None)
bpy.context.scene.objects.link(c1)

c2 = bpy.data.objects.new("empty", None)
bpy.context.scene.objects.link(c2)

#print(bck)

for x in range(1):

    c1.location = (0,0,0)
    c2.location = (0,0,0)
    '''
    if gimme():
        w1 = genWing(c1)
        c1.location = (2 * random.randint(-1,1), -2, 0)
        c1.rotation_euler = (0,0,PI/2*random.randint(-18,18)/18)


        w2 = genWing(c2)
        c2.location = (2 * random.randint(-1,1), 2, 0)
        c2.rotation_euler = (0,0,PI/2*random.randint(-18,18)/18) 
    '''       
    #else:
    w2 = genWing(c2)
    #c2.location = (random.randint(-1,1), random.randint(-1,1), 0)
    c2.rotation_euler = (0,0,PI/2*random.randint(-18,18)/18)

    camera.location = (random.randint(10,11) * -1 if random.randint(0,1) < 1 else 1, random.randint(10,11) * -1 if random.randint(0,1) < 1 else 1, random.randint(9,15))

    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100

    #scene.render.setBackgroundColor(1.0,1.0,1.0)
    bck.active_material = maskmats[0]
    bck.data.materials[0] = maskmats[0]

            
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = write_path + str(x) + "_{}_a.png".format(mode)
    bpy.ops.render.render(write_still = 1)

    for key in objs:
        if key != "":
            shadeMasks(objs, key, x)
    for key in objs:
        for obj in objs[key]:
            print("wiping")
            scene_objs.remove(obj, do_unlink=True)
        objs[key].clear()


print("Generated " + str(x+1) + " images in " + str(float(millis() - timestart)/1000.0) + " seconds")
scene_objs.remove(c1, do_unlink=True)
scene_objs.remove(c2, do_unlink=True)
 

'''
text_file = open("/Users/will/projects/legoproj/regtest/labels.txt", "w")
text_file.write(labels)
text_file.close() 
'''   