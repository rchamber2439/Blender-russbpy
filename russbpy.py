"""
russbpy.py - Russ Chamberlain's set of Blender Python extensions.

NOTE:
- There are NO measurement units specified in this API.
  The concept of units (eg. mm vs. inches) is usually only relevant to the
  slicer that prepares a *.stl file for printing.

#########################################
#########################################
TODO:
- Remove my own Vector and replace it with the mathutils Vector
- Add matrix-based functions to manipulate objects
#########################################
#########################################
"""

import bpy
import math
import os
import sys
import time
from random import random, randint

from mathutils import Matrix
from mathutils import Vector as Vec

# russbpy_modnum_gen - The global modifier number generator.
#
russbpy_modnum_gen = 1

# russbpy_fn - The global "fineness" factor. This is used to set the number of facets in a cylinder, sphere, etc.
#
russbpy_fn=32

# russbpy_transform_metatdata - Set to True to switch between Edit and Object mode and transform the object's metadata.
#                               Only set this, via SetTransformMetadata(), if you _know_ what you are doing!
russbpy_transform_metatdata=False

# russbpy_quiet - Set to True to prevent output to the console from the Print() function
#
russbpy_quiet = False

# russbpy_start_time - The last time the Init() function was called.
#
russbpy_start_time = 0

# russbpy_last_time - The last time the Elapsed() function was called.
#
russbpy_last_time = 0

#################################################
# Colors
#################################################

Red     =(1.0,0.0,0.0)
Green   =(0.0,1.0,0.0)
Blue    =(0.0,0.0,1.0)
White   =(1.0,1.0,1.0)
Black   =(0.0,0.0,0.0)
Grey    =(0.5,0.5,0.5)
Cyan    =(0.0,1.0,1.0)
Magenta =(1.0,0.0,1.0)
Yellow  =(1.0,1.0,0.0)
Orange  =(1.0,0.647058823529,0.0)
Purple  =(0.545098039216,0,0.545098039216)
Pink    =(1.0,0.411764705882,0.705882352941)
Brown   =(0.545098039216,0.270588235294,0.0745098039216)

"""Colours

Red, Green, Blue, White, Black, Grey, Cyan, Magenta, Yellow, Orange, Purple, Pink, Brown
"""

Colors = [
    Red,
    Green,
    Blue,
    White,
    Black,
    Grey,
    Cyan,
    Magenta,
    Yellow,
    Orange,
    Purple,
    Pink,
    Brown,
]

# russbpy_color - The current color, used if no color is specified.
#
russbpy_color=Green

#################################################
# Materials
#################################################
class Shapeways_StrongAndFlexiblePlasticUnpolished:
    def __init__( self, factor = 1.0 ):
        self.min_supported_wall_mm 		= 0.7 * factor
        self.min_unsupported_wall_mm 		= 0.7 * factor

        self.min_supported_wire_mm 		= 0.8 * factor
        self.min_unsupported_wire_mm 		= 1.0 * factor

        self.min_embossed_detail_width_mm 	= 0.2 * factor
        self.min_embossed_detail_height_mm 	= 0.5 * factor

        self.min_engraved_detail_width_mm 	= 0.2 * factor
        self.min_engraved_detail_height_mm 	= 0.5 * factor

        self.min_escape_hole_diameter_mm 	= 4.0 * factor

        self.clearance_mm 			= 0.5 * factor


#################################################
# 2D Shapes
#################################################

def CirclePoints( r=1, vertices=10, location=(0,0,0) ):
    """Create a set of points on a circle in the XY plane

    Keyword arguments:
    r        -- The radius
    vertices -- The number of vertices to use in the polygon approximation of the circle
    location -- The location of the center of the circle

    Return the list of vertices
    """
    angle = ( 2.0 * math.pi ) / vertices

    verts = []
    # Top
    r = float( r )
    for i in range( 0, vertices ):
        x = r * math.cos( angle * i )
        y = r * math.sin( angle * i )
        verts.append( [ location[0] + x, location[1] + y, location[2] ] )

    return verts

def Circle( name=None, r=1, vertices=None, location=(0,0,0) ):
    """Draw a circle in the XY plane and return the corresponding object

    Keyword arguments:
    name     -- The name for the new circle object
    r        -- The radius
    vertices -- The number of vertices to use in the polygon approximation of the circle
    location -- The location of the center of the circle

    Return the circle object
    """
    if vertices is None:
        vertices = russbpy_fn
    bpy.ops.mesh.primitive_circle_add( radius=r, vertices=vertices, location=location )
    ob = bpy.context.object
    if name is not None:
        ob.name = name
    return( ob )

def Plane( name=None, location=(0,0,0), size=1.0 ):
    """Draw a plane in the XY plane and return the corresponding object
    The plane is 2 units by 2 units, extending one unit in each of the X, -X, Y and -Y directions

    Keyword arguments:
    name     -- The name for the new plane object
    location -- The location of the center of the plane
    size     -- The size factor to scale the plane with

    Return the plane object
    """
    bpy.ops.mesh.primitive_plane_add( location=location )
    ob = bpy.context.object
    if name is not None:
        ob.name = name
    ScaleUniform( ob, size )
    return( ob )

def NGon( name=None, r=1.0, sides=8, location=(0,0,0) ):
    """Draw a regular N-gon in the XY plane and return the corresponding object

    The first vertex is at (r,0,0) relative to the location.

    Keyword arguments:
    name     -- The name for the new N-gon object
    r        -- The outer radius of the N-gon, ie. measured at the vertices
    sides    -- The number of sides on the N-gon
    location -- The location of the center of the N-gon

    Return the N-gon object
    """

    verts = CirclePoints( r, sides, location )
    verts.append( [ location[0], location[1], location[2] ] )

    faces = []
    for i in range( 0, sides ):
        l = i
        r = ( ( i + 1 ) % sides )
        faces.append( [ l, r, sides ] )

    return Mesh( name, verts, [], faces )

def Square( name=None, size=1.0, location=(0,0,0) ):
    """Draw a square in the XY plane and return the corresponding object

    Keyword arguments:
    name     -- The name for the new N-gon object
    size     -- The length of the sides
    location -- The location of the center of the square

    Return the square object
    """

    n = NGon( r=math.sqrt( side * side / 2.0 ), sides=4 )
    Select( n )
    # Align the square with the axes
    RotateDegZ( n, 45 )
    TranslateV( n, location )
    return n

def ZigZag( name=None, segments=5, angle_max=30.0, x1=0, y1=0, x2=1, y2=1 ):
    """Draw a random zigag path of line segments from (x1,y1,0) to (x2,y2,0) and return the corresponding object

    Keyword arguments:
    name      -- The name for the new zigzag object
    segments  -- The number of line segments
    angle_max -- The maximum number of degrees to zig or zag between each segment
    x1        -- The starting X coordinate
    y1        -- The starting y coordinate
    x2        -- The ending X coordinate
    y2        -- The ending y coordinate

    Return the zigzag object
    """

    angle_max_rad = DegToRad( angle_max )
    d = Distance( x1, y1, 0, x2, y2, 0 )
    step = d / float( segments )
    verts = [ [ x1, y1, 0 ] ]
    edges = []
    for i in range( 0, segments - 1 ):
        # Move randomly towards the endpoint.
        # Determine the vector to the endpoint,
        # then use that vector as the middle possibility
        # of a random vector within the angle_max.
        xi = verts[i][0]
        yi = verts[i][1]
        d = Distance( xi, yi, 0, x2, y2, 0 )
        dx = x2 - xi
        dy = y2 - yi
        old_theta = math.asin( dy / d )
        new_theta = old_theta + angle_max_rad * ( random() - 0.5 )

        xj = xi + math.cos( new_theta ) * step
        yj = yi + math.sin( new_theta ) * step

        verts.append( [ xj, yj, 0 ] )
        edges.append( [ i, i + 1 ] )

    verts.append( [ x2, y2, 0 ] )
    edges.append( [ segments - 1, segments ] ) 
    return Mesh( name=name, verts=verts, edges=edges )

#################################################
# 3D Shapes
#################################################

def Sphere( name=None, r=1, segments=None, rings=None, location=(0,0,0) ):
    """Draw a solid sphere and return the corresponding object

    Keyword arguments:
    name      -- The name for the new sphere object
    r         -- The radius
    segments  -- The number of vertical segments (like beach-ball panels)
    rings     -- The number of rings (horizontal slices)
    location  -- The location of the center of the sphere

    Return the sphere object
    """
    if segments is None:
        segments = russbpy_fn
    if rings is None:
        rings = int( russbpy_fn / 2 )
    bpy.ops.mesh.primitive_uv_sphere_add( size=r, segments=segments, ring_count=rings, location=location )
    ob = bpy.context.object
    if name is not None:
        ob.name = name
    return( ob )

def MeshSphere( name=None, r=1.0, latitudes=11, longitudes=10, location=(0,0,0), quads=True ):
    """Draw a solid sphere and with evenly-spaced faces

    Keyword arguments:
    name       -- The name for the new sphere object
    r          -- The radius
    latitudes  -- The number of vertical latitude lines
    longitudes -- The number of rings (horizontal slices)
    location   -- The location of the center of the sphere
    quads      -- Use quads or triangles?

    Return the sphere object
    """
    # Latitudes excludes the poles, and must be odd.
    latitudes = latitudes + ( 1 - latitudes % 2 )
    r_steps = float( r ) / float( longitudes )

    verts = []
    faces = []

    # The first 0 .. longitudes-1 points are the equator
    equator_verts = CirclePoints( r, longitudes, location=(location[0],location[1],location[2]) )
    for v in equator_verts:
        verts.append( v )

    # Build the upper hemisphere, cross-section by cross-section.
    # Given the latitude angle, the cross-section radius is:
    #     csr / r = cos( lat_angle )
    #         csr = cos( lat_angle ) * r
    # Given the latitude angle, the height of the cross-section radius is:
    #     csh / csr = tan( lat_angle )
    #           csh = tan( lat_angle ) * csr
    hem_lats = int( latitudes / 2 )
    lat_angle = 90.0 / float( hem_lats + 1 )
    for li in range( 1, hem_lats ):
        csr = Cos( li * lat_angle ) * r
        csh = Tan( li * lat_angle ) * csr
        cs_verts = CirclePoints( csr, longitudes, location=(location[0],location[1],location[2]+csh) )

        if li == 1 :
            # Faces connecting to the equator
            for longi in range( 0, longitudes ):
                if quads:
                    faces.append( ( longi,
                                    ( longi + 1 ) % longitudes,
                                    len( verts ) + ( longi + 1 ) % longitudes,
                                    len( verts ) + longi ) )
                else:
                    faces.append( ( longi,
                                    ( longi + 1 ) % longitudes,
                                    len( verts ) + ( longi + 1 ) % longitudes ) )
                    faces.append( ( len( verts ) + ( longi + 1 ) % longitudes,
                                    len( verts ) + longi,
                                    longi ) )
        if li < hem_lats - 1:
            for longi in range( 0, longitudes ):
                if quads:
                    faces.append( ( len( verts ) + longi,
                                    len( verts ) + ( longi + 1 ) % longitudes,
                                    len( verts ) + longitudes + ( longi + 1 ) % longitudes,
                                    len( verts ) + longitudes + longi ) )
                else:
                    faces.append( ( len( verts ) + longi,
                                    len( verts ) + ( longi + 1 ) % longitudes,
                                    len( verts ) + longitudes + ( longi + 1 ) % longitudes ) )
                    faces.append( ( len( verts ) + longitudes + ( longi + 1 ) % longitudes,
                                    len( verts ) + longitudes + longi,
                                    len( verts ) + longi ) )
        else:
            for longi in range( 0, longitudes ):
                faces.append( ( len( verts ) + longi,
                                len( verts ) + ( longi + 1 ) % longitudes,
                                len( verts ) + longitudes ) )
        for v in cs_verts:
            verts.append( v )

    verts.append( ( location[0], location[1], location[2] + r ) )

    # Build the lower hemisphere, cross-section by cross-section.
    # Given the latitude angle, the cross-section radius is:
    #     csr / r = cos( lat_angle )
    #         csr = cos( lat_angle ) * r
    # Given the latitude angle, the height of the cross-section radius is:
    #     csh / csr = tan( lat_angle )
    #           csh = tan( lat_angle ) * csr
    hem_lats = int( latitudes / 2 )
    lat_angle = 90.0 / float( hem_lats + 1 )
    for li in range( 1, hem_lats ):
        csr = Cos( li * lat_angle ) * r
        csh = Tan( li * lat_angle ) * csr
        cs_verts = CirclePoints( csr, longitudes, location=(location[0],location[1],location[2]-csh) )

        if li == 1 :
            # Faces connecting to the equator
            for longi in range( 0, longitudes ):
                if quads:
                    faces.append( ( len( verts ) + longi,
                                    len( verts ) + ( longi + 1 ) % longitudes,
                                    ( longi + 1 ) % longitudes,
                                    longi ) )
                else:
                    faces.append( ( len( verts ) + longi,
                                    len( verts ) + ( longi + 1 ) % longitudes,
                                    ( longi + 1 ) % longitudes ) )
                    faces.append( ( ( longi + 1 ) % longitudes,
                                    longi,
                                    len( verts ) + longi ) )
        if li < hem_lats - 1:
            for longi in range( 0, longitudes ):
                if quads:
                    faces.append( ( len( verts ) + longitudes + longi,
                                    len( verts ) + longitudes + ( longi + 1 ) % longitudes,
                                    len( verts ) + ( longi + 1 ) % longitudes,
                                    len( verts ) + longi ) )
                else:
                    faces.append( ( len( verts ) + longitudes + longi,
                                    len( verts ) + longitudes + ( longi + 1 ) % longitudes,
                                    len( verts ) + ( longi + 1 ) % longitudes ) )
                    faces.append( ( len( verts ) + ( longi + 1 ) % longitudes,
                                    len( verts ) + longi,
                                    len( verts ) + longitudes + longi ) )
        else:
            for longi in range( 0, longitudes ):
                faces.append( ( len( verts ) + longitudes,
                                len( verts ) + ( longi + 1 ) % longitudes,
                                len( verts ) + longi ) )
        for v in cs_verts:
            verts.append( v )

    verts.append( ( location[0], location[1], location[2] - r ) )

    ob = Mesh( name, verts, [], faces )

    return ob

def SpiralPointsOnSphere( r=1, num_loops=3, points_per_loop=10, clockwise=False ):
    """Return an array of 3D points that spiral around a sphere from pole to pole.

    Keyword arguments:
    r               -- The radius of the sphere
    num_loops       -- The number of 360-degree loops in the spiral
    points_per_loop -- The number of points per loop
    clockwise       -- Use clockwise traversal? (set to False for counter-clockwise)

    return the array of points (size is num_loops x points_per_loop)
    """
    r = float( r )

    # Traverse the sphere from pole to pole, ie. 180 degrees.
    num_points = num_loops * points_per_loop + 1
    vert_step = float( 180.0 / float( num_points ) )
    loop_step = float( 360.0 / float( points_per_loop ) )
    if clockwise:
        loop_step *= -1.0

    points = []
    vert_angle = float( 90.0 )
    loop_angle = float( 0.0 )
    for l in range( 0, num_loops ):
        for p in range( 0, points_per_loop ):
            # Calculate the spherical position based on: ( r, vert_angle, loop_angle )
            curr_r = r * Cos( vert_angle )
            x = curr_r * Cos( loop_angle )
            y = curr_r * Sin( loop_angle )
            z = r * Sin( vert_angle )

            points.append( ( x, y, z ) )

            loop_angle += loop_step
            vert_angle += vert_step

    points.append( ( 0, 0, -r ) )

    return points

