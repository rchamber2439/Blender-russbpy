#
# example_cylinder_rotation_with_set_origin.py - Show how to create a Cylinder, set its origin,
#                                                then rotate duplicates of it.
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

# Translate (move) the cylinder up in the Z-axis.
TranslateZ( c, 150.0 )

# Set the origin of the object to the origin of the world.
# Now the rotations will rotate the cylinder around
# the center of the world instead of the center
# of the object.
SetOriginOrigin( c )

# Rotate duplicates of the cylinder.
count = 30
for i in range( 1, count ):
    d = Duplicate( c )
    RotateDegY( d, ( 360.0 / count ) * float( i ) )

# Finalize the russbpy.py module.
# The following files are written:
#    - example_cylinder_rotation_with_set_origin.blend  A Blender file containing the generated model.
#    - example_cylinder_rotation_with_set_origin.stl    An STL file, which may be used to make a 3D print.
#    - example_cylinder_rotation_with_set_origin.log    A log file containing lines log during the run.
Fini()
