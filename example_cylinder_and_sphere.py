#
# example_cylinder_and_sphere.py - Show how to create a Cylinder and a Sphere.
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

# Finalize the russbpy.py module.
# The following files are written:
#    - example_cylinder_and_sphere.blend  A Blender file containing the generated model.
#    - example_cylinder_and_sphere.stl    An STL file, which may be used to make a 3D print.
#    - example_cylinder_and_sphere.log    A log file containing lines log during the run.
Fini()
