#
# example_toris_clipped.py - Show how to create a Torus and clip it.
#
import re, os, sys, time
sys.path.append( os.getcwd() )

from russbpy import *
import bpy

import math
from random import randint, random

# Initialize the russbpy.py module.
# The one parameter sets the default fineness.
# The value of 50 means, for example, that
# Cylinders will have 50 faces by default.
Init( 50 )

r = 100.0
offset = 4.0 * r

# Create a purple Torus.
t = Torus( name='My Torus', major_radius=r, minor_radius=30.0 )
SetColor( t, Purple )

for x in range( -1, 2 ):
    for y in range( -1, 2 ):
        for z in range( -1, 2 ):
            d = Duplicate( t )
            Clip( d, x=x, y=y, z=z )
            Translate( d, x=-offset * x, y=-offset * y, z=-offset * z )

# Delete the original torus, as one of the copies duplicates it exactly.
Delete( t )

# Finalize the russbpy.py module.
# The following files are written:
#    - example_toris_clipped.blend  A Blender file containing the generated model.
#    - example_toris_clipped.stl    An STL file, which may be used to make a 3D print.
#    - example_toris_clipped.log    A log file containing lines log during the run.
Fini()
