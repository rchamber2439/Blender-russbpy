#
# example_cylinder_and_sphere_grid.py - Show how to create a joined Cylinder and Sphere, then make a grid.
#
import re, os, sys, time
sys.path.append( os.getcwd() )

from russbpy import *
import bpy

import math
from random import randint, random

# Initialize the russbpy.py module.
# The one parameter sets the default fineness.
# The value of 100 means, for example, that
# Cylinders will have 100 faces by default.
Init( 100 )

# Create a red Cylinder.
c = Cylinder( name='My Cylinder', r=3.0, h=10.0 )
SetColor( c, Red )

# Create a yellow Sphere.
# Position its center at the top of the Cylinder.
s = Sphere( name='My Sphere', r=5.0, location=[ 0, 0, 5.0 ] )
SetColor( s, Yellow )

# Join the two objects.
# NOTE: Join() is MUCH preferred over the Union() Boolean operation,
#       because for the purposes of 3D printing, it doesn't matter
#       that two objects share parts of their volume. For any given
#       location in space, the printer will simply note
#       "there is stuff there", regardless of whether there is
#       one object or many objects.
#       You wil save a lot of CPU time and hassle by using
#       Join() instead of Union().
j = Join( c, s )

# Generate a 5x5 grid of objects.
# Note that after each Array() call, the input object
# now represents the entire array of objects, so
# the second Array() call makes an array of arrays.
Array( j, count=5, x_offset=15 )
Array( j, count=5, y_offset=15 )

# Finalize the russbpy.py module.
# The following files are written:
#    - example_cylinder_and_sphere_grid.blend  A Blender file containing the generated model.
#    - example_cylinder_and_sphere_grid.stl    An STL file, which may be used to make a 3D print.
#    - example_cylinder_and_sphere_grid.log    A log file containing lines log during the run.
Fini()