def Torus( name=None, major_radius=1, minor_radius=.25, major_segments=None, minor_segments=None, location=(0,0,0) ):
    """Draw a solid torus in the XY plane and return the corresponding object

    Keyword arguments:
    name            -- The name for the new torus object
    major_radius    -- The radius to the center of the extruded circle forming the torus
    minor_radius    -- The radius of the extruded circle forming the torus
    major_segments  -- The number of segments having a circular cross-section (default is from Blender)
    minor_segments  -- The number of segments in each circular cross-section (default is from Blender)
    location        -- The location of the center of the torus

    return the torus object
    """
    if major_segments is None:
        major_segments = int( russbpy_fn * 1.5 )
    if minor_segments is None:
        minor_segments = int( russbpy_fn / 2 )
    bpy.ops.mesh.primitive_torus_add( major_radius=major_radius, minor_radius=minor_radius, major_segments=major_segments, minor_segments=minor_segments, location=location )
    ob = bpy.context.object
    if name is not None:
        ob.name = name
    return( ob )

def MeshTorus( name=None, major_radius=4.0, minor_radius=1.0, rings=10, ring_points=5, location=(0,0,0), quads=True ):
    """Create a solid torus with evenly-spaced faces

    Keyword arguments:
    name            -- The name for the new torus object
    major_radius    -- The radius to the center of the extruded circle forming the torus
    minor_radius    -- The radius of the extruded circle forming the torus
    rings           -- The number of segments having a circular cross-section
    ring_points     -- The number of points on each ring
    location        -- The location of the center of the torus
    quads           -- Use quads or triangles?

    Return the torus object
    """
    rings = int( rings / 2 ) * 2  # Must be even
    ring_spacer_deg = 360.0 / rings
    
    circle_verts = CirclePoints( minor_radius, ring_points, ( major_radius, 0, 0 ) )
    t = RotationDeg( angle=90.0, axis=(1,0,0), point=(0,0,0) )
    circle_verts = t.apply( circle_verts )
    
    verts = []
    faces = []

    # Determine vertices
    r = RotationDeg( ring_spacer_deg, ( 0, 0, 1 ), ( 0, 0, 0 ) )
    for i in range( 0, rings ):
        for v in circle_verts:
            verts.append( v )
        circle_verts = r.apply( circle_verts )

    # Determine edges
    for i in range( 0, rings ):
        j = ( i + 1 ) % rings
        for k in range( 0, ring_points ):
            if quads:
                faces.append( ( i * ring_points + ( ( k + 1 ) % ring_points ), 
			        i * ring_points + k,
                                j * ring_points + k,
                                j * ring_points + ( ( k + 1 ) % ring_points ) ) )
            else:
                faces.append( ( i * ring_points + ( ( k + 1 ) % ring_points ), 
			        i * ring_points + k,
                                j * ring_points + k ) )
                faces.append( ( j * ring_points + k,
                                j * ring_points + ( ( k + 1 ) % ring_points ), 
                                i * ring_points + ( ( k + 1 ) % ring_points ) ) )

    ob = Mesh( name, verts, [], faces )
    TranslateV( ob, location )

    return ob

def FlatTorus( name=None, r=1, h=.25, minor_w=.25, location=(0,0,0) ):
    """Draw a solid, flattened torus in the XY plane and return the corresponding object

    Keyword arguments:
    name        -- The name for the new flattened torus object
    r    	-- The radius to the center of the extruded rectangle forming the torus
    h           -- The height of the flattened torus
    minor_w     -- The width (along the radius) of the ring around the flattened torus
    location    -- The location of the center of the torus

    return the torus object
    """
    mw2 = minor_w / 2.0
    ob = Cylinder( name=name, r=r + mw2, h=h, location=location )
    hole = Cylinder( r=r - mw2, h=h * 2, location=location )
    Difference( ob, hole, True )
    return( ob )

def Cube( name=None, size=1, location=(0,0,0) ):
    """Draw a solid cube and return the corresponding object

    Keyword arguments:
    name     -- The name for the new torus object
    size     -- The length of each edge
    location -- The location of the center of the cube

    Return the cube object
    """

    bpy.ops.mesh.primitive_cube_add( location=location )
    ob = bpy.context.object
    ScaleUniform( ob, size / 2.0 )
    if name is not None:
        ob.name = name
    return( ob )

def RectangularPrism( name=None, x=1, y=2, z=3, location=(0,0,0) ):
    """Draw a solid rectangular prism and return the corresponding object

    Keyword arguments:
    name     -- The name for the new torus object
    x        -- The length along the X axis
    y        -- The length along the Y axis
    z        -- The length along the Z axis
    location -- The location of the center of the rectangular prism

    Return the rectangular prism object
    """

    ob = Cube( name, size=1 )
    Scale( ob, x, y, z )
    TranslateV( ob, location )
    return( ob )

def RoundedRectangularPrism( name=None, x=1, y=2, z=3, z_r=.1, location=(0,0,0) ):
    """Draw a solid rectangular prism with rounded edges in the Z axis and return the corresponding object

    Keyword arguments:
    name     -- The name for the new torus object
    x        -- The length along the X axis
    y        -- The length along the Y axis
    z        -- The length along the Z axis
    z_r      -- The radius of the rounding parallel to the Z axis
    location -- The location of the center of the rectangular prism

    Return the rectangular prism object
    """

    x_w = x - ( 2.0 * z_r )
    y_w = y - ( 2.0 * z_r )

    r1 = RectangularPrism( x=x, y=y_w, z=z )
    r2 = RectangularPrism( x=x_w, y=y, z=z )

    x2 = x_w / 2.0
    y2 = y_w / 2.0
    z2 = z / 2.0
    c1 = Cylinder( r=z_r, h=z, location=(x2,y2,0) )
    c2 = Cylinder( r=z_r, h=z, location=(x2,-y2,0) )
    c3 = Cylinder( r=z_r, h=z, location=(-x2,y2,0) )
    c4 = Cylinder( r=z_r, h=z, location=(-x2,-y2,0) )

    ob = Join( r1, r2, c1, c2, c3, c4 )
    TranslateV( ob, location )
    return ob


def MeshRectangularPrism( name=None, x=10, x_faces=10, y=20, y_faces=20, z=30, z_faces=30, location=(0,0,0), quads=True ):
    """Draw a solid rectangular prism with control over the number of faces

    Keyword arguments:
    name     -- The name for the new torus object
    x        -- The length along the X axis
    x_faces  -- The length along the X axis
    y        -- The length along the Y axis
    y_faces  -- The length along the Y axis
    z        -- The length along the Z axis
    z_faces  -- The length along the Z axis
    location -- The location of the center of the rectangular prism
    quads    -- Use quads or triangles?

    Return the rectangular prism object
    """
    x_start = -x / 2.0
    y_start = -y / 2.0
    z_start = -z / 2.0
    x_end = x_start + x
    y_end = y_start + y
    z_end = z_start + z

    x_inc = float( x ) / float( x_faces )
    y_inc = float( y ) / float( y_faces )
    z_inc = float( z ) / float( z_faces )

    verts = []
    faces = []

    # ---------------------------------------------

    # Create the XY top vertices
    # The vertices are striped as:
    #    x0,y0  x0,y1 . . . x0,yn x1,y0 x1,y1 ... x1,yn . . . xm,y0 xm,y1 ... xm,ym
    # NOTE: N faces in a row require N+1 vertices across
    xy_verts = []
    xy_faces = []
    for xi in range( 0, x_faces + 1 ):
        for yi in range( 0, y_faces + 1 ):
            xy_verts.append( ( x_start + xi * x_inc, y_start + yi * y_inc, z_end ) )

    # Create the XY top face
    for xi in range( 0, x_faces ):
        for yi in range( 0, y_faces ):
            if quads:
                xy_faces.append( ( xi * ( y_faces + 1 ) + yi,
                                   ( xi + 1 ) * ( y_faces + 1 ) + yi,
                                   ( xi + 1 ) * ( y_faces + 1 ) + yi + 1,
                                   xi * ( y_faces + 1 ) + yi + 1 ) ) 
            else:
                xy_faces.append( ( xi * ( y_faces + 1 ) + yi,
                                   ( xi + 1 ) * ( y_faces + 1 ) + yi,
                                   ( xi + 1 ) * ( y_faces + 1 ) + yi + 1 ) )
                xy_faces.append( ( ( xi + 1 ) * ( y_faces + 1 ) + yi + 1,
                                   xi * ( y_faces + 1 ) + yi + 1,
                                   xi * ( y_faces + 1 ) + yi ) )
    for v in xy_verts:
        verts.append( v )
    for f in xy_faces:
        faces.append( f )

    # Create the XY bottom face
    r = RotationDeg( 180.0, ( 1, 0, 0 ), ( 0, 0, 0 ) )
    xy_verts = r.apply( xy_verts )

    # Create the XY bottom face
    xy_faces = []
    for xi in range( 0, x_faces ):
        for yi in range( 0, y_faces ):
            if quads:
                xy_faces.append( ( len(verts) + xi * ( y_faces + 1 ) + yi,
                                   len(verts) + ( xi + 1 ) * ( y_faces + 1 ) + yi,
                                   len(verts) + ( xi + 1 ) * ( y_faces + 1 ) + yi + 1,
                                   len(verts) + xi * ( y_faces + 1 ) + yi + 1 ) ) 
            else:
                xy_faces.append( ( len(verts) + xi * ( y_faces + 1 ) + yi,
                                   len(verts) + ( xi + 1 ) * ( y_faces + 1 ) + yi,
                                   len(verts) + ( xi + 1 ) * ( y_faces + 1 ) + yi + 1 ) )
                xy_faces.append( ( len(verts) + ( xi + 1 ) * ( y_faces + 1 ) + yi + 1,
                                   len(verts) + xi * ( y_faces + 1 ) + yi + 1,
                                   len(verts) + xi * ( y_faces + 1 ) + yi ) )
    for v in xy_verts:
        verts.append( v )
    for f in xy_faces:
        faces.append( f )

    # ---------------------------------------------

    # Create the XZ top vertices
    # The vertices are striped as:
    #    x0,z0  x0,z1 . . . x0,zn x1,z0 x1,z1 ... x1,zn . . . xm,z0 xm,z1 ... xm,zm
    # NOTE: N faces in a row require N+1 vertices across
    xz_verts = []
    xz_faces = []
    for xi in range( 0, x_faces + 1 ):
        for zi in range( 0, z_faces + 1 ):
            xz_verts.append( ( x_start + xi * x_inc, y_end, z_start + zi * z_inc ) )

    # Create the XZ top face
    for xi in range( 0, x_faces ):
        for zi in range( 0, z_faces ):
            if quads:
                xz_faces.append( ( len(verts) + xi * ( z_faces + 1 ) + zi + 1,
                                   len(verts) + ( xi + 1 ) * ( z_faces + 1 ) + zi + 1,
                                   len(verts) + ( xi + 1 ) * ( z_faces + 1 ) + zi,
                                   len(verts) + xi * ( z_faces + 1 ) + zi ) )
            else:
                xz_faces.append( ( len(verts) + xi * ( z_faces + 1 ) + zi + 1,
                                   len(verts) + ( xi + 1 ) * ( z_faces + 1 ) + zi + 1,
                                   len(verts) + ( xi + 1 ) * ( z_faces + 1 ) + zi ) )
                xz_faces.append( ( len(verts) + ( xi + 1 ) * ( z_faces + 1 ) + zi,
                                   len(verts) + xi * ( z_faces + 1 ) + zi,
                                   len(verts) + xi * ( z_faces + 1 ) + zi + 1 ) )
    for v in xz_verts:
        verts.append( v )
    for f in xz_faces:
        faces.append( f )

    # Create the XZ bottom face
    r = RotationDeg( 180.0, ( 0, 0, 1 ), ( 0, 0, 0 ) )
    xz_verts = r.apply( xz_verts )

    # Create the XZ bottom face
    xz_faces = []
    for xi in range( 0, x_faces ):
        for zi in range( 0, z_faces ):
            if quads:
                xz_faces.append( ( len(verts) + xi * ( z_faces + 1 ) + zi + 1,
                                   len(verts) + ( xi + 1 ) * ( z_faces + 1 ) + zi + 1,
                                   len(verts) + ( xi + 1 ) * ( z_faces + 1 ) + zi,
                                   len(verts) + xi * ( z_faces + 1 ) + zi ) )
            else:
                xz_faces.append( ( len(verts) + xi * ( z_faces + 1 ) + zi + 1,
                                   len(verts) + ( xi + 1 ) * ( z_faces + 1 ) + zi + 1,
                                   len(verts) + ( xi + 1 ) * ( z_faces + 1 ) + zi ) )
                xz_faces.append( ( len(verts) + ( xi + 1 ) * ( z_faces + 1 ) + zi,
                                   len(verts) + xi * ( z_faces + 1 ) + zi,
                                   len(verts) + xi * ( z_faces + 1 ) + zi + 1 ) )
    for v in xz_verts:
        verts.append( v )
    for f in xz_faces:
        faces.append( f )

    # ---------------------------------------------

    # Create the YZ top vertices
    # The vertices are striped as:
    #    y0,z0  y0,z1 . . . y0,zn y1,z0 y1,z1 ... y1,zn . . . ym,z0 ym,z1 ... ym,zm
    # NOTE: N faces in a row require N+1 vertices across
    yz_verts = []
    yz_faces = []
    for yi in range( 0, y_faces + 1 ):
        for zi in range( 0, z_faces + 1 ):
            yz_verts.append( ( x_end, y_start + yi * y_inc, z_start + zi * z_inc ) )

    # Create the YZ top face
    for yi in range( 0, y_faces ):
        for zi in range( 0, z_faces ):
            if quads:
                yz_faces.append( ( len(verts) + yi * ( z_faces + 1 ) + zi,
                                   len(verts) + ( yi + 1 ) * ( z_faces + 1 ) + zi,
                                   len(verts) + ( yi + 1 ) * ( z_faces + 1 ) + zi + 1,
                                   len(verts) + yi * ( z_faces + 1 ) + zi + 1 ) )
            else:
                yz_faces.append( ( len(verts) + yi * ( z_faces + 1 ) + zi,
                                   len(verts) + ( yi + 1 ) * ( z_faces + 1 ) + zi,
                                   len(verts) + ( yi + 1 ) * ( z_faces + 1 ) + zi + 1 ) )
                yz_faces.append( ( len(verts) + ( yi + 1 ) * ( z_faces + 1 ) + zi + 1,
                                   len(verts) + yi * ( z_faces + 1 ) + zi + 1,
                                   len(verts) + yi * ( z_faces + 1 ) + zi ) )
    for v in yz_verts:
        verts.append( v )
    for f in yz_faces:
        faces.append( f )

    # Create the YZ bottom face
    r = RotationDeg( 180.0, ( 0, 1, 0 ), ( 0, 0, 0 ) )
    yz_verts = r.apply( yz_verts )

    # Create the YZ bottom face
    yz_faces = []
    for yi in range( 0, y_faces ):
        for zi in range( 0, z_faces ):
            if quads:
                yz_faces.append( ( len(verts) + yi * ( z_faces + 1 ) + zi,
                                   len(verts) + ( yi + 1 ) * ( z_faces + 1 ) + zi,
                                   len(verts) + ( yi + 1 ) * ( z_faces + 1 ) + zi + 1,
                                   len(verts) + yi * ( z_faces + 1 ) + zi + 1 ) )
            else:
                yz_faces.append( ( len(verts) + yi * ( z_faces + 1 ) + zi,
                                   len(verts) + ( yi + 1 ) * ( z_faces + 1 ) + zi,
                                   len(verts) + ( yi + 1 ) * ( z_faces + 1 ) + zi + 1 ) )
                yz_faces.append( ( len(verts) + ( yi + 1 ) * ( z_faces + 1 ) + zi + 1,
                                   len(verts) + yi * ( z_faces + 1 ) + zi + 1,
                                   len(verts) + yi * ( z_faces + 1 ) + zi ) )
    for v in yz_verts:
        verts.append( v )
    for f in yz_faces:
        faces.append( f )
   
    ob = Mesh( name, verts, [], faces )
    TranslateV( ob, location )
    return ob

