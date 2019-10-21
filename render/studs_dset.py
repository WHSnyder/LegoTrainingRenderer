import bpy
import random
import math
import time
import numpy as np
import json
import mathutils as mu
import os
from math import degrees


write_path = "/Users/will/projects/legoproj/data/studs/"

PI = 3.1415

millis = lambda: int(round(time.time() * 1000))
timestart = millis()

scene = bpy.context.scene
scene_objs = bpy.data.objects

flat = scene_objs["Flat"]
stud = scene_objs["Bump"]
diag = scene_objs["Diag"]
camera = bpy.data.objects['Camera']
bck = bpy.data.objects['Background']


objs = [flat, stud, diag]

random.seed()


def objcopy(obj):
    newObj = obj.copy()
    newObj.data = obj.data.copy()
    scene.objects.link(newObj)

    return newObj


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

mats = [black, gray, lgray]
choices = len(mats)


def gimme():
    return False if random.randint(0,1) == 0 else True


def setMat(objects, mat):
	for obj in objs:
		obj.data.materials[0] = mat


def genGrid():

	h = random.randint(2,6)
	w = random.randint(2,6)
	u = .32

	sense = random.randint(0,5)

	init = u * np.asarray([0 - w/2, 0 - h/2, 0])

	count = 0
	objects = []

	setMat(objs, mats[random.randint(0,2)])
	bpy.context.scene.update()


	if sense == 0 or sense == 5:

		for i in range(w):
			for j in range(h):
				loc = init + np.asarray([u * i, u * j, 0])
				newstud = objcopy(stud)
				newstud.location = loc
				count += 1
				objects.append(newstud)

	else:

		for i in range(w):
			for j in range(h):
				choice = random.randint(0,sense)

				if choice == 0:
					newobj = objcopy(stud)
					count += 1 
				else:
					newobj = objcopy(flat)

				loc = init + np.asarray([u * i, u * j, 0])
				
				newobj.location = loc
				objects.append(newobj)


	bpy.context.scene.update()

	return count, objects




scene.render.resolution_x = 512
scene.render.resolution_y = 512
scene.render.resolution_percentage = 100

bpy.context.scene.update()

projection_matrix = camera.calc_matrix_camera(
        bpy.context.scene.render.resolution_x,
        bpy.context.scene.render.resolution_y)

bpy.context.scene.update()




num = 3000


renders = {}
renders["list"] = []


for x in range(num):


    camera.location = (random.randint(2,4) * -1 if random.randint(0,1) < 1 else 1, random.randint(2,4) * -1 if random.randint(0,1) < 1 else 1, random.randint(2,3))

    count, grid = genGrid()

    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100

    bck.data.materials[0] = white_shadeless

    bpy.context.scene.update()

    path = write_path + "{}.png".format(x)

    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = path
    bpy.ops.render.render(write_still = 1)


    for obj in grid:
        scene_objs.remove(obj, do_unlink=True)

    renders["list"].append(tuple([path, x, count]))


with open(write_path + "{}.json".format("dset"), 'w') as fp:
    json.dump(renders, fp)


print("Generated " + str(x+1) + " images in " + str(float(millis() - timestart)/1000.0) + " seconds")