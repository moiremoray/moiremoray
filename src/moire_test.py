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

# defaults
if 'IP_PORT' not in locals():
    IP_PORT = '127.0.0.1:7890'
if 'program' not in locals():
    program = 'circle'
if 'speed' not in locals():
    speed = 0
if 'n_shapes' not in locals():
    n_shapes = 1
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

n_pixels = 6272  # number of pixels in the included "moire" layout
n_struts = 49
n_pixels_strut = 128
fps = 20         # frames per second


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


def circles(cycle_secs, n_shapes=1):
    # default params
    if cycle_secs == 0:
        cycle_secs = 4

    shapes = [Circle() for i in range(n_shapes)]
    for shape in shapes:
        shape.n_pixels = n_pixels
        shape.n_struts = n_struts
        shape.n_pixels_strut = n_pixels_strut
        shape.cycle_secs = cycle_secs

    while True:
        pxl_channels = [0] * n_pixels * 3  # r g b
        for shape in shapes:
            shp_pxls = shape.render()
            pxl_channels = map(lambda px1, px2: px1+px2, pxl_channels, shp_pxls)

        # average
        n_shapes = float(len(shapes))
        pxl_channels = [ch / n_shapes for ch in pxl_channels]

        # pixels = zip(pixels[0::3], pixels[1::3], pixels[2::3])  # pack every 3 values into a tuple (r,g,b)
        pixels = []
        for i in xrange(0, len(pxl_channels), 3):
            pixels.append((pxl_channels[i],
                           pxl_channels[i+1],
                           pxl_channels[i+2]))

        client.put_pixels(pixels, channel=0)
        time.sleep(1 / fps)

# run
if 'single' in program:
    single(speed)
elif 'strut' in program:
    strutwise(speed)
elif 'span' in program:
    spanwise(speed)
elif 'circ' in program:
    circles(speed, n_shapes)
else:
    print 'program does not exist'