def RectangularCup( name=None, x=1, y=2, z=3, x_thickness=0.1, y_thickness=0.2, z_thickness=0.3, location=(0,0,0) ):
    """Draw a cylindrical cup with a height along the Z axis and the open end along the positive Z axis

    Keyword arguments:
    name        -- The name for the new cup object
    x           -- The length along the X axis
    y           -- The length along the Y axis
    z           -- The length along the Z axis
    x_thickness -- The thickness of wall along the X axis
    y_thickness -- The thickness of wall along the Y axis
    z_thickness -- The thickness of wall along the Z axis
    location    -- The location of the center of the tube
    """

    o = RectangularPrism( name=name, x=x, y=y, z=z )
    i = RectangularPrism( x=x - x_thickness * 2.0, y=y - y_thickness * 2.0, z=z )
    TranslateZ( i, z_thickness )
    Difference( o, i, True )
    TranslateV( o, location )
    return o

def Cylinder( name=None, r=1.0, h=1.0, vertices=None, cap=True, location=(0,0,0) ):
    """Draw a cylinder with the height along the Z axis and return the corresponding object

    Keyword arguments:
    name     -- The name for the new cylinder object
    r        -- The radius
    h        -- The height
    vertices -- The number of vertices to use in the polygon approximation of the circle
    cap      -- Cap the ends of the cylinder? If uncapped, the cylinder isn't solid.
    location -- The location of the center of the cylinder

    Return the cylinder object
    """

    if vertices is None:
        vertices = russbpy_fn
    bpy.ops.mesh.primitive_cylinder_add( radius=r, depth=h, vertices=vertices, location=location )
    ob = bpy.context.object
    if name is not None:
        ob.name = name
    Subdivide( ob )	# This steps helps with Boolean operations.
    return( ob )

def MeshCylinder( name=None, r=1.0, h=5.0, r_faces=5, h_faces=5, c_faces=10, location=(0,0,0), quads=True ):
    """Draw a cylinder with the height along the Z axis with control of the faces

    Keyword arguments:
    name     -- The name for the new cylinder object
    r        -- The radius
    h        -- The height
    r_faces  -- The number faces per radial line
    h_faces  -- The number faces per height line
    c_faces  -- The number faces per circumference
    location -- The location of the center of the cylinder
    quads    -- Use quads or triangles?

    Return the cylinder object
    """
    h_steps = float( h ) / float( h_faces )
    r_steps = float( r ) / float( r_faces )

    circle_verts = CirclePoints( r, c_faces, location=(location[0],location[1],location[2] - h/2.0) )

    verts = []
    faces = []

    t = Translation( ( 0, 0, h_steps ) )

    # Build up the curved wall
    for hi in range( 0, h_faces + 1 ):
        for v in circle_verts:
            verts.append( v )
        circle_verts = t.apply( circle_verts )

    for hi in range( 0, h_faces ):
        for ci in range( 0, c_faces ):
            if quads:
                faces.append( ( hi * c_faces + ci,
                                hi * c_faces + ( ci + 1 ) % c_faces,
                                ( hi + 1 ) * c_faces + ( ci + 1 ) % c_faces,
                                ( hi + 1 ) * c_faces + ci ) )
            else:
                faces.append( ( hi * c_faces + ci,
                                hi * c_faces + ( ci + 1 ) % c_faces,
                                ( hi + 1 ) * c_faces + ( ci + 1 ) % c_faces ) )
                faces.append( ( ( hi + 1 ) * c_faces + ( ci + 1 ) % c_faces,
                                ( hi + 1 ) * c_faces + ci,
                                hi * c_faces + ci ) )

    # Fill in the bottom
    # For the bottom, the outer vertices are 0, ..., c_faces - 1
    for ri in range( 1, r_faces ):
        circle_verts = CirclePoints( r - ri * r_steps, c_faces, location=(location[0],location[1],location[2] - h/2.0) )
        for ci in range( 0, c_faces ):
            if ri == 1:
                if quads:
                    faces.append( ( len( verts ) + ci,
                                    len( verts ) + ( ci + 1 ) % c_faces,
                                    ( ci + 1 ) % c_faces,
                                    ci ) )
                else:
                    faces.append( ( len( verts ) + ci,
                                    len( verts ) + ( ci + 1 ) % c_faces,
                                    ( ci + 1 ) % c_faces ) )
                    faces.append( ( ( ci + 1 ) % c_faces,
                                    ci,
                                    len( verts ) + ci ) )
            else:
                if quads:
                    faces.append( ( len( verts ) + ci,
                                    len( verts ) + ( ci + 1 ) % c_faces,
                                    len( verts ) - c_faces + ( ci + 1 ) % c_faces,
                                    len( verts ) - c_faces + ci ) )
                else:
                    faces.append( ( len( verts ) + ci,
                                    len( verts ) + ( ci + 1 ) % c_faces,
                                    len( verts ) - c_faces + ( ci + 1 ) % c_faces ) )
                    faces.append( ( len( verts ) - c_faces + ( ci + 1 ) % c_faces,
                                    len( verts ) - c_faces + ci,
                                    len( verts ) + ci ) )

        if ri == ( r_faces - 1 ):
            for ci in range( 0, c_faces ):
                faces.append( ( len( verts ) + c_faces,
                                len( verts ) + ( ci + 1 ) % c_faces,
                                len( verts ) + ci ) )

        for v in circle_verts:
            verts.append( v )

    verts.append( ( location[0], location[1], location[2] - h/2.0 ) )

    # Fill in the top
    # For the top, the outer vertices are c_faces * h_faces, ..., c_faces * ( h_faces + 1 ) - 1
    top_base = c_faces * h_faces
    for ri in range( 1, r_faces ):
        circle_verts = CirclePoints( r - ri * r_steps, c_faces, location=(location[0],location[1],location[2] + h/2.0) )
        for ci in range( 0, c_faces ):
            if ri == 1:
                if quads:
                    faces.append( ( top_base + ci,
                                    top_base + ( ci + 1 ) % c_faces,
                                    len( verts ) + ( ci + 1 ) % c_faces,
                                    len( verts ) + ci ) )
                else:
                    faces.append( ( top_base + ci,
                                    top_base + ( ci + 1 ) % c_faces,
                                    len( verts ) + ( ci + 1 ) % c_faces ) )
                    faces.append( ( len( verts ) + ( ci + 1 ) % c_faces,
                                    len( verts ) + ci,
                                    top_base + ci ) )
            else:
                if quads:
                    faces.append( ( len( verts ) - c_faces + ci,
                                    len( verts ) - c_faces + ( ci + 1 ) % c_faces,
                                    len( verts ) + ( ci + 1 ) % c_faces,
                                    len( verts ) + ci ) )
                else:
                    faces.append( ( len( verts ) - c_faces + ci,
                                    len( verts ) - c_faces + ( ci + 1 ) % c_faces,
                                    len( verts ) + ( ci + 1 ) % c_faces ) )
                    faces.append( ( len( verts ) + ( ci + 1 ) % c_faces,
                                    len( verts ) + ci,
                                    len( verts ) - c_faces + ci ) )

        if ri == ( r_faces - 1 ):
            for ci in range( 0, c_faces ):
                faces.append( ( len( verts ) + c_faces,
                                len( verts ) + ci,
                                len( verts ) + ( ci + 1 ) % c_faces ) )

        for v in circle_verts:
            verts.append( v )

    verts.append( ( location[0], location[1], location[2] + h/2.0 ) )

    ob = Mesh( name, verts, [], faces )

    return ob

def CylinderP2P( name=None, r=1.0, p1=(0,0,0), p2=(1.0,1.0,1.0) ):
    """Draw a cylinder from p1 to p2.

    Keyword arguments:
    name     -- The name for the new cylinder object
    r        -- The radius
    p1       -- The start point
    p2       -- The end point

    Return the cylinder object
    """
    h = DistanceV( p1, p2 )
    c = Cylinder( name=name, r=r, h=h )

    # Point the cylinder up from the origin
    TranslateZ( c, h / 2.0 )
    SetOriginOrigin( c )

    # Gotta adjust the transform_metadata setting so the
    # rotation occurs as expected.
    tm = GetTransformMetadata()
    SetTransformMetadata( False )
    v = Vector( p1, p2 )
    #Print( "CylinderP2P: p1 = (%s,%s,%s)" % ( p1[0], p1[1], p1[2] ) )
    #Print( "CylinderP2P: p2 = (%s,%s,%s)" % ( p2[0], p2[1], p2[2] ) )
    if v[0] == 0.0 and v[1] == 0.0 and v[2] < 0.0:
        # KLUDGE!
        # Rotating 180.0 degrees doesn't seem to work.
        TranslateV( c, p2 )
    else:
        RotateToV( c, v=v )
        #Print( "CylinderP2P: v = (%s,%s,%s)" % ( v[0], v[1], v[2] ) )
        TranslateV( c, p1 )
    SetTransformMetadata( tm )
    return c

def Tube( name=None, r=1.0, h=1.0, thickness=.5, vertices=None, location=(0,0,0) ):
    """Draw a solid, cylindrical tube with the height along the Z axis and return the corresponding object

    Keyword arguments:
    name      -- The name for the new tube object
    r         -- The outer radius
    h         -- The height
    thickness -- The thickness of the tube wall
    vertices  -- The number of vertices to use in the polygon approximation of the circle.
                 Set to None to use the current default.
    location  -- The location of the center of the tube

    Return the tube object
    """

    o = Cylinder( r=r, h=h, vertices=vertices, location=location )
    i = Cylinder( r=r - thickness, h=h, vertices=vertices, location=location )
    Difference( o, i, True )

    return o

def Cup( name=None, r=0.9, h=1.0, wall_thickness=0.1, base_thickness=0.1, location=(0,0,0) ):
    """Draw a cylindrical cup with a height along the Z axis and the open end along the positive Z axis

    Keyword arguments:
    name           -- The name for the new cup object
    r              -- The outer radius of the cup
    h              -- The height of the cup
    wall_thickness -- The thickness of the curved wall
    base_thickness -- The thickness of the circular base
    location       -- The location of the center of the tube
    """

    o = Cylinder( name=name, r=r, h=h )
    i = Cylinder( r=r-wall_thickness, h=h )
    TranslateZ( i, base_thickness )
    Difference( o, i, True )
    TranslateV( o, location )
    return o

def Cone( name=None, r=1, top_r=0, h=1, vertices=None, cap=True, location=(0,0,0) ):
    """Draw a solid cone with the height along the Z axis and return the corresponding object

    Keyword arguments:
    name      -- The name for the new cone object
    r         -- The base radius
    top_r     -- The top radius (for truncated cones)
    h         -- The height of the cone
    vertices  -- The number of vertices to use in the polygon approximation of the circle.
                 Set to None to use the current default.
    cap       -- Cap the base of the cone? If uncapped, the cone isn't solid.
    location  -- The location of the center of the tube

    Return the cone object
    """
    if vertices is None:
        vertices = russbpy_fn
    bpy.ops.mesh.primitive_cone_add( radius1=r, radius2=top_r, depth=h, location=location, vertices=vertices )
    ob = bpy.context.object
    if name is not None:
        ob.name = name
    return( ob )

def CharMetrics( ch, font=None ):
    """Return a hash of metrics for the given character, as rendered in the given font

    When calculating the metrics, the character is rendered in the default font size, positioned at the origin.
    The primary use of the metrics is for the height-to-width ratio and baseline offset ratio, so the font size used doesn't really matter.

    Keyword arguments:
    ch   -- The character
    font -- The file-system path to the font used to render the character (default Blender current font)

    Return the hash object, with the following values defined:
        min_w             -- Minimum width (X-axis) extent
        max_w             -- Maximum width (X-axis) extent
        min_h             -- Minimum height (Y-axis) extent
        max_h             -- Maximum height (Y-axis) extent
        baseline_offset_h -- the offset of the bottom extent relative to the character baseline
    """
    metrics = {}
    
    if len( ch ) != 1:
        raise "Input '%s' is not a single character" % ch

    # store the location of current 3d cursor
    saved_location = bpy.context.scene.cursor_location  # returns a vector

    bpy.context.scene.cursor_location = (0,0,0)
    bpy.ops.object.text_add()
    c = Current()
    c.data.body = ch
    c.data.extrude = 0.5
    if font is not None:
        c.data.font = bpy.data.fonts.load( font )
    c.select = True
    # Convert to mesh
    bpy.ops.object.convert( target='MESH' )
    
    bb = c.bound_box   # array of 3d points
    min_w = 99999
    max_w = 0
    min_h = 99999
    max_h = 0
    for p in c.bound_box:
        if min_w > p[0]:
            min_w = p[0]
        if max_w < p[0]:
            max_w = p[0]
        if min_h > p[1]:
            min_h = p[1]
        if max_h < p[1]:
            max_h = p[1]

    w = ( max_w - min_w )
    h = ( max_h - min_h )
    baseline_offset_h = -min_h

    metrics[ 'min_w' ] = min_w
    metrics[ 'max_w' ] = max_w
    metrics[ 'w' ] = w
    metrics[ 'min_h' ] = min_h
    metrics[ 'max_h' ] = max_h
    metrics[ 'h' ] = h
    metrics[ 'baseline_offset_h' ] = baseline_offset_h
    #Print( "metrics[ %c ] = %s" % ( ch, metrics ) )

    # set 3dcursor location back to the stored location
    bpy.context.scene.cursor_location = saved_location

    Delete( c )

    return metrics

