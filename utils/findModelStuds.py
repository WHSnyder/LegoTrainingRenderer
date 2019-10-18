import bpy
import random
import json
import time
import numpy as np
import mathutils as mu
import sys


modes = ["sel", "pattern"]
name = 'Brick'


option = 0
mode = modes[option]


scene = bpy.context.scene
scene_objs = bpy.data.objects


cur = scene_objs[name]
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
selected_verts = [v for v in mesh.vertices if v.select]


if len(selected_verts) == 0:
    sys.exit()


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


with open("/Users/will/projects/legoproj/pieces/{}.json".format(name),"w") as fp:
    json.dump(data, fp)


'''
bpy.ops.object.mode_set(mode='EDIT', toggle=False)
bpy.context.tool_settings.mesh_select_mode = sel_mode
'''