#
# example_cylinder.py - Show how to create a Cylinder
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

# Create a Cylinder.
c = Cylinder( name='My Cylinder', r=3.0, h=10.0 )

# Finalize the russbpy.py module.
# The following files are written:
#    - example_cylinder.blend	A Blender file containing the generated model.
#    - example_cylinder.stl	An STL file, which may be used to make a 3D print.
#    - example_cylinder.log	A log file containing lines log during the run.
Fini()