def TextMetrics( text="abc123", font=None ):
    """Return an array of hashes of metrics, corresponding to each character of text, as rendered in the given font

    When calculating the metrics, each character is rendered in the default font size, positioned at the origin.
    The primary use of the metrics is for the height-to-width ratio and baseline offset ratio, so the font size used doesn't really matter.

    Keyword arguments:
    text -- The text
    font -- The file-system path to the font used to render the text (default Blender current font)

    Return the array with each element being a hash object, with the following values defined:
        min_w             -- Minimum width (X-axis) extent
        max_w             -- Maximum width (X-axis) extent
        min_h             -- Minimum height (Y-axis) extent
        max_h             -- Maximum height (Y-axis) extent
        baseline_offset_h -- the offset of the bottom extent relative to the character baseline
    """
    metrics = {}
    for c in text:
        if not c in metrics.keys():
            metrics[ c ] = CharMetrics( c, font )

    return metrics

def Text( name=None, text="abc123", h=1, font=None, align='LEFT', bevel_depth=0.0, location=(0,0,0), center=True, subdivide=1 ):
    """Draw some solid text in the XY plane and return the corresponding object

    The text can be read looking down from the positive Z-axis, looking towards the origin.
    The text starts in the negative X-axis and ends in the positive X-axis

    Keyword arguments:
    text        -- The text to draw
    h           -- The height of the text
    font        -- The font used to render the text
    align       -- The horizontal alignment of the text. Can be one of: LEFT, CENTER, RIGHT
    bevel_depth -- The bevel depth along the character edges
    location    -- The location of the start (or center when center=True) of the text
    center      -- Center the text? Otherwise start the text at the given location
    subdivide   -- The number of subdivisions. Higher numbers mean more, smaller faces

    Return the text object
    """
    global russbpy_modnum_gen
    bpy.context.scene.cursor_location = location
    bpy.ops.object.text_add()
    ob=Current()
    if font is not None:
        russbpy_fn = bpy.data.fonts.load( font )
        ob.data.font = russbpy_fn
    if name is not None:
        ob.name = name
    ob.data.body = text
    ob.data.align = align
    ob.data.extrude = h / 2.0
    ob.data.bevel_depth = bevel_depth
    ob.select = True
    # Convert to mesh
    bpy.ops.object.convert( target='MESH' )

    if subdivide != 1:
        # Remesh for a nicer mesh
        ob.select = True
        mod = ob.modifiers.new('remesher', 'REMESH')
        mod.name = "modifier_%d" % russbpy_modnum_gen
        russbpy_modnum_gen = russbpy_modnum_gen + 1
        mod.use_remove_disconnected = False
        mod.octree_depth = subdivide
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

    if center:
        SetOriginCenter( ob )
        TranslateTo( ob, 0, 0, 0 )
    
    return ob

def ShowFont( font ):
    """Show the font's characters in a grid

    Keyword arguments:
    font -- The file-system path to the font to render the characters with

    Return nothing
    """
    for i in range( 0, 16 ):
    	for j in range( 0, 16 ):
            t = Text( text=chr( i * 16 + j ), h=.01, font=font )
            TranslateX( t, i * 2 )
            TranslateY( t, j * 2 )

def SphericalText( text='Abc123', font=None, r=1, thickness=.05, angular_height=30, r_offset=0, subdivide=1, spacer_deg=4 ):
    """Draw solid, spherical text and return the corresponding object

    The first character of the text is rendered near (r,0,0).
    The text is readable when the positive Z-axis extends up.
    The equator of the sphere is halfway between the topmost character extent and the bottommost character extent.

    Keyword arguments:
    text           -- The text to draw
    font           -- The font used to render the text
    r              -- The outer radius of the text
    thickness      -- The thickness of the text
    angular_height -- The angular height of the text, in degrees up from the equator of the sphere
    r_offset       -- The radial offset, in degrees.
                      Positive values rorate the text towards the top of the sphere.
                      Negative values rorate the text towards the bottom of the sphere.
    subdivide      -- The number of subdivisions. Higher numbers mean more, smaller faces
    spacer_deg     -- The number of spacer degrees between characters

    Return the spherical text object
    """

    for c in text:
        if c == ' ':
            raise "No spaces allowed!"

    # Get the text metrics
    metrics = TextMetrics( text, font )

    # Determine the tallest character 
    max_h = 0
    for c in metrics.keys():
        if max_h < metrics[c][ 'h' ]:
            max_h = metrics[c][ 'h' ]
    #Print( "max_h = %s" % max_h )

    # Create an array of text objects, one per character
    obs = []    # Objects
    dims = []
    for c in text:
        t = Text( text=c, h=1, font=font, center=True, subdivide=subdivide )
        RotateDeg( t, 90, ( 0, 1, 0 ) )
        RotateDeg( t, 90, ( 1, 0, 0 ) )
        obs.append( t )
        dt = Dimensions( t )
        dims.append( dt )

    # Convert angular height to actual height
    #       - theta = A / 2
    #       - sin theta = y / r
    #       - y = sin theta * r
    #       - actual height = 2 * y
    theta = angular_height / 2.0
    y = math.sin( theta / 180.0 * math.pi ) * r
    h = y * 2

    # Determine the vertical scale required for the
    # tallest character to fit the angular height.
    #   h = factor * max_h
    #   factor = h / max_h
    factor = h / max_h

    # Determine the vertical tweak for each character.
    # Then determine the angular tweak.
    for c in metrics.keys():
        metrics[c]['v_tweak'] = factor * ( ( max_h - metrics[c]['h'] ) / 2 + metrics[c]['baseline_offset_h'] )
        # sin( theta ) = v_tweak / r
        # theta = asin( v_tweak / r )
        #Print( "v_tweak for '%c' is %s" % ( c, metrics[c]['v_tweak'] ) )
        metrics[c]['v_tweak_rad'] = math.asin( metrics[c]['v_tweak'] / r )
        #Print( "v_tweak_rad for '%c' is %s" % ( c, metrics[c]['v_tweak_rad'] ) )

    # Scale each object.
    # Move it to the edge of the sphere.
    # Change the center of rotation to the origin.
    for i in range( 0, len( text ) ):
        ob = obs[ i ]
        ScaleUniform( ob, factor )
        TranslateX( ob, r )
        SetOrigin( ob, 0, 0, 0 )
        TranslateZ( ob, r * r_offset )

    # Determine the angular width of each character
    #   theta = aw / 2
    #   sin theta = (width/2) / r
    #   theta = arcsin( (width/2) / r )
    #   aw =  2 * arcsin( (width/2) / r )
    aw = []
    for i in range( 0, len( text ) ):
        xw = dims[ i ][ 0 ]
        angle = 2 * math.asin( ( xw / 2 ) / r )
        angle = angle / ( 2.0 * math.pi ) * 360.0
        aw.append( angle )

    # Arrange the characters
    ap = 0
    for i in range( 0, len( text ) ):
        # Adjust characters vertically
        RotateRad( obs[ i ], metrics[ text[i] ]['v_tweak_rad'], (0, 1, 0) )
        if i > 0:
            ap = ap + aw[ i - 1 ] / 2.0 + spacer_deg + aw[ i ] / 2.0
            RotateDeg( obs[ i ], ap, ( 0, 0, 1 ) )

    # For some reason, intersecting each letter with
    # its own hollow sphere works better than intersecting
    # each letter with the same sphere.
    # The problem with the latter is some letters aren't
    # closed, or disappear entirely.
    for i in range( 0, len( text ) ):
        # Create a hollow sphere
        outer = Sphere( r=r )
        inner = Sphere( r=r-thickness )
        Difference( outer, inner, True )
        Intersect( obs[ i ], outer, True )

    j = Join( obs )

    return j

def CylindricalText( text='Abc123', font=None, r=1, thickness=.05, angular_height=30, subdivide=1, inverse=False, spacer_deg=4, backwards=False, escape='_' ):
    """Draw cylindrical text and return the corresponding object

    Keyword arguments:
    text           -- The text to draw
    font           -- The font used to render the text
    r              -- The outer radius of the text
    thickness      -- The thickness of the text
    angular_height -- The angular height of the text, in degrees up from the equator of the cylinder
    subdivide      -- The number of subdivisions. Higher numbers mean more, smaller faces
    inverse        -- Take out the text and leave the cylinder? Otherwise, leave only the text
    spacer_deg     -- The number of spacer degrees between characters
    backwards      -- Draw the text backwards so it is readable from inside the cylinder?
                      Otherwise the text is readable from outside the cylinder
    escape         -- The character to use as a space substitute
                      Required because only non-blank characters can be measured

    Return the cylindrical text object
    """

    if backwards:
        text = text[::-1]

    l = list( text )
    for i in range( 0, len( l ) ):
        if l[ i ] == ' ':
            l[ i ] = escape
    text = "".join( l )

    # Get the text metrics
    metrics = TextMetrics( text, font )

    # Determine the tallest character 
    max_h = 0
    for c in metrics.keys():
        if max_h < metrics[c][ 'h' ]:
            max_h = metrics[c][ 'h' ]
    #Print( "max_h = %s" % max_h )

    # Create an array of text objects, one per character
    obs = []    # Objects
    dims = []
    for c in text:
        t = Text( text=c, h=1, font=font, center=True, subdivide=subdivide )
        RotateDeg( t, 90, ( 0, 1, 0 ) )
        RotateDeg( t, 90, ( 1, 0, 0 ) )
        obs.append( t )
        dt = Dimensions( t )
        dims.append( dt )

    # Convert angular height to actual height
    #       - theta = A / 2
    #       - sin theta = y / r
    #       - y = sin theta * r
    #       - actual height = 2 * y
    theta = angular_height / 2.0
    y = math.sin( theta / 180.0 * math.pi ) * r
    h = y * 2

    # Determine the vertical scale required for the
    # tallest character to fit the angular height.
    #   h = factor * max_h
    #   factor = h / max_h
    factor = h / max_h

    # Determine the vertical tweak for each character.
    # Then determine the angular tweak.
    for c in metrics.keys():
        metrics[c]['v_tweak'] = factor * ( ( max_h - metrics[c]['h'] ) / 2 + metrics[c]['baseline_offset_h'] )
        # sin( theta ) = v_tweak / r
        # theta = asin( v_tweak / r )
        #Print( "v_tweak for '%c' is %s" % ( c, metrics[c]['v_tweak'] ) )
        metrics[c]['v_tweak_rad'] = math.asin( metrics[c]['v_tweak'] / r )
        #Print( "v_tweak_rad for '%c' is %s" % ( c, metrics[c]['v_tweak_rad'] ) )

    # Scale each object.
    # Move it to the edge of the sphere.
    # Change the center of rotation to the origin.
    for i in range( 0, len( text ) ):
        ob = obs[ i ]
        ScaleUniform( ob, factor )
        if backwards:
            RotateDegZ( ob, 180 )
        Translate( ob, r, 0, 0 )
        SetOrigin( ob, 0, 0, 0 )

    # Determine the angular width of each character
    #   theta = aw / 2
    #   sin theta = (width/2) / r
    #   theta = arcsin( (width/2) / r )
    #   aw =  2 * arcsin( (width/2) / r )
    aw = []
    for i in range( 0, len( text ) ):
        xw = dims[ i ][ 0 ]
        angle = 2 * math.asin( ( xw / 2 ) / r )
        angle = angle / ( 2.0 * math.pi ) * 360.0
        aw.append( angle )

    # Arrange the characters
    ap = 0
    for i in range( 0, len( text ) ):
        # Adjust characters vertically
        RotateRad( obs[ i ], metrics[ text[i] ]['v_tweak_rad'], (0, 1, 0) )
        if i > 0:
            ap = ap + aw[ i - 1 ] / 2.0 + spacer_deg + aw[ i ] / 2.0
            RotateDeg( obs[ i ], ap, ( 0, 0, 1 ) )

    # For some reason, intersecting each letter with
    # its own hollow cylinder works better than intersecting
    # each letter with the same cylinder.
    # The problem with the latter is some letters aren't
    # closed, or disappear entirely.
    outer = Cylinder( r=r, h=r*2 )
    inner = Cylinder( r=r-thickness, h=r*2 )
    Difference( outer, inner, True )
    for i in range( 0, len( text ) ):
        if text[ i ] != escape:
            if inverse:
                Difference( outer, obs[ i ], True )
            else:
                Intersect( obs[ i ], outer )

    for i in reversed( range( 0, len( text ) ) ):
        if text[ i ] == escape:
            Delete( obs[ i ] )
            del obs[ i ]

    if inverse:
        j = outer
    else:
        Delete( outer )
        j = Join( obs )

    return j

def Mesh( name=None, verts=[], edges=[], faces=[] ):
    """Draw a mesh and return the corresponding object

    Keyword arguments:
    name  -- The name for the new mesh object
    verts -- The (x,y,z) vertices for the mesh
    edges -- The (v1,v2) edges for the mesh, where v1 and v2 are in range(0,len(verts))
    faces -- The faces for the mesh, as triangles (v1,v2,v3) or quads (v1,v2,v3,v4)
             where v1, v2, v3 and v4 are in range(0,len(edges))
             Note that the faces are constructed using the right-hand rule

    Return the mesh object
    """

    # Vertices are [ ( x, y, z ), ... ]
    #   Where x, y and z are float coordinates
    #
    # Edges are [ [ Vi, Vj ], ... ]
    #
    # Faces are [ [ Vi, Vj, Vk ], ... ]
    #   quads are allowed: [ Vi, Vj, Vk, Vl ]
    #
    md = bpy.data.meshes.new( "mesh" )
    md.from_pydata( verts, edges, faces )
    md.update()

    ob = bpy.data.objects.new( "", md )
    if name is not None:
        ob.name = name
    bpy.data.scenes[0].objects.link( ob )

    return ob

def TriangleV( name=None, v1=(0,0,0), v2=(0,1,0), v3=(0,0,1) ):
    """Draw an N-gon prism and return the correcponding object

    Keyword arguments:
    name  -- The name for the new triangle object
    v1    -- The first vertex in the triangle
    v2    -- The second vertex in the triangle
    v3    -- The third vertex in the triangle

    Return the mesh object
    """
    print( "V1" )
    print( v1 )
    verts = [ v1, v2, v3 ]
    #edges = [ [ 0, 1 ], [ 1, 2 ], [ 2, 0 ] ]
    faces = [ [ 0, 1, 2 ] ]
    return Mesh( name, verts, [], faces )

def NGonPrism( name=None, r=1.0, h=1.0, sides=8, open=False ):
    """Draw an N-gon prism and return the correcponding object

    Keyword arguments:
    name  -- The name for the new N-gon prism object
    r     -- The outer radius of the N-gon, ie. measured at the vertices
    h     -- The height
    sides -- The number of sides to the N-gon ends of the prism
    open  -- Leave the prism open at the ends?
               Otherwise the ends are capped

    Return the N-gon prism object
    """
    h = h / 2.0

    swath = ( 2.0 * math.pi ) / sides

    verts = []
    # Top
    for i in range( 0, sides ):
        x = r * math.cos( i * swath )
        y = r * math.sin( i * swath )
        verts.append( [ x, y, h ] )
        verts.append( [ x, y, -h ] )
    verts.append( [ 0, 0, h ] )
    verts.append( [ 0, 0, -h ] )

    faces = []
    # quads on the sides
    for i in range( 0, sides ):
        l = i * 2
        r = ( ( i + 1 ) % sides ) * 2
        faces.append( [ l, l + 1, r + 1, r ] )

    if not open:
        for i in range( 0, sides ):
            l = i * 2
            r = ( ( i + 1 ) % sides ) * 2
            faces.append( [ l, r, sides * 2 ] )
            faces.append( [ l + 1, sides * 2 + 1, r + 1 ] )

    return Mesh( name, verts, [], faces )

