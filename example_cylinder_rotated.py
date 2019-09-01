#
# example_cylinder_rotation.py - Show how to create a Cylinder and rotate duplicates of it.
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

# Create a yellow Cylinder.
c = Cylinder( name='My Cylinder', r=5.0, h=100.0 )
SetColor( c, Yellow )

# Rotate duplicates of the cylinder.
count = 10
for i in range( 1, count ):
    d = Duplicate( c )
    RotateDegY( d, ( 360.0 / float( 2 * count ) ) * float( i ) )

# Finalize the russbpy.py module.
# The following files are written:
#    - example_cylinder_rotation.blend  A Blender file containing the generated model.
#    - example_cylinder_rotation.stl    An STL file, which may be used to make a 3D print.
#    - example_cylinder_rotation.log    A log file containing lines log during the run.
Fini()
