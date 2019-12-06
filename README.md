# Lego Renderer for Machine Learning Projects


A set of Python scripts/Blender utilities for rendering Lego scenes for use in deep learning/computer vision projects.
Includes a basic scene with a tracked camera, scripts for rendering images, normals, masks of Lego combinations, and utilities for recording the positions of special features on different pieces (studs, corners, holes) easily.


![alt text](./repo_images/renders.gif "Rendering")


![alt text](./repo_images/0000_tst.gif "render1")  ![alt text](./repo_images/0001_tst.gif "mask1")  ![alt text](./repo_images/0002_tst.gif "normals1")  ![alt text](./repo_images/0003_tst.gif "masks1")


![alt text](./repo_images/0000_masks.gif "0")  ![alt text](./repo_images/0001_masks.gif "1")  ![alt text](./repo_images/0002_masks.gif "2")  ![alt text](./repo_images/0003_masks.gif "3")


## Folders and Files:

* render
  * renderbench.blend: Blend file containing a camera view-locked to the center of the scene and a surface with an adjustable image texture.  Also comes with a compositor rigged for rendering depth, normals, and mask layers to EXR files.

  * combo_dset.py: Script for rendering images of Lego structure permutations.  Works by hiding a random subset of pieces in the scene, randomly setting the material values of the visible pieces, and randomly setting the camera position and lighting.  Each rendering script records the scene layout, object matrices, camera view and frustum matrices for each render, and object mask values. This data is saved to path/dset.json post-rendering.

* utils
  * record_studs.py: To record the locations of studs or other meaningful features on each piece, select them (vertices) in edit mode and run this script

  * feature_utils.py: Scripts for reading matrices from json files, projecting coordinates given render matrices, checking features for occlusion/self-occlusion.   

* dataprep
  * seperate_masks.py: Functions for separating the rendered masks by hue according to the json file generated during rendering.  Generates a new json file linking each render with its masks.  Run with -p pathtojson/dset.json.

  * coco_prepare.py: Functions for gathering renders and separated masks into a COCO dataset, given the json files generated from separate_masks.py.  Run with -p pathtojson_0/dset_withmasks.json pathtojson_1/dset_withmasks.json pathtojson_etc/dset_withmasks.json -t tag (val,test,train,etc). 

* piecedata
    * Folder containing coordinates of meaningful features in json files, obj files of pieces, etc.


## Requirements:

* [OpenEXR Python libraries](https://github.com/jamesbowman/openexrpython) (pip install git+https://github.com/jamesbowman/openexrpython.git  <-- that command works most reliably...)
* Blender not 2.8
* Python 3


This project should be useful to people interested in generating high quality training data of Lego pieces.  I think Lego will play a very important role in the development of artificial intelligence over the next 10 years.  The need for both fuzzy logic (visual pattern recognition, keypoints, occlusion robustness) and structured reasoning (voxelized understanding of pieces, symmetry-robust pose estimation) is something current deep learning approaches struggle with.  Once these dynamics are reliably understood, solutions to robotics problems involving highly subtle movement could be explored with Lego.


## Note: If importing pieces from Leocad/LDRAW scale them down by .016


## To Do:

* Blender 2.8 support

* Add menus/widgets as part of an actual addon