def Arrow( body_x=10, body_y=1, body_z=1, head_r=2 ):
    """Draw an arrow and return the corresponding object

    The arrow lies along the X axis, pointing away from the origin towards the positive X-axis
    The arrow is viewable from the Z-axis, viewing towards the origin

    Keyword arguments:
    body_x -- The length of the arrow
    body_y -- The width of the arrow body
    body_z -- The thickness of the arrow
    head_r -- The radius of the arrow head, containing three points of an equilateral triangle

    Return the arrow object
    """
    # Create an arrow along the X axis, pointing away from the origin
    # starting at the origin.

    # Sanity checks
    if head_r < body_z:
        raise ValueError( "Head radius (%s) must be at least as big as arrow body height (%s)" % ( head_r, body_z ) )
    
    # Determine offset of the center of an equilateral
    # triangle compared to the mid-height point.
    center_offset = head_r * Sin( 30.0 )
    edge_as_r = 2.0 * head_r * Cos( 30.0 )
    head_h = edge_as_r * Cos( 30.0 )
    half_h = head_h / 2.0
    tweak = ( half_h - center_offset ) + half_h

    # Build an arrow of the given length,
    # pointing to +X from the origin
    x_len = body_x - head_h
    p = RectangularPrism( x=x_len, y=body_y, z=body_z )
    head = NGonPrism( sides=3, r=head_r, h=body_z )

    ( x, y, z ) = Dimensions( head )

    TranslateX( head, x_len * .5 + x / 2.0 - tweak )
    TranslateX( p, -half_h )
    Union( head, p, True )
    TranslateX( head, x_len / 2.0 + half_h )
    SetOrigin( head, 0, 0, 0 )
    return head

def RainDrop( radius, center_to_tip, thickness ):
    """Draw a raindrop shape.

    Keyword arguments:
    radius        -- The radius of the rounded tip of the raindrop.
    center_to_tip -- The distance from the center of the rounded tip to the sharp tip.
    thickness     -- The thickness of the raindrop.

    Return the object
    """
    if center_to_tip < radius:
        center_to_tip = radius + center_to_tip 
    t = Cylinder( r=radius, h=thickness )
    d = RectangularPrism( x=center_to_tip, y=radius * 2.0, z=thickness, location=( center_to_tip / 2.0, 0, 0 ) )
    x1 = Duplicate( d )
    x2 = Duplicate( d )
    Union( d, t, True )

    angle = ASin( radius / center_to_tip )
    Print( "angle=%s" % angle )

    ScaleZ( x1, 2.0 )
    ScaleX( x1, 2.0 )
    TranslateY( x1, radius )
    SetOrigin( x1, center_to_tip, 0, 0 )
    RotateDegZ( x1, -angle )
    Difference( d, x1, True )

    ScaleZ( x2, 2.0 )
    ScaleX( x2, 2.0 )
    TranslateY( x2, -radius )
    SetOrigin( x2, center_to_tip, 0, 0 )
    RotateDegZ( x2, angle )
    Difference( d, x2, True )

    return d

def Snowflake( ob, radius=1.0 ):
    """Create a snowflake from the given object

    Keyword arguments:
    ob     -- The object to use as one half arm of the snowflake
    radius -- The distance to push ob away from the center of the snowflake

    Note that ob will be copied and positioned at the origin to begin the snowflake.
    The first arm is moved in the positive X-axis direction.

    Return the snowflake object
    """

    arm = Duplicate( ob )
    TranslateTo( arm, 0, 0, 0 )
    TranslateX( arm, radius )
    SetOrigin( arm, 0, 0, 0 )

    # One half of the arms.
    obs = []
    for i in range( 0, 6 ):
        a = Duplicate( arm )
        RotateDegZ( a, i * 60.0 )
        obs.append( a )

    # Then the other half.
    RotateDegX( arm, 180 )
    for i in range( 0, 6 ):
        a = Duplicate( arm )
        RotateDegZ( a, i * 60.0 )
        obs.append( a )

    Delete( arm )
    return Join( obs )

def L( stroke_width=1.0, height=10.0, width=5.0, thickness=.1 ):
    """Create a 3D letter L in the XY plane.

    Keyword arguments:
    stroke_width  -- The width of the character's strokes
    height        -- The height of the letter
    width         -- The width of the letter
    thickness     -- The thickness of the object

    Return the object
    """
    l = Cube()
    Scale( l, stroke_width, height, thickness )

    leftright = Cube()
    Scale( leftright, width, stroke_width, thickness )
    Translate( leftright, ( width - stroke_width ) / 2.0, -( height - stroke_width ) / 2.0, 0 )
    Union( l, leftright, True )

    SetOriginCenter( l )
    TranslateTo( l, 0, 0, 0 )
    return l

def C( stroke_width=1.0, height=10.0, thickness=.1 ):
    """Create a 3D letter C in the XY plane.

    Keyword arguments:
    stroke_width  -- The width of the character's strokes
    height        -- The height of the letter
    thickness     -- The thickness of the object

    Return the object
    """
    width = height
    o_radius = height / 2.0
    i_radius = o_radius - stroke_width
    co = Cylinder( r=o_radius, h=thickness )
    ci = Cylinder( r=i_radius, h=thickness )
    Difference( co, ci, True )

    angle = 60.0 # degrees
    cutout = NGonPrism( r=height, h=thickness * 2.0, sides=3 )
    RotateDegZ( cutout, 180 )
    TranslateX( cutout, height )
    Difference( co, cutout, True )
    return co

def R( stroke_width=1.0, height=10.0, width=5.0, thickness=.1 ):
    """Create a 3D letter R in the XY plane.

    Keyword arguments:
    stroke_width  -- The width of the character's strokes
    height        -- The height of the letter
    width         -- The width of the letter
    thickness     -- The thickness of the object

    Return the object
    """
   
    # Vertical stroke
    r = Cube()
    Scale( r, stroke_width, height, thickness )
    TranslateX( r, stroke_width / 2.0 )

    # Upper curve
    o_radius = ( width / 2.0 ) + stroke_width / 4.0
    i_radius = o_radius - stroke_width
    co = Cylinder( r=o_radius, h=thickness )
    ci = Cylinder( r=i_radius, h=thickness )
    Difference( co, ci, True )

    # Plane to cut the upper bulge in half
    p = Plane()
    RotateDegY( p, 90 )
    ScaleY( p, height * 2.0 )
    Difference( co, p, True )

    # Upper horizontal bar
    ub = Cube()
    Scale( ub, width - o_radius, stroke_width, thickness )
    TranslateY( ub, o_radius - stroke_width / 2.0 )
    TranslateX( ub, -( ( width - o_radius ) - stroke_width ) / 2.0 )
    Union( co, ub, True )

    # Lower horizontal bar
    lb = Cube()
    Scale( lb, width - o_radius, stroke_width, thickness )
    TranslateY( lb, -( o_radius - stroke_width / 2.0 ) )
    TranslateX( lb, -( width - o_radius ) / 2.0 )
    Union( co, lb, True )
    Translate( co, width - o_radius, height / 2.0 - o_radius, 0 )
    Union( r, co, True )

    # Leg of the R
    leg = Cube()
    SetOrigin( leg, 0, 0.5, 0 )
    lh = height / 2.0 + stroke_width
    Scale( leg, stroke_width, lh, thickness )
    TranslateX( leg, width - o_radius + stroke_width / 2.0 )
    TranslateY( leg, -stroke_width / 2.0 )
    RotateDegZ( leg, 18 )

    # Plane to trim the bottom portion of the leg
    p = Plane()
    RotateDegX( p, -90 )
    ScaleX( p, width * 2.0 )
    ScaleZ( p, thickness * 2.0 )
    TranslateY
    Difference( leg, p, True )
    Union( r, leg, True )

    # Center the letter
    SetOrigin( r, width / 2.0, 0, 0 )
    TranslateTo( r, 0, 0, 0 )

    return r

def BallJoint( ball_radius=10.0, stem_height=5.0, stem_radius=2.0, center_in_ball=False ):
    """Create a ball of a ball-and-socket joint.

    The ball points up in the Z axis relative to the origin.
    The bottom of the stem is at the origin.

    Keyword arguments:
    ball_radius -- The radius of the ball
    stem_height -- The height of the stem at the bottom of the socket
    stem_radius -- The radius of the stem at the bottom of the socket
    center_in_ball -- Put the object center in the center of the ball, else at the bottom of the stem

    Return the ball object
    """
    b = Sphere( r=ball_radius )
    h = stem_height + ball_radius
    stem = Cylinder( r=stem_radius, h=h )
    TranslateZ( stem, h / 2 - ( ball_radius + stem_height ) )
    Union( b, stem, True )

    TranslateZ( b, ball_radius + stem_height )
    if center_in_ball:
        SetOrigin( b, 0, 0, ball_radius + stem_height )
    else:
        SetOriginOrigin( b )
    return b

def SocketJoint( ball_radius=10.0,
                 socket_thickness=2.0,
                 socket_finger_gap=4.0,
                 socket_finger_base_offset=5.0,
                 socket_finger_tip_offset=5.0,
                 stem_height=10.0,
                 stem_radius=2.0,
                 center_in_socket=False ):
    """Create a socket of a ball-and-socket joint.

    The socket points up in the Z axis relative to the origin.
    The bottom of the stem is at the origin.

    Keyword arguments:
    ball_radius               -- The radius of the ball
    socket_thickness          -- The thickness of the socket wall
    socket_finger_gap         -- The space between the four "fingers" of the socket
    socket_finger_base_offset -- The offset of the finger base downwards from the center of the socket
    socket_finger_tip_offset  -- The offset of the finger tips, upwards from the center of the socket
    stem_height               -- The height of the stem at the bottom of the socket
    stem_radius               -- The radius of the stem at the bottom of the socket
    center_in_socket          -- Put the object center in the center of the socket, else at the bottom of the stem

    Return the socket object
    """
    socket_radius = ball_radius + socket_thickness
    s = Sphere( r=socket_radius )
    h = stem_height + socket_radius
    stem = Cylinder( r=stem_radius, h=h )
    TranslateZ( stem, h / 2 - ( socket_radius + stem_height ) )
    Union( s, stem, True )

    i = Sphere( r=ball_radius )
    Difference( s, i, True )

    gap_rectangle = RectangularPrism( x=4.0 * ball_radius, y=socket_finger_gap, z = 2.0 * socket_radius )
    TranslateZ( gap_rectangle, socket_radius - socket_finger_base_offset )
    Difference( s, gap_rectangle, False )
    RotateDegZ( gap_rectangle, 90.0 )
    Difference( s, gap_rectangle, True )

    b = Sphere( r=ball_radius )
    TranslateZ( b, socket_finger_tip_offset )
    Difference( s, b, True )

    TranslateZ( s, socket_radius + stem_height )
    if center_in_socket:
        SetOrigin( s, 0, 0, socket_radius + stem_height )
    else:
        SetOriginOrigin( s )
    return s

def BallAndSocketJoint( ball_radius=10.0,
                        socket_thickness=2.0,
                        socket_finger_gap=4.0,
                        socket_finger_base_offset=5.0,
                        socket_finger_tip_offset=5.0,
                        stem_height=10.0,
                        stem_radius=2.0,
                        center_in_ball=False ):
    """Create a ball-and-socket joint in two pieces

    Both pieces will be standing at the origin with the top in the Z direction.
    To get the ball to actually fit in the socket, you'll need to rotate one of the pieces 180 degrees around the X or Y axis.

    Keyword arguments:
    ball_radius               -- The radius of the ball
    socket_thickness          -- The thickness of the socket wall
    socket_finger_gap         -- The space between the four "fingers" of the socket
    socket_finger_base_offset -- The offset of the finger base downwards from the center of the socket
    socket_finger_tip_offset  -- The offset of the finger tips, upwards from the center of the socket
    stem_height               -- The height of the stem at the bottom of the socket
    stem_radius               -- The radius of the stem at the bottom of the socket
    center_in_ball            -- Is the object center in the center of the ball/socket?

    Return a tuple ( ball object, socket object )
    """
    b = BallJoint( ball_radius, stem_height, stem_radius, center_in_ball )
    s = SocketJoint( ball_radius, socket_thickness, socket_finger_gap, socket_finger_base_offset, socket_finger_tip_offset, stem_height, stem_radius, center_in_ball )

    return ( b, s )

def Spring( name=None, major_radius=1.0, major_segments=10, minor_radius=0.1, minor_segments=10, rise=1.0, turns=5, capped=1, location=(0,0,0) ):
    """Draw a spring

    Keyword arguments:
    name            -- The name for the new spring object
    major_radius    -- The radius of the spring, to the center of the extruded circle
    major_segments  -- The number of segments making a full turn of the spring
    minor_radius    -- The radius of the extruded circle forming the spring
    minor_segments  -- The number of segments in each circular cross-section (default is from Blender)
    rise            -- The rise between each full turn
    turns           -- The number of full turns in the spring
    capped          -- Capped ends? (0=No, 1=flat, 2=sphere)
    location        -- The location of the center of the spring

    Return the spring object
    """

    verts = []
    faces = []

    start = ( 0.0, float( major_radius ), 0.0 )
    end   = ( float( turns ) * rise, float( major_radius ), 0.0 )
    verts.append( start )
    circle_verts = CirclePoints( minor_radius, minor_segments, start )

    deg_step  = 360.0 / float( major_segments )
    r = RotationDeg( deg_step, axis=( 1.0, 0.0, 0.0 ), point=( 0.0, 0.0, 0.0 ) )

    rise_step = float( rise ) / float( major_segments )
    t = Translation( ( rise_step, 0.0, 0.0 ) )

    for turn in range( 0, turns ):
        for s in range( 0, major_segments ):
            for v in circle_verts:
                verts.append( v )
            circle_verts = r.apply( circle_verts )
            circle_verts = t.apply( circle_verts )

    for v in circle_verts:
        verts.append( v )

    if capped == 1:
        # Fill in the start face.
        # The vertices are 0 (center), 1, ..., minor_segments
        for v in range( 0, minor_segments - 1 ):
            faces.append( ( 0, v + 2, v + 1 ) )
        faces.append( ( 0, 1, minor_segments ) )

    # Fill in the spring
    turn_step = minor_segments * major_segments 
    for turn in range( 0, turns ):
        for s in range( 0, major_segments ):
            for p in range( 0, minor_segments - 1 ):
                # The start vertices are 1 + turn * ( minor_segments * major_segments ) + s * minor_segments, ..., + minor_segments - 1
                sv1 = 1 + turn * turn_step + s * minor_segments + p
                sv2 = sv1 + 1
                ev1 = sv1 + minor_segments
                ev2 = sv2 + minor_segments
                faces.append( ( sv1, sv2, ev2, ev1 ) )

            sv1 = 1 + turn * turn_step + s * minor_segments + minor_segments - 1
            sv2 = sv1 - ( minor_segments - 1 )
            ev1 = sv1 + minor_segments
            ev2 = sv2 + minor_segments
            faces.append( ( sv1, sv2, ev2, ev1 ) )

    if capped == 1:
        # Fill in the end face.
        s = len( verts ) - minor_segments
        e = len( verts ) - 1
        verts.append( end )
        c = e + 1
        for v in range( s, e ):
            faces.append( ( c, v, v + 1 ) )
        faces.append( ( c, e - 1, s ) )

    m = Mesh( name, verts, [], faces )

    if capped == 2:
        s1 = Sphere( r=minor_radius, location=start )
        s2 = Sphere( r=minor_radius, location=end )
        m = Join( m, s1, s2 )

    return m

