import bpy
import random
import json
import time
import numpy as np
import mathutils as mu
import sys

bpy.context.scene.update()


modes = ["sel", "pattern"]


option = 0
mode = modes[option]


scene = bpy.context.scene
scene_objs = bpy.data.objects

cur = bpy.context.selected_objects[0]
name = cur.name.split(".")[0]

data = {}
data["name"] = name


'''
bpy.context.scene.objects.active = wing
bpy.ops.object.mode_set(mode='EDIT', toggle=False)
bpy.ops.mesh.select_all(action='DESELECT')

sel_mode = bpy.context.tool_settings.mesh_select_mode
bpy.context.tool_settings.mesh_select_mode = [True, False, False]
bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
'''





mesh = cur.data
offset = mu.Vector((4,4,0)) 

verts = [] 

mode = bpy.context.active_object.mode
# we need to switch from Edit mode to Object mode so the selection gets updated
bpy.ops.object.mode_set(mode='OBJECT')
selected_verts = [v for v in bpy.context.active_object.data.vertices if v.select]

#print(len(selected_verts))


if "Engine" in name:
	for i in range(0,len(selected_verts),2):
		print(i)
		v1,v2 = selected_verts[i],selected_verts[i+1]
		v = (v1.co+v2.co)/2

		tup = (v[0],v[1],v[2])
		verts.append(tup)

else:
	for vert in selected_verts:
	    coord = vert.co
	    tup = (coord[0], coord[1], coord[2])
	    verts.append(tup)


data["studs"] = verts


'''
for vert in mesh.vertices:
    coord = 100*vert.co
    if abs(coord[2] - 6.4) < .00001:
        if abs(coord[0] % 8) < .00001 and abs(coord[1] % 8) < .00001:
            verts.append(vert.co)
'''


with open("/home/will/projects/training/piecedata/{}.json".format(name),"w") as fp:
    json.dump(data, fp)


'''
bpy.ops.object.mode_set(mode='EDIT', toggle=False)
bpy.context.tool_settings.mesh_select_mode = sel_mode
'''