#!/usr/bin/env python

from __future__ import division
import time
import math
import random
import sys
sys.path.append('vendor/openpixelcontrol/python_clients') # TODO: use dependency management so we don't need to explicitly point the file to dependent vendor soures
import opc
import color_utils
from circle import Circle
from wave import Wave
from radial_wave import RadialWave

#-------------------------------------------------------------------------------
# handle command line

def usage():
    print
    print '    Usage: moire_test.py [ip:port]'
    print
    print '    If not set, ip:port defauls to 127.0.0.1:7890'
    print
    sys.exit(0)

# process options and flags
for n in range(1, len(sys.argv)):
    if ':' in sys.argv[n] and not sys.argv[n].startswith('-'):
        IP_PORT = sys.argv[n]
    elif sys.argv[n].startswith('-'):
        if sys.argv[n] == '-p':
            program = sys.argv[n + 1]
        elif sys.argv[n] == '-s':
            speed = float(sys.argv[n + 1])  # TODO: standardize speed on all programs to be speed of an entire cycle ?
        elif sys.argv[n] == '--count':
            n_shapes = int(sys.argv[n + 1])
        elif sys.argv[n] == '--blend':
            blend_mode = sys.argv[n + 1]

# defaults
if 'IP_PORT' not in locals():
    IP_PORT = '127.0.0.1:7890'
if 'program' not in locals():
    program = 'circle'
if 'speed' not in locals():
    speed = 0
if 'n_shapes' not in locals():
    n_shapes = 1
if 'blend_mode' not in locals():
    blend_mode = None
#-------------------------------------------------------------------------------
# connect to server

client = opc.Client(IP_PORT)
if client.can_connect():
    print '    connected to %s' % IP_PORT
else:
    # can't connect, but keep running in case the server appears later
    print '    WARNING: could not connect to %s' % IP_PORT
print


#-------------------------------------------------------------------------------
# send pixels

print '    sending pixels forever (control-c to exit)...'
print

n_pixels = 1920  # number of pixels in the included "moire" layout
n_struts = 32
n_pixels_strut = 60
fps = 20         # frames per second


def color(cycle_secs):
    if cycle_secs == 0:
        cycle_secs = 250
    start_time = time.time()
    while True:
        t = time.time() - start_time
        t_step = t % cycle_secs
        t_norm = t_step / cycle_secs
        ii_pixel = int(t_norm * n_pixels)
        pixels = []
        for ii in range(n_pixels):
            r, g, b = 255, 255, 255
            pixels.append((r, g, b))
        client.put_pixels(pixels, channel=0)
        time.sleep(1 / fps)


def single(cycle_secs):
    if cycle_secs == 0:
        cycle_secs = 250
    start_time = time.time()
    while True:
        t = time.time() - start_time
        t_step = t % cycle_secs
        t_norm = t_step / cycle_secs
        ii_pixel = int(t_norm * n_pixels)
        pixels = []
        for ii in range(n_pixels):
            r, g, b = 0, 0, 0
            if ii == ii_pixel:
                r, g, b = 255, 255, 255
            pixels.append((r, g, b))
        client.put_pixels(pixels, channel=0)
        time.sleep(1 / fps)


def strutwise(cycle_secs):
    if cycle_secs == 0:
        cycle_secs = 5
    start_time = time.time()
    while True:
        t = time.time() - start_time
        t_step = t % cycle_secs
        t_norm = t_step / cycle_secs
        ii_strut = int(t_norm * n_struts)
        pixels = []
        r, g, b = 0, 0, 0
        for ii in range(n_pixels):
            r, g, b = 0, 0, 0
            if (ii_strut * n_pixels_strut) < ii < ((ii_strut + 1) * n_pixels_strut):
                r, g, b = 255, 255, 255
            pixels.append((r, g, b))
        client.put_pixels(pixels, channel=0)
        time.sleep(1 / fps)


def spanwise(cycle_secs):
    if cycle_secs == 0:
        cycle_secs = 3
    start_time = time.time()
    while True:
        t = time.time() - start_time
        t_step = t % cycle_secs
        t_norm = t_step / cycle_secs
        ii_span = int(t_norm * n_pixels_strut)
        pixels = []
        for ii in range(n_pixels):
            r, g, b = 0, 0, 0
            if ii % n_pixels_strut == ii_span:
                r, g, b = 255, 255, 255

            pixels.append((r, g, b))
        client.put_pixels(pixels, channel=0)
        time.sleep(1 / fps)


#  t current time zero based counting up to duration, b begin value, c change in value, d total duration
# i.e. ease_out_cubic(1, 0, 5, 4): we are at time 1 out of 4, the entire tween started at 0 and ends at 5
def ease_out_cubic(t, b, c, d):
    t /= d
    t -= 1
    return c*(t*t*t + 1) + b


def ease_out_quartic(t, b, c, d):
    t /= d
    t -= 1
    return -c * (t*t*t*t - 1) + b


def pack_pixels(pxl_channels):
    # pixels = zip(pixels[0::3], pixels[1::3], pixels[2::3])  # pack every 3 values into a tuple (r,g,b)
    pixels = []
    for i in xrange(0, len(pxl_channels), 3):
        pixels.append((pxl_channels[i],
                       pxl_channels[i+1],
                       pxl_channels[i+2]))
    return pixels


def blend_average(n_pixels, shapes):
    pxl_channels = shapes[0].render()
    for shape in shapes[1:]:
        shp_pxls = shape.render()
        pxl_channels = map(lambda px1, px2: px1+px2, pxl_channels, shp_pxls)

    # average
    n_shapes = float(len(shapes))
    pxl_channels = [ch / n_shapes for ch in pxl_channels]

    return pack_pixels(pxl_channels)


def blend_add(n_pixels, shapes):
    pxl_channels = shapes[0].render()
    for shape in shapes[1:]:
        shp_pxls = shape.render()
        pxl_channels = map(lambda px1, px2: px1+px2, pxl_channels, shp_pxls)

    return pack_pixels(pxl_channels)


def blend_subtract(n_pixels, shapes):
    pxl_channels = shapes[0].render()
    for shape in shapes[1:]:
        shp_pxls = shape.render()
        pxl_channels = map(lambda px1, px2: px1-px2, pxl_channels, shp_pxls)

    return pack_pixels(pxl_channels)


def blend_multiply(px1, px2):
    pxl_channels = shapes[0].render()
    for shape in shapes[1:]:
        shp_pxls = shape.render()
        pxl_channels = map(lambda px1, px2: px1*px2, pxl_channels, shp_pxls)

    return pack_pixels(pxl_channels)


def blend_screen(n_pixels, shapes):
    pxl_channels = shapes[0].render()
    for shape in shapes[1:]:
        shp_pxls = shape.render()
        pxl_channels = map(lambda px1, px2: 1.0 - (1.0 - px1) * (1.0 - px2), pxl_channels, shp_pxls)

    return pack_pixels(pxl_channels)


def overlay_pixels(px1, px2):
    if px1 < 0.5:
        return 2.0*px1*px2
    else:
        return 1.0 - 2.0*(1.0 - px1)*(1.0 - px2)


def blend_overlay(n_pixels, shapes):
    pxl_channels = shapes[0].render()
    for shape in shapes[1:]:
        shp_pxls = shape.render()
        pxl_channels = map(overlay_pixels, pxl_channels, shp_pxls)

    return pack_pixels(pxl_channels)


def blend(mode_str, n_pixels, shapes):
    mode_funcs = {
        'avg': blend_average,
        'add': blend_add,
        'sub': blend_subtract,
        'mult': blend_multiply,
        'screen': blend_screen,
        'overlay': blend_overlay,
    }
    func = mode_funcs.get(mode_str, blend_average)
    return func(n_pixels, shapes)


def circles_opposed(cycle_secs, n_shapes=1, blend_mode=None):
    # default params
    if cycle_secs == 0:
        cycle_secs = 4

    # initialize shapes
    c1 = Circle()
    c1.center_x = 0.0
    c1.center_y = 0.5
    c1.randomize_center = False
    c1.randomize_stroke = False
    c2 = Circle()
    c2.center_x = 1.0
    c2.center_y = 0.5
    c2.randomize_center = False
    c2.randomize_stroke = False
    shapes = [c1, c2]

    for shape in shapes:
        shape.n_pixels = n_pixels
        shape.n_struts = n_struts
        shape.n_pixels_strut = n_pixels_strut
        shape.cycle_secs = cycle_secs

    # render loop
    while True:
        # render each shape and apply blend mode
        pixels = blend(blend_mode, n_pixels, shapes)

        # write pixels to opc server
        client.put_pixels(pixels, channel=0)

        # wait one frame-sec before rendering again
        time.sleep(1 / fps)


def circles(cycle_secs, n_shapes=1, blend_mode=None):
    # default params
    if cycle_secs == 0:
        cycle_secs = 4

    # initialize shapes
    shapes = [Circle() for i in range(n_shapes)]

    for shape in shapes:
        shape.randomize_cycle = True
        shape.n_pixels = n_pixels
        shape.n_struts = n_struts
        shape.n_pixels_strut = n_pixels_strut
        shape.cycle_secs = cycle_secs

    # render loop
    while True:
        # render each shape and apply blend mode
        pixels = blend(blend_mode, n_pixels, shapes)

        # write pixels to opc server
        client.put_pixels(pixels, channel=0)

        # wait one frame-sec before rendering again
        time.sleep(1 / fps)


def shapes(cycle_secs, blend_mode=None):
    # default params
    if cycle_secs == 0:
        cycle_secs = 4

    # initialize shapes
    w1 = Wave()
    w1.center_x = 0.0
    w1.center_y = 0.5
    w1.r_rand, w1.g_rand, w1.b_rand = random.random(), random.random(), random.random()
    w2 = Wave()
    w2.center_x = 0.2
    w2.center_y = 0.5
    w2.r_rand, w2.g_rand, w2.b_rand = random.random(), random.random(), random.random()
    shapes = [
        w1,
        w2,
    ]

    for shape in shapes:
        shape.n_pixels = n_pixels
        shape.n_struts = n_struts
        shape.n_pixels_strut = n_pixels_strut
        shape.cycle_secs = cycle_secs

    # render loop
    while True:
        # render each shape and apply blend mode
        pixels = blend(blend_mode, n_pixels, shapes)

        # write pixels to opc server
        client.put_pixels(pixels, channel=0)

        # wait one frame-sec before rendering again
        time.sleep(1 / fps)


def radial_wave(cycle_secs, blend_mode=None):
    # default params
    if cycle_secs == 0:
        cycle_secs = 4

    # initialize shapes
    w1 = RadialWave()
    w1.center_x = 0.5
    w1.center_y = 0.5
    w1.r_rand, w1.g_rand, w1.b_rand = random.random(), random.random(), random.random()

    w2 = RadialWave()
    w2.center_x = 0.4
    w2.center_y = 0.4
    w2.r_rand, w2.g_rand, w2.b_rand = x`random.random(), random.random(), random.random()

    w3 = RadialWave()
    w3.center_x = 0.5
    w3.center_y = 0.5
    w3.r_rand, w3.g_rand, w3.b_rand = random.random(), random.random(), random.random()
    shapes = [
        w1,
        w2,
        # w3,
    ]

    for shape in shapes:
        shape.n_pixels = n_pixels
        shape.n_struts = n_struts
        shape.n_pixels_strut = n_pixels_strut
        shape.cycle_secs = cycle_secs
    w2.cycle_secs = 5

    # render loop
    while True:
        # render each shape and apply blend mode
        pixels = blend(blend_mode, n_pixels, shapes)

        # write pixels to opc server
        client.put_pixels(pixels, channel=0)

        # wait one frame-sec before rendering again
        time.sleep(1 / fps)

# run
if 'color' in program:
    color(speed)
elif 'single' in program:
    single(speed)
elif 'strut' in program:
    strutwise(speed)
elif 'span' in program:
    spanwise(speed)
elif 'circles_opposed' in program:
    circles_opposed(speed, n_shapes, blend_mode)
elif 'circles' in program:
    circles(speed, n_shapes, blend_mode)
elif 'shapes' in program:
    shapes(speed, blend_mode)
elif 'radial_wave' in program:
    radial_wave(speed, blend_mode)
else:
    print 'program does not exist'