def TriangularPrism( name=None, base=2.0, height=1.5, depth=0.5, location=(0,0,0) ):
    """Create a triangular prism, with the base along the X axis, and the top towards positive Y.

    Keyword arguments:
    name     -- The name for the new N-gon object
    base     -- The base of the triangle
    height   -- The height of the triangle
    depth    -- The vertical depth of the prism.
    location -- The location of the center of the N-gon

    Return the triangular prism object
    """

    b2 = base / 2.0
    d2 = depth / 2.0
    verts = ( [ -b2, 0, d2 ], [ b2, 0, d2 ], [ 0, height, d2 ],
              [ -b2, 0, -d2 ], [ b2, 0, -d2 ], [ 0, height, -d2 ] )

    faces = [ ( 0, 1, 2 ), ( 3, 4, 1, 0 ), ( 4, 5, 2, 1 ), ( 5, 3, 0, 2 ), ( 4, 3, 5 ) ]

    return Mesh( name, verts, [], faces )

def Rack( name=None, length=10.0, width=1.0, height=1.0, tooth_height=0.5, tooth_width=0.5, file_depth=0.1 ):
    """Create a rack, suitable for a pinion.

    The length of the rack extends along the X axis, and the teeth point up towards positive Z.
    
    Keyword arguments:
    name         -- The name for the new spring object
    length       -- The lenth of the rack
    width        -- The width of the rack
    height       -- The height of the rack, including the teeth
    tooth_height -- The height of each tooth
    tooth_width  -- The width of each tooth, parallel to the rack's length
    file_depth   -- The amount to file off of each tooth
    
    Return the object
    """
    rck = []
    ht = height - tooth_height
    rack = RectangularPrism( name=name, x=length, y=width, z=ht )
    rck.append( rack )
    tooth = TriangularPrism( base=tooth_width, height=tooth_height, depth=width )
    RotateDegX( tooth, 90 )
    h2 = ht / 2.0

    # Array the teeth
    num_teeth = int( length / tooth_width + 0.5 )
    start_x = - length / 2.0 + tooth_width / 2.0

    for t in range( 0, num_teeth ):
        tuth = Duplicate( tooth )
        TranslateTo( tuth, start_x + t * tooth_width, 0, h2 )
        rck.append( tuth )

    Delete( tooth )

    r = Join( rck )

    if( file_depth > 0.0 ):
        p = Plane( size=length )
        RotateDegX( p, 180 )
        TranslateZ( p, ht / 2.0 + tooth_height - file_depth )
        Difference( r, p, True )

    TranslateTo( r, 0, 0, -h2 )
    SetOriginOrigin( r )

    return r

def Pinion( name=None, r=1.0, h=1.0, tooth_depth=0.5, file_depth=0.1, num_teeth=12, location=(0,0,0) ):
    """Create a pinion, suitable for a rack.

    The length of the rack extends along the X axis, and the teeth point up towards positive Z.
    
    Keyword arguments:
    r             -- The radius of the pinion
    h             -- The height of the pinion
    tooth_depth   -- The depth of the gear teeth
    file_depth    -- The amount to file off of each tooth
    num_teeth     -- The number of teeth
    
    Return the object
    """

    inner_r = r - tooth_depth
    inner_circ = 2.0 * inner_r * math.pi
    base = inner_circ / float( num_teeth )
    step = 360.0 / float( num_teeth )

    tooth = TriangularPrism( base=base, height=tooth_depth, depth=h )
    RotateDegZ( tooth, -90 )
    RotateDegY( tooth, -90 )

    if( file_depth > 0.0 ):
        clip = Cylinder( r=r*2.0, h=h*2.0 )
        hole = Cylinder( r=r-file_depth, h=h*3 )
        Difference( clip, hole, True )

    ob = []
    for t in range( 0, num_teeth ):
        tuth = Duplicate( tooth )
        PositionPolar( tuth, r=inner_r, z_angle=step * t, xy_angle=0.0 )
        if( file_depth > 0.0 ):
            Difference( tuth, clip, False )
        ob.append( tuth )

    Delete( tooth )
    if( file_depth > 0.0 ):
        Delete( clip )

    # cos( step / 2.0 ) = inner_r / nr
    # nr = inner_r / cos( step / 2.0 )
    nr = inner_r / Cos( step / 2.0 )

    center =  NGonPrism( r=nr, h=h, sides=num_teeth )
    RotateDegZ( center, step / 2.0 )
    ob.append( center )

    o = Join( ob )

    TranslateToV( o, location )
    return o
    

#################################################
# Operators and Transformations
#################################################

def Delete( ob=None ):
    """Delete an object

    Keyword arguments:
    ob -- The object to delete

    Return nothing
    """
    if ob is not None:
        Select( ob )
    bpy.ops.object.delete()

def DeleteSelected():
    """Delete the currently selected object

    Keyword arguments:
    None

    Return nothing
    """
    bpy.ops.object.delete()

def Duplicate( ob=None ):
    """Duplicate an object

    Keyword arguments:
    ob -- The object to duplicate. If None, use the currently selected object.

    Return the new object which is a duplicate of the input
    """
    if ob is not None:
        Select( ob )
    bpy.ops.object.duplicate()
    return Current()

def Join( *obs ):
    """Join objects into a single object

    Keyword arguments:
    obs -- The array of objects to join

    Return the new object
    """
    if isinstance( obs[0], list ):
        Select( obs[0] )    # Backward compatibility
    else:
        add = False
        for o in obs:
            Select( o, add )
            add = True
    bpy.ops.object.join()
    return Current()

def SetOrigin( ob, x, y, z ):
    """Set an object's origin

    The object's origin specifies the object's location.
    During rotation, the object's origin is used as the rotation origin.

    Keyword arguments:
    ob -- The object to set the origin on
    x  -- The new X coordinate of the object's origin
    y  -- The new Y coordinate of the object's origin
    z  -- The new Z coordinate of the object's origin

    Return nothing
    """
    # store the location of current 3d cursor
    saved_location = bpy.context.scene.cursor_location  # returns a vector
    
    # give 3dcursor new coordinates
    bpy.context.scene.cursor_location = ( x, y, z )
    
    # set the origin on the current object to the 3dcursor location
    Select( ob )
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    
    # set 3dcursor location back to the stored location
    bpy.context.scene.cursor_location = saved_location

def SetOriginOrigin( ob ):
    """Set an object's origin to the origin.

    The object's origin specifies the object's location.
    During rotation, the object's origin is used as the rotation origin.

    Keyword arguments:
    ob -- The object to set the origin on

    Return nothing
    """
    SetOrigin( ob, 0, 0, 0 )

def SetOriginV( ob, v ):
    """Set an object's origin

    The object's origin specifies the object's location.
    During rotation, the object's origin is used as the rotation origin.

    Keyword arguments:
    ob -- The object to set the origin on
    v  -- The new coordinates of the object's origin

    Return nothing
    """
    SetOrigin( ob, v[0], v[1], v[2] )

def SetOriginCenter( ob ):
    """Set an object's origin to the bounding-box center

    The object's origin specifies the object's location.
    During rotation, the object's origin is used as the rotation origin.

    Keyword arguments:
    ob -- The object to set the origin on

    Return nothing
    """
    bb = ob.bound_box
    ( lx, ly, lz ) = bb[ 0 ]
    ( hx, hy, hz ) = bb[ 6 ]
    SetOrigin( ob, lx + ( hx - lx ) / 2, ly + ( hy - ly ) / 2, lz + ( hz - lz ) / 2 )

def Scale( ob, x, y, z ):
    """Scale an object

    Keyword arguments:
    ob -- The object to scale. None means the currently-selected object.
    x  -- The scale factor along the X-axis
    y  -- The scale factor along the Y-axis
    z  -- The scale factor along the Z-axis

    Return nothing
    """
    if ob is not None:
        Select( ob )
    if russbpy_transform_metatdata:
        bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.transform.resize( value=( x, y, z ) )
    if russbpy_transform_metatdata:
        bpy.ops.object.mode_set(mode = 'OBJECT')

def ScaleX( ob, x ):
    """Scale an object along the X-axis

    Keyword arguments:
    ob -- The object to scale. None means the currently-selected object.
    x  -- The scale factor along the X-axis

    Return nothing
    """
    Scale( ob, x, 1, 1 )

def ScaleY( ob, y ):
    """Scale an object along the Y-axis

    Keyword arguments:
    ob -- The object to scale. None means the currently-selected object.
    y  -- The scale factor along the Y-axis

    Return nothing
    """
    Scale( ob, 1, y, 1 )

def ScaleZ( ob, z ):
    """Scale an object along the Z-axis

    Keyword arguments:
    ob -- The object to scale. None means the currently-selected object.
    z  -- The scale factor along the Z-axis

    Return nothing
    """
    Scale( ob, 1, 1, z )

def ScaleXY( ob, xy ):
    """Scale an object along the Z-axis

    Keyword arguments:
    ob -- The object to scale. None means the currently-selected object.
    xy -- The scale factor along both the X-axis and Y-axis

    Return nothing
    """
    Scale( ob, xy, xy, 1 )

def ScaleUniform( ob, f ):
    """Scale an object uniformly in all 3 axes

    Keyword arguments:
    ob -- The object to scale. None means the currently-selected object.
    f  -- The uniform scale factor

    Return nothing
    """
    Scale( ob, f, f, f )

def ScaleV( ob, v=(1,1,1) ):
    """Scale an object

    Keyword arguments:
    ob -- The object to scale. None means the currently-selected object.
    v  -- The vector of (x,y,z) scale factors

    Return nothing
    """
    Scale( ob, v[0], v[1], v[2] )

def ScaleAll( x, y, z ):
    """Scale all objects

    Keyword arguments:
    x  -- The scale factor along the X-axis
    y  -- The scale factor along the Y-axis
    z  -- The scale factor along the Z-axis

    Return nothing
    """
    SelectAll()
    Scale( None, x, y, z )

def ScaleAllUniform( f ):
    """Scale all objects uniformly in all 3 axes

    Keyword arguments:
    f  -- The uniform scale factor

    Return nothing
    """
    ScaleAll( f, f, f )
    
def Translate( ob, x, y, z ):
    """Translate (move) an object

    Keyword arguments:
    ob -- The object to translate. None means the currently-selected object.
    x  -- The distange to translate along the X-axis
    y  -- The distange to translate along the Y-axis
    z  -- The distange to translate along the Z-axis

    Return nothing
    """
    if ob is not None:
        Select( ob )
    else:
        ob = bpy.context.active_object

    if russbpy_transform_metatdata:
        bpy.ops.object.mode_set(mode = 'EDIT')
    if x is not None:
        bpy.ops.transform.translate( value=( x, y, z ) )
    else:
        ( x, y, z ) = ob.location
        bpy.ops.transform.translate( value=(-x,-y,-z) )
    if russbpy_transform_metatdata:
        bpy.ops.object.mode_set(mode = 'OBJECT')

def TranslateV( ob, v ):
    """Translate (move) an object

    Keyword arguments:
    ob -- The object to translate. None means the currently-selected object.
    v  -- The vector of (x,y,z) distances to translate by

    Return nothing
    """
    Translate( ob, v[0], v[1], v[2] )
    
def TranslateX( ob, x ):
    """Translate (move) an object along the X axis

    Keyword arguments:
    ob -- The object to translate. None means the currently-selected object.
    x  -- The distance to move the object along the X-axis

    Return nothing
    """
    Translate( ob, x, 0, 0 )
    
def TranslateY( ob, y ):
    """Translate (move) an object along the Y axis

    Keyword arguments:
    ob -- The object to translate. None means the currently-selected object.
    y  -- The distance to move the object along the Y-axis

    Return nothing
    """
    Translate( ob, 0, y, 0 )
    
def TranslateZ( ob, z ):
    """Translate (move) an object along the Z axis

    Keyword arguments:
    ob -- The object to translate. None means the currently-selected object.
    z  -- The distance to move the object along the Z-axis

    Return nothing
    """
    Translate( ob, 0, 0, z )

def TranslateTo( ob, x, y, z ):
    """Translate (move) an object to the given point

    Keyword arguments:
    ob -- The object to translate. None means the currently-selected object.
    x  -- The x coordinate of the object's new location
    y  -- The y coordinate of the object's new location
    z  -- The z coordinate of the object's new location

    Return nothing
    """
    Select( ob )
    if russbpy_transform_metatdata:
        bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.transform.translate( value=(x - ob.location[ 0 ], y - ob.location[ 1 ], z - ob.location[ 2 ]) )
    if russbpy_transform_metatdata:
        bpy.ops.object.mode_set(mode = 'OBJECT')

def TranslateToV( ob, v=(1,1,1) ):
    """Translate (move) an object's origin to the given point

    Keyword arguments:
    ob -- The object to translate. None means the currently-selected object.
    v  -- The vector coordinate to move the object's origin to.

    Return nothing
    """
    TranslateTo( ob, v[0], v[1], v[2] )

def RotateRad( ob, angle, axis=(0,0,1.0) ):
    """Rotate an object about its origin

    Keyword arguments:
    ob    -- The object to translate. None means the currently-selected object.
    angle -- The angle to rotate around the axis, in radians
    axis  -- The vector representing the axis to rotate the object around.
             For the purposes of this rotation, the axis vector is translated so 
             it begins at the origin of the object.

    Return nothing
    """
    if ob is not None:
        Select( ob )
    if russbpy_transform_metatdata:
        bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.transform.rotate( value=angle, axis=axis )
    if russbpy_transform_metatdata:
        bpy.ops.object.mode_set(mode = 'OBJECT')

def RotateRadZ( ob, angle ):
    """Rotate an object about the Z axis

    Keyword arguments:
    ob    -- The object to rotate
    angle -- The angle of rotation, in radians

    Return nothing
    """
    RotateRad( ob, angle, axis=(0,0,1.0) )

def DegToRad( deg ):
    """Convert degrees to radians

    Keyword arguments:
    deg -- The degree value to convert

    Return the equivalent angle, in radians
    """
    return ( deg / 180.0 ) * math.pi

