# -*- coding: utf-8 -*-
"""
This script is to convert the xml annotation files from ImageNet to appropriate
format needed by YOLO. 

Download the ILSVRC2015_devkit.tar.gz from the ImageNet competition website.
The class labels are at ILSVRC2015_devkit/devkit/data/map_det.txt or
map_clsloc.txt (depending on the task you're training on). These two files were
also made available in this folder.
"""

import xml.etree.ElementTree as ET
import pickle
import os, sys
from os import listdir, getcwd
from os.path import join

import numpy as np
import glob

map_clsloc = np.genfromtxt('ILSVRC2015_devkit/devkit/data/map_det.txt',
        delimiter=' ', dtype=None)

# tuple 'n07831146' to (999, 'carbonara')
code_to_class = {}
code_to_idx  = {}
class_to_idx = {}
class_to_code = {}
# object index should start from 0
for code, idx, cls in map_clsloc:
    code_to_class[code] = cls
    code_to_idx[code] = idx - 1
    
    class_to_idx[cls] = idx - 1
    class_to_code[cls] = code

def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

def convert_annotation(annot_dir, partition, cls_code, cls_idx):
    """
    Input:
     - annot_dir: path to the parent annotation dir
     - partition: 'train' or 'val'
     - cls_code: code representing a class
     - cls_idx: corresponding class index (DEPRECATED: not being used)

    Path example:
       ILSVRC2015/Annotations/CLS-LOC/train/n13133613/n13133613_1124.xml
       ILSVRC2015/Data/CLS-LOC/train/n13133613/n13133613_1124.JPEG
     for the validation images, replace 'train' by 'val'
    """
    cls_dir = os.path.join(annot_dir, partition, cls_code)
    print "Processing: {}".format(cls_dir)
    output_dir = 'labels/' + cls_code
    try:
        os.makedirs(output_dir)
    except OSError:
        pass

    xml_files = glob.glob(cls_dir + '/*')

    for xml_file in xml_files:
        in_file = open(xml_file)
        out_file = open(output_dir + '/' + os.path.splitext(os.path.basename(xml_file))[0] + '.txt', 'w')
        #out_file = open('VOCdevkit/VOC%s/labels/%s.txt'%(year, image_id), 'w')

        print " file: {}".format(xml_file)

        tree = ET.parse(in_file)
        root = tree.getroot()
        size = root.find('size')
        w = int(size.find('width').text)
        h = int(size.find('height').text)

        for obj in root.iter('object'):
            # difficult = obj.find('difficult').text
            cls = obj.find('name').text

            # cls can be either code or name, e.g:
            #   'n02100735_8212.xml': 'English_setter'
            #   'n02100735_11226.xml': 'n02100735'
            if cls in code_to_class.keys():
                cls_id = code_to_idx[cls]
            elif cls in class_to_code.keys():
                cls_id = class_to_idx[cls]
            else:
                print "Inexistent class {}".format(cls)
                continue

            # ignore difficult samples (not available for ImageNet)
            # if int(difficult) == 1:
            #     continue

            xmlbox = obj.find('bndbox')
            b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
            bb = convert((w,h), b)
            #print (str(cls_id) + " " + " ".join([str(a) for a in bb]))
            out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')


if __name__ == '__main__':

    # root path to the imagenet directory
    root_dir = 'ILSVRC2015'
    annot_dir = os.path.join(root_dir, 'Annotations/DET')
    data_dir = os.path.join(root_dir, 'Data/DET')

    for cls_code, cls_idx, cls_name in map_det:
        convert_annotation(annot_dir, 'train', cls_code, cls_idx)

