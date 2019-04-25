#
# test.py - A simple test of russbpy.py
#
# 1) Edit blender.bat to point to your Blender 2.79 installation.
# 2) Run:
#         blender.bat test.py
#
import re, os, sys, time

sys.path.append( os.getcwd() )

from russbpy import *

base_r = 10.0
base_h = 1.0

cone_r = base_r
cone_h = base_h * 7.0

ball_r = base_r * 0.8

text_thickness = 1.0

Init( 100 )

base = Cylinder( name='base', r=base_r, h=base_h )
SetColor( base, Brown )

cone = Cone( name='cone', r=cone_r, h=cone_h )
TranslateZ( cone, base_h / 2.0 + cone_h / 2.0 )
SetColor( cone, Brown )

ball = Sphere( name='ball', r=ball_r )
TranslateZ( ball, base_h / 2.0 + cone_h + ball_r )
SetColor( ball, Green )

text = SphericalText( text='MADE_USING_CODE!', r=ball_r + text_thickness, thickness=text_thickness, angular_height=20.0 )
TranslateZ( text, base_h / 2.0 + cone_h + ball_r )
SetColor( text, Yellow )

Fini()