def RadToDeg( rad ):
    """Convert radians to degrees

    Keyword arguments:
    rad -- The radians value to convert

    Return the equivalent angle, in degrees
    """
    return ( rad * 180.0 ) / math.pi

def RotateDeg( ob, angle=0, axis=(0,0,1.0) ):
    """Rotate an object using degrees

    Keyword arguments:
    ob    -- The object to translate. None means the currently-selected object.
    angle -- The angle to rotate around the axis, in degrees
    axis  -- The axis to rotate the object around.

    Return nothing
    """
    RotateRad( ob, angle=DegToRad( angle ), axis=axis )

def RotateDegX( ob, angle=0 ):
    """Rotate an object using degrees

    Keyword arguments:
    ob    -- The object to translate. None means the currently-selected object.
    angle -- The angle to rotate around the axis, in degrees

    Return nothing
    """
    RotateDeg( ob, angle=angle, axis=(1.0,0,0) )

def RotateDegY( ob, angle=0 ):
    """Rotate an object using degrees

    Keyword arguments:
    ob    -- The object to translate. None means the currently-selected object.
    angle -- The angle to rotate around the axis, in degrees

    Return nothing
    """
    RotateDeg( ob, angle=angle, axis=(0,1.0,0) )

def RotateDegZ( ob, angle=0 ):
    """Rotate an object using degrees

    Keyword arguments:
    ob    -- The object to translate. None means the currently-selected object.
    angle -- The angle to rotate around the axis, in degrees

    Return nothing
    """
    RotateDeg( ob, angle=angle, axis=(0,0,1.0) )

def GetRotationToV( ob_normal=(0,0,1.0), v=(0,0,1.0) ):
    """Get the angle and axis of rotation to rotate an object towards the given vector.

    Keyword arguments:
    ob_normal -- The object's normal vector
    v         -- The vector to rotate to

    Return ( angle, axis ), where axis is an (X,Y,Z) vector
    """
    # Determine the axis of rotation.
    cp = CrossProductV( ob_normal, v )
    dist = DistanceV( (0.0,0.0,0.0), cp )
    if dist == 0:
        axis = [ 0.0, 0.0, 1.0 ]
    else:
        axis = [ cp[0] / dist, cp[1] / dist, cp[2] / dist ]

    # Determine the angle of rotation.
    dp = DotProductV( v, ob_normal )
    d1 = DistanceV( (0.0,0.0,0.0), v ) 
    d2 = DistanceV( (0.0,0.0,0.0), ob_normal )
    prod = d1 * d2
    if prod != 0:
        cos = dp / prod
        angle = ACos( cos )
    else:
        angle = 0
    return( angle, axis )

def RotateToV( ob, ob_normal=(0,0,1.0), v=(0,0,1.0) ):
    """Rotate an object to the given vector

    Keyword arguments:
    ob        -- The object to rotate
    ob_normal -- The object's normal vector
    v         -- The vector to rotate to

    Return nothing
    """
    ( angle, axis ) = GetRotationToV( ob_normal, v )
    #Print( "RotateToV: angle = %s" % angle )
    #Print( "RotateToV: v  = (%s, %s, %s)" % ( v[0], v[1], v[2] ) )
    if angle != 0:
        RotateDeg( ob, angle=angle, axis=axis )

def PositionPolar( ob, r=1.0, z_angle=0.0, xy_angle=0.0 ):
    """Rotate and position an object, centered on the origin, using polar coordinates

    The object lies flat facing up along the Z+ axis with the base
    parallel to the Y axis on the X+ side.
    then is rotated so that its top face faces outward
    from the imaginary sphere traced by the radius.
    The center of the object will be positioned at the radius.

    Keyword arguments:
    ob        -- The object to position
    r         -- The radius to center the object on
    z_angle   -- The angle (rho) around the Z axis starting at the X+ axis in the range 0..360 (or -180..180).
    xy_angle  -- The angle (theta) above the xy plane in the Z+ direction in the range -90..90

    Return nothing
    """

    # First, rotate the object so it faces through the X+ axis.
    RotateDeg( ob, 90.0, ( 0, 1, 0 ) )

    # Second, move the object out to the radius.
    Translate( ob, r, 0, 0 )

    # Third, Set the object's origin to the origin.
    SetOriginOrigin( ob )

    # Fourth, rotate the object away from the XY plane.
    RotateDeg( ob, xy_angle, ( 0, 1, 0 ) )

    # Fifth, rotate the object around the Z axis.
    RotateDeg( ob, z_angle, ( 0, 0, 1 ) )

def SetColor( ob, rgb=None ):
    """Set an object's color. If the ogject is None, set the current global color.

    Note that as a side-effect, this function creates a new
    Blender material with the color, called "<object-name>_color"

    Keyword arguments:
    ob  -- The object to set the color of
    rgb -- A vector of (r,g,b) (red,green,blue) color intensities
           Each value is in the range [0,1]

    Return nothing
    """
    global russbpy_color

    if ob is not None:
        Select( ob )
    else:
        # Just set the current color
        if rgb is None:
            raise "Cannot set the current color to None"
        russbpy_color = rgb
        return
    if rgb is None:
        rgb = russbpy_color
    mat = bpy.data.materials.new( '%s_color' % ob.name )
    mat.diffuse_color = rgb
    #mat.use_transparency = True
    #mat.transparency_method = 'RAYTRACE'
    #mat.alpha = 0.5
    ob.data.materials.append( mat )
    ob.active_material = mat

def RandomColor( min_r=0, max_r=1.0, min_g=0, max_g=1.0, min_b=0, max_b=1.0 ):
    """Generate a random color

    Keyword arguments:
    min_r -- The minimum red value, in the range [0,1]
    max_r -- The maximum red value, in the range [0,1]
    min_g -- The minimum green value, in the range [0,1]
    max_g -- The maximum green value, in the range [0,1]
    min_b -- The minimum blue value, in the range [0,1]
    max_b -- The maximum blue value, in the range [0,1]

    Return the RGB color
    """
    r = min_r + ( max_r - min_r ) * random()
    g = min_g + ( max_g - min_g ) * random()
    b = min_b + ( max_b - min_b ) * random()

    return ( r, g, b )

def RandomPointInSphere( r=1.0, location=(0,0,0) ):
    """Generate a random point in a sphere

    Keyword arguments:
    r        -- The radius of the sphere
    location -- The location of the center of the rectangular prism

    Return the random point ( x, y, z )
    """
    # Start with polar coordinates.
    r = random() * r
    theta = random() * 360.0
    phi = random() * 180.0

    x = r * Cos( theta ) * Sin( phi ) + location[0]
    y = r * Sin( theta ) * Sin( phi ) + location[1]
    z = r * Cos( phi ) + location[2]

    return ( x, y, z )

def RandomPointInRectangularPrism( x=1, y=2, z=3, location=(0,0,0) ):
    """Generate a random point in a rectangular prism

    Keyword arguments:
    x        -- The length along the X axis
    y        -- The length along the Y axis
    z        -- The length along the Z axis
    location -- The location of the center of the rectangular prism

    Return the random point ( x, y, z )
    """
    x = float( x )
    y = float( y )
    z = float( z )
    rx = ( random() * x - x / 2.0 ) + location[ 0 ]
    ry = ( random() * y - y / 2.0 ) + location[ 1 ]
    rz = ( random() * z - z / 2.0 ) + location[ 2 ]

    return ( rx, ry, rz )
    
def Boolean( ob1, ob2, op, delete=False ):
    """Perform a Boolean CSG (Constructive Solid Geometry) operation

    Keyword arguments:
    ob1    -- The left-hand object
    ob2    -- The right-hand object
    op     -- The Boolean CSG operation ( 'DIFFERENCE', 'INTERSECT', or 'UNION' )
    delete -- Delete ob2 after the operation?

    Return an object that is the result of the operation
    """
    global russbpy_modnum_gen

    Select( ob1 )
    # Add a modifier
    mod = ob1.modifiers.new('joiner', 'BOOLEAN')
    mod.name = "modifier_%d" % russbpy_modnum_gen
    russbpy_modnum_gen = russbpy_modnum_gen + 1
    mod.object = ob2
    mod.operation = op
    
    # Copy materials from one object to the other
    for mat in ob2.data.materials:
        ob1.data.materials.append( mat )

    # Apply modifier
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

    if delete:
        # If requested, delete the second operand
        Delete( ob2 )

    return ob1

def Intersect( ob1, ob2, delete=False ):
    """Intersect ob1 with ob2

    WARNING! This operation can take a LONG time with complex objects!
             It is strongly suggested you minimize the number of calls made to this function.

    This function can fail if vertices and/or faces are within Blender's tolerances
    for points being too close. Consider scaling the object by a factor of 10 or 100
    before calling this function.

    Keyword arguments:
    ob1    -- The left-hand operand
    ob2    -- The right-hand operand
    delete -- Delete ob2 after the operation?

    Return an object consisting of the solid spaces that occur in both ob1 and ob2
    """
    return Boolean( ob1, ob2, 'INTERSECT', delete )
    
def Union( ob1, ob2, delete=False ):
    """Union ob1 and ob2

    WARNING! This operation can take a LONG time with complex objects!
             It is strongly suggested you minimize the number of calls made to this function.
             If you can affort the extra faces, consider using Join() instead.

    This function can fail if vertices and/or faces are within Blender's tolerances
    for points being too close. Consider scaling the object by a factor of 10 or 100
    before calling this function.

    Keyword arguments:
    ob1    -- The left-hand operand
    ob2    -- The right-hand operand
    delete -- Delete ob2 after the operation?

    Return an object consisting of the solid spaces that occur in either ob1 or ob2
    """
    return Boolean( ob1, ob2, 'UNION', delete )
    
def Difference( ob1, ob2, delete=False ):
    """Perform a Boolean CSG (Constructive Solid Geometry) operation

    WARNING! This operation can take a LONG time with complex objects!
             It is strongly suggested you minimize the number of calls made to this function.

    This function can fail if vertices and/or faces are within Blender's tolerances
    for points being too close. Consider scaling the object by a factor of 10 or 100
    before calling this function.

    Keyword arguments:
    ob1    -- The left-hand operand
    ob2    -- The right-hand operand
    delete -- Delete ob2 after the operation?

    Return an object consisting of the solid spaces in ob1 and not in ob2
    """
    return Boolean( ob1, ob2, 'DIFFERENCE', delete )

def Subdivide( ob, times=1, fractal=0, fractal_along_normal=1, seed=1 ):
    """Subdivide the object's faces into smaller areas

    Subdivision is sometimes required for CSG (Constructive Solid Geometry) operations
    to succeed and/or look reasonable.
    
    Use fractal subdivision to create rough textures on object faces

    Keyword arguments:
    ob      -- The object to subdivide
    times   -- The number of times to subdivide, as an integer
    fractal -- The fractal deformation factor to apply to the subdivision
               A value of zero (0) causes subdivision to have uniform faces that remain in the plane of the original face.
               A non-zero value causes subdivision to have maximally jagged faces that extend above and below the plane of the face.
               The larger the value, the higher and deeper the deformation.
    fractal_along_normal
            -- When set to one (1), move vertices along their normals when doing a fractal subdivision.
               When set to zero (0), move vertices in random directions when doing a fractal subdivision.
               A value of zero is more likely to lead to a very spiky object that may not be a valid CSG object.
    seed    -- The random seed value to use when fractal is non-zero.
               The same (fractal,fractal_along_normal,seed) values will always result in the same result on the same object.
           

    Return nothing
    """
    if ob is not None:
        Select( ob )
    bpy.ops.object.editmode_toggle()
    for i in range( 0, times ):
        bpy.ops.mesh.subdivide( fractal=fractal, fractal_along_normal=fractal_along_normal, seed=1 )
    bpy.ops.object.editmode_toggle()

def SubdivideFractal( ob, fractal=1, times=5, seed=1 ):
    """Subdivide an object using a fractal deformation

    This is just a convenience function on top of Subdivide()

    Keyword arguments:
    ob      -- The object to subdivide
    fractal -- The fractal factor to apply to the subdivision, in the range [0,1]
               A value of zero (0) causes subdivision to have uniform faces that remain in the plane of the face.
               A value of one (1) causes subdivision to have maximally jagged faces that extend above and below the plane of the face.
    times   -- The number of times to subdivide, as an integer
    seed    -- The random seed value to use when fractal is non-zero.
               The same (fractal,fractal_along_normal,seed) values will always result in the same result on the same object.

    Return nothing
    """
    Subdivide( ob, fractal=f, times=times, fractal_along_normal=1)

def FaceCenter( ob, face_num=0 ):
    """Determine the point at the center of the given face.

    Keyword arguments:
    ob       -- The object
    face_num -- The zero-based face number to select

    Return the point at the center of the face.
    """
    sum_x = 0
    sum_y = 0
    sum_z = 0
    num_v = len( ob.data.polygons[face_num].vertices )
    for i in range( 0, num_v ):
        v = ob.data.vertices[ ob.data.polygons[face_num].vertices[i] ]
        sum_x += v.co[0]
        sum_y += v.co[1]
        sum_z += v.co[2]
    num_v = float( num_v )
    return( sum_x / num_v, sum_y / num_v, sum_z / num_v )

def Remesh( ob, depth=1 ):
    """Remesh the object into roughly uniform faces

    Keyword arguments:
    ob    -- The object
    depth -- The depth of the remesh (# times to recursively remesh)

    Return nothing
    """
    global russbpy_modnum_gen

    # Remesh for a nicer mesh
    if ob is not None:
        Select( ob )
    mod = ob.modifiers.new('remesher', 'REMESH')
    mod.name = "modifier_%d" % russbpy_modnum_gen
    russbpy_modnum_gen = russbpy_modnum_gen + 1
    mod.use_remove_disconnected = False
    mod.octree_depth = depth
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

def ConvertToWorldCoordinates( ob ):
    """Convert the object's data to world coordinates

    Keyword arguments:
    ob -- The object

    Return nothing
    """
    ob.data.transform( ob.matrix_world )
    ob.matrix_world = Matrix()
    ob.data.update(1)

class Transformation:
    def __init__( self, matrix ):
        """ Set the transformation

        Keyword arguments:
        matrix -- The transformation matrix, of type mathutils.Matrix
        """
        self.matrix = matrix

    def apply( self, point_or_list ):
        """ Apply the transformation

        Keyword arguments:
        point_or_list -- A single point or a list of points to transform

        Return the transformed point or list of points
        """
        if isinstance( point_or_list, list ):
            points = []
            for p in point_or_list:
                points.append( self.matrix * Vec( p ) )
            return points
        else:
            return self.matrix * Vec( point_or_list )

class RotationDeg( Transformation ):
    def __init__( self, angle, axis, point ):
        """ Set the rotation about the given point and axis

        Keyword arguments:
        angle -- The angle of rotation, in degrees
        axis  -- The axis of rotation, as a vector from the origin that will be translated to the point
        point -- The point to rotate around
        """
        r = Matrix.Rotation(DegToRad( angle ), 4, axis)
        t = Matrix.Translation(point)
        super(RotationDeg, self).__init__( t * r * t.inverted() )

