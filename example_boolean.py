#
# example_boolean.py - Show how to use the Boolean operations: Difference, Intersection, Union.
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

r = 100.0
offset = 4.0 * r

# Create a pink cone.
c = Cone( name='My Cone', r=10.0, h=20.0 )
SetColor( c, Pink )

# Create a green pie slice.
p = Pie3D( name='My Pie', r=10.0, h=20.0, angle=45.0 )
SetColor( p, Green )

# Add the caption
t0 = Text( name='Caption 0', text='Two Objects', h=0.1 )
ScaleUniform( t0, 5.0 )
RotateDegX( t0, 90.0 )
TranslateY( t0, -15.0 )
SetColor( t0, Yellow )

# Show boolean difference.
# Delete the second object so we can see the hole left behind.
c1 = Duplicate( c )
p1 = Duplicate( p )
Difference( c1, p1, True )
TranslateX( c1, 40.0 )

# Add the caption
t1 = Text( name='Caption 1', text='Boolean\nDifference', h=0.1 )
ScaleUniform( t1, 5.0 )
RotateDegX( t1, 90.0 )
TranslateY( t1, -15.0 )
TranslateX( t1, 40.0 )
SetColor( t1, Yellow )

# Show boolean intersection.
# Delete the second object so we can see what is left.
c2 = Duplicate( c )
p2 = Duplicate( p )
Intersection( c2, p2, True )
TranslateX( c2, 80.0 )

# Add the caption
t2 = Text( name='Caption 2', text='Boolean\nIntersection', h=0.1 )
ScaleUniform( t2, 5.0 )
RotateDegX( t2, 90.0 )
TranslateY( t2, -15.0 )
TranslateX( t2, 80.0 )
SetColor( t2, Yellow )

# Show boolean union.
# Delete the second object so we can see what is left.
c3 = Duplicate( c )
p3 = Duplicate( p )
Union( c3, p3, True )
TranslateX( c3, 120.0 )

# Add the caption
t3 = Text( name='Caption 3', text='Boolean Union\n(One Object)', h=0.1 )
ScaleUniform( t3, 5.0 )
RotateDegX( t3, 90.0 )
TranslateY( t3, -15.0 )
TranslateX( t3, 120.0 )
SetColor( t3, Yellow )

# Finalize the russbpy.py module.
# The following files are written:
#    - example_boolean.blend  A Blender file containing the generated model.
#    - example_boolean.stl    An STL file, which may be used to make a 3D print.
#    - example_boolean.log    A log file containing lines log during the run.
Fini()
