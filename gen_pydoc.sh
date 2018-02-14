#!/bin/bash

mkdir -p tmp
cd tmp
cp ../russbpy.py russbpy.tmp
sed "/import bpy/d" russbpy.tmp > russbpy.tmp2
sed "/from mathutils/d" russbpy.tmp2 > russbpy.py
pydoc -w russbpy
cp *.html ..
cd ..