class Translation( Transformation ):
    def __init__( self, vector ):
        """ Set the translation

        Keyword arguments:
        vector -- The translation vector
        """
        t = Matrix.Translation(vector)
        super(Translation, self).__init__( t )

#################################################
# Selecting
#################################################

def SelectFace( ob, face_num=0 ):
    """Select a specific face of an object

    The selection of the face can be used to set up transformations that apply only to that face.

    Keyword arguments:
    ob        -- The object containing the face
    face_num  -- The zero-based face number to select

    Return nothing
    """
    if ob is not None:
        Select( ob )

    # Select the given face of the active object.
    bpy.ops.object.mode_set(mode = 'OBJECT')
    obj = bpy.context.active_object

    # deselect everything
    bpy.ops.object.mode_set(mode = 'EDIT')
    SelectNone()

    # Select the face
    bpy.ops.object.mode_set(mode = 'OBJECT')
    obj.data.polygons[face_num].select = True

def SelectVertex( ob, vertex_num=0 ):
    """Select a specific vertex of an object

    The selection of the vertex can be used to set up transformations that apply only to that vertex.

    Keyword arguments:
    ob          -- The object containing the face
    vertex_num  -- The zero-based vertex number to select

    Return nothing
    """
    if ob is not None:
        Select( ob )

    # Select the given face of the active object.
    bpy.ops.object.mode_set(mode = 'OBJECT')
    obj = bpy.context.active_object

#    # deselect everything
#    bpy.ops.object.mode_set(mode = 'EDIT')
#    SelectNone()

    # Select the face
#    bpy.ops.object.mode_set(mode = 'OBJECT')
    obj.data.vertices[vertex_num].select = True

def Select( ob, add=False ):
    """Select an object

    The selection of the object can be used to set up tranformations that only apply to that object.
    In general, it is best to explicitly pass objects around _instead_ of using Select(), but there
    are some Blender operations that work better with the current selection, hence this function.

    Keyword arguments:
    ob  -- The object to select
    add -- Add the object to the current selection?
           Otherwise, the object will be the only object selected.

    Return nothing
    """
    if not add:
        SelectNone()
    if ob is not None:
        if isinstance( ob, list ):
            for o in ob:
                Select( o, add )
                if not add: add = True
        else:
            ob.select = True
    if not add:
        bpy.context.scene.objects.active = ob

def SelectAll():
    """Select all objects

    Keyword arguments:
    None

    Return nothing
    """
    bpy.ops.object.select_all(action='SELECT')

def SelectNone():
    """Deselect all objects

    Keyword arguments:
    None

    Return nothing
    """
    bpy.ops.object.select_all(action='DESELECT')

def ShowAll():
    """Show all objects

    Adjust the Blender viewport to contain all objects, filling the frame with them.

    Keyword arguments:
    None

    Return nothing
    """
    if bpy.context.screen is not None:
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {'area': area, 'region': region }
                        bpy.ops.view3d.view_all(override)

#################################################
# Math
#################################################

def Sin( theta ):
    """Return the sine of an angle in degrees

    Keyword arguments:
    theta -- The angle, in degrees

    Return the sine of the angle
    """
    return math.sin( DegToRad( theta ) )

def ASin( val ):
    """Return the arcsine of a value

    Keyword arguments:
    val -- The sine value

    Return the arcsine of the value
    """
    return RadToDeg( math.asin( val ) )

def Cos( theta ):
    """Return the cosine of an angle

    Keyword arguments:
    theta -- The angle, in degrees

    Return the cosine of the angle
    """
    return math.cos( DegToRad( theta ) )

def ACos( val ):
    """Return the arccosine of a value

    Keyword arguments:
    val -- The cosine value

    Return the arccosine of the value in degrees
    """
    return RadToDeg( math.acos( val ) )

def Tan( theta ):
    """Return the tangent of an angle in degrees

    Keyword arguments:
    theta -- The angle, in degrees

    Return the tangent of the angle
    """
    return math.tan( DegToRad( theta ) )

def ATan( val ):
    """Return the arctangent of a value

    Keyword arguments:
    val -- The tangent value

    Return the arctangent of the value in degrees
    """
    return RadToDeg( math.atan( val ) )

def DotProduct( x1, y1, z1, x2, y2, z2 ):
    """Return the dot product between vector 1 and vector 2

    Keyword arguments:
    x1 -- The x coordinate of vector 1
    y1 -- The y coordinate of vector 1
    z1 -- The z coordinate of vector 1
    x2 -- The x coordinate of vector 2
    y2 -- The y coordinate of vector 2
    z2 -- The z coordinate of vector 2

    Return the dot product of the two vectors
    """
    return x1 * x2 + y1 * y2 + z1 * z2

def DotProductV( v1, v2 ):
    """Return the dot product between vector 1 and vector 2

    Keyword arguments:
    v1 -- The first vector
    v2 -- The second vector

    Return the dot product of the two vectors
    """
    return DotProduct( v1[0], v1[1], v1[2], v2[0], v2[1], v2[2] )

def CrossProduct( x1, y1, z1, x2, y2, z2 ):
    """Return the cross product between vector 1 and vector 2

    Keyword arguments:
    x1 -- The x coordinate of vector 1
    y1 -- The y coordinate of vector 1
    z1 -- The z coordinate of vector 1
    x2 -- The x coordinate of vector 2
    y2 -- The y coordinate of vector 2
    z2 -- The z coordinate of vector 2

    Return the cross product of the two vectors
    """
    return ( y1*z2 - z1*y2, z1*x2 - x1*z2, x1*y2 - y1*x2 )

def CrossProductV( v1=(0,0,0), v2=(0,0,1.0) ):
    """Return the cross product between vector 1 and vector 2

    Keyword arguments:
    v1 -- The first vector
    v2 -- The second vector

    Return the cross product of the two vectors
    """
    return CrossProduct( v1[0], v1[1], v1[2], v2[0], v2[1], v2[2] )

def Vector( p1=(0,0,0), p2=(1,1,1) ):
    """Return the cross vector from p1 to p2

    Keyword arguments:
    p1 -- The first point
    p2 -- The second point

    Return the vector from p1 to p2
    """
    return ( p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2] )

def AddV( v1=(0,0,0), v2=(1,1,1) ):
    """Add one vector to another

    Keyword arguments:
    v1 -- The first vector
    v2 -- The second vector

    Return the sum of the vectors
    """
    return ( v2[0] + v1[0], v2[1] + v1[1], v2[2] + v1[2] )

def SubV( v1=(0,0,0), v2=(1,1,1) ):
    """Subtract one vector from another

    Keyword arguments:
    v1 -- The first vector
    v2 -- The second vector

    Return the difference of v1 minus v2
    """
    return ( v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2] )

def Mul( p=(0.0,0.0,0.0), f=1.0 ):
    """Multiply a vector by a constant factor

    Keyword arguments:
    p -- The point
    f -- The multiplicative factor

    Return the vector multiplied by the factor
    """
    return ( p1[0] * f, p1[1] * f, p1[2] * f )

def NormalizeV( v=(1.0,2.0,3.0) ):
    """Noralize the given vector

    Keyword arguments:
    v -- The vector to normalize

    Return the normalized vector
    """
    l = Distance( 0.0, 0.0, 0.0, v[0], v[1], v[2] )
    f = 1.0 / l
    return( v[0] * f, v[1] * f, v[2] * f )

#################################################
# Info
#################################################

def Dimensions( ob ):
    """Return an object's dimensions

    Keyword arguments:
    ob -- The object

    Return the object's dimensions as (x,y,z)
    """
    return ob.dimensions # (x,y,z)

def Location( ob ):
    """Return the location of an object's origin

    Keyword arguments:
    ob -- The object

    Return the object's location as (x,y,z)
    """
    return ob.location # (x,y,z)

def VertexCount( ob ):
    """Return the number of vertices in the object

    Keyword arguments:
    ob -- The object

    Return the number of vertices
    """
    return len( ob.data.vertices )

def VertexInfo( ob, vert_index ):
    """Return the information for the given object's vertex

    Keyword arguments:
    ob         -- The object
    vert_index -- The vertex index, origin zero

    Return the vertex information, as follows:
	( global_position, normal )
    """
    v = ob.data.vertices[ vert_index ]
    mat = ob.matrix_world
    global_location = ( v.co[0], v.co[1], v.co[2] )
    global_normal = v.normal
    return ( global_location, global_normal )

def Vertices( ob ):
    """Return the vertices of the object as an array

    Keyword arguments:
    ob -- The object

    Return the array of vertices
    """
    vertices = []
    for i in range( 0, VertexCount( ob ) ):
        ( v, vn ) = VertexInfo( ob, i )
        vertices.append( v )
    return vertices

def EdgeCount( ob ):
    """Return the number of edges in the object

    Keyword arguments:
    ob -- The object

    Return the number of edges
    """
    return len( ob.data.edges )

def EdgeInfo( ob, edge_index ):
    """Return the information for the given object's edge

    Keyword arguments:
    ob         -- The object
    edge_index -- The edge index, origin zero

    Return the edge information, as follows:
	( vertex1_index, vertex2_index )
    """
    e = ob.data.edges[ edge_index ]
    return ( e.vertices[0], e.vertices[1] )

def Current():
    """Return the current object

    Note there may be several objects selected, but there can only be one current object.

    Keyword arguments:
    None

    Return the current object
    """
    return bpy.context.object

def Distance( x1, y1, z1, x2, y2, z2 ):
    """Return the distance between two points

    Keyword arguments:
    x1 -- The X coordinate of the first point
    y1 -- The Y coordinate of the first point
    z1 -- The Z coordinate of the first point
    x2 -- The X coordinate of the second point
    y2 -- The Y coordinate of the second point
    z2 -- The Z coordinate of the second point

    Return the distance between (x1,y1,z1) and (x2,y2,z2)
    """
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    return math.sqrt( dx * dx + dy * dy + dz * dz )

def DistanceV( p1, p2 ):
    """Return the distance between two points

    Keyword arguments:
    p1 -- The first (x,y,z) point
    p2 -- The second (x,y,z) point

    Return the distance between p1 and p2
    """
    return Distance( p1[0], p1[1], p1[2], p2[0], p2[1], p2[2] )

#################################################
# Timing
#################################################

def Elapsed( msg=None ):
    """Display the elapsed time, with an optional message

    The elapsed time is shown relative from both the last call to Elapsed() and from program start

    Keyword arguments:
    msg -- An optional text message to display next to the elapsed time

    Return nothing
    """
    global russbpy_last_time

    curr_time = time.time()
    elapsed_time = curr_time - russbpy_last_time
    total_elapsed_time = curr_time - russbpy_start_time
    if msg is not None:
        Print( "===> %6.1fs (%6.1fs total): %s" % ( elapsed_time, total_elapsed_time, msg ) )
    else:
        Print( "===> %6.1fs (%6.1fs total)" % ( elapsed_time, total_elapsed_time ) )
    russbpy_last_time = curr_time

#################################################
# Export
#################################################

def SaveSTL( fn ):
    """Export all objects to an STL file

    Keyword arguments:
    fn -- The filename to export to

    Return nothing
    """
    SelectAll()
    bpy.ops.export_mesh.stl( filepath=fn )

#################################################
# Mainline
#################################################

def Init( fn=32, transform_metadata=False, quiet=False ):
    """ Initialize the russbpy module

    The elapsed time for the Elapsed() function starts when Init() is called.
    All objects are deleted during this call.
    The current cursor location is put to the origin (0,0,0)

    Keyword arguments:
    fn                 -- The fineness setting, which determines how finely objects will be faceted by default
    transform_metadata -- Whether or not metadata gets transformed with objects.

    Return nothing
    """
    global russbpy_fn, russbpy_transform_metatdata, russbpy_quiet, russbpy_start_time, russbpy_last_time, my_log

    my_log = open( "%s.log" % os.path.splitext( sys.argv[ len( sys.argv ) - 1 ] )[0], 'w' )

    russbpy_start_time = time.time()
    russbpy_last_time = russbpy_start_time

    russbpy_fn = fn
    russbpy_transform_metatdata = transform_metadata
    russbpy_quiet = quiet

    # Delete the current objects
    SelectAll()
    DeleteSelected()

    bpy.context.scene.cursor_location = (0,0,0)

def Percent( progress, final, bar_length=0 ):
    """ Return a representation of percent progress

    Keyword arguments:
    progress -- The current progress
    final    -- The final progress value

    Return the percentage representation
    """
    frac = ( float( progress ) / float( final ) )
    pct = 100.0 * frac

    if bar_length > 0:
        bar_prog = int( frac * bar_length )
        bar = '=' * bar_prog + '-' * ( bar_length - bar_prog )
        rep = "%s/%s %s (%5.2f%%)" % ( progress, final, bar, pct )
    else:
        rep = "%s/%s (%5.2f%%)" % ( progress, final, pct )
    return rep

def Print( msg ):
    """ Append a message to the *.log file

    Keyword arguments:
    msg -- The message to append

    Return nothing
    """
    global my_log

    if not russbpy_quiet:
        print( "RJC: %s" % msg )
    my_log.write( "%s\n" % msg )

def PrintV( v, msg ):
    """ Print a vector/point.

    Keyword arguments:
    v   -- The vector/point to print
    msg -- The message to print

    Return nothing
    """
    Print( "%s: (%s, %s, %s)" % ( msg, v[0], v[1], v[2] ) )

def GetFN():
    """ Get the current fineness setting

    Keyword arguments:
    None

    Return the current fineness setting
    """
    return russbpy_fn

def SetFN( fn=32 ):
    """ Set the current fineness setting

    Keyword arguments:
    fn -- The new fineness setting

    Return nothing
    """
    global russbpy_fn

    russbpy_fn = fn

def GetTransformMetadata():
    """ Get the current transform_metadata setting

    Keyword arguments:
    None

    Return the current transform_metadata setting
    """
    return russbpy_transform_metatdata

def SetTransformMetadata( transform_metadata=True ):
    """ Set the current transform_metadata setting

    Keyword arguments:
    transform_metadata -- The new transform_metadata setting

    Return nothing
    """
    global russbpy_transform_metatdata

    russbpy_transform_metatdata = transform_metadata

def Fini():
    """ Finalize the russbpy module

    This function calls ShowAll() to show all objects.
    This function calls SaveSTL() to export all objects to an STL file with the same filename as the main Python module.
    This function calls SelectNone() to remove all selections (which can be distracting).
    Finally, Elapsed() is called to show the total elapsed time since Init() was called.

    Keyword arguments:
    None

    Return nothing
    """
    global my_log
    ShowAll()
    if bpy.context.screen is not None:
        for a in bpy.context.screen.areas:
            if a.type == 'VIEW_3D':
                for s in a.spaces:
                    if s.type == 'VIEW_3D':
                        s.clip_end = 100000000.0
        SaveSTL( "%s.stl" % os.path.splitext( sys.argv[ len( sys.argv ) - 1 ] )[0] )
        bpy.ops.wm.save_as_mainfile( filepath="%s.blend" % os.path.splitext( sys.argv[ len( sys.argv ) - 1 ] )[0] )
    SelectNone()
    Elapsed( "DONE" )
    my_log.close()
