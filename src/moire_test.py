#!/usr/bin/env python

from __future__ import division
import time
import math
import random
import sys
sys.path.append('vendor/openpixelcontrol/python_clients') # TODO: use dependency management so we don't need to explicitly point the file to dependent vendor soures
import opc
import color_utils


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
            speed = float(sys.argv[n + 1]) #  TODO: standardize speed on all programs to be speed of an entire cycle ?

# defaults
if 'IP_PORT' not in locals():
    IP_PORT = '127.0.0.1:7890'
if 'program' not in locals():
    program = 'circle'
if 'speed' not in locals():
    speed = 0

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
n_struts = 16
n_pixels_strut = 60
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


def circles(cycle_secs):
    if cycle_secs == 0:
        cycle_secs = 4
    start_time = time.time()
    t_change_pos = -10000
    center_x, center_y = 0.5, 0.5
    r_rand, g_rand, b_rand = 1, 1, 1
    stroke_width = 0.125
    last_t_step = start_time + 100000
    r_max = 0
    while True:
        t = time.time() - start_time
        t_step = t % cycle_secs
        t_norm = t_step / cycle_secs
        rad = t_norm * r_max  # ease_out_quartic(t_step, 0, 1, cycle_secs)
        if last_t_step > t_step:#- t_change_pos > cycle_secs:  # every cycle_secs...
            t_change_pos = t
            center_x, center_y = random.random(), random.random()  # change circle center
            r_rand, g_rand, b_rand = random.random(), random.random(), random.random()  # adjust color
            stroke_width = 0.0625 + random.random() * 0.25  # change circle stroke width
            r_max = max(center_x, center_y, 1 - center_x, 1 - center_y) + stroke_width * 2  # max radius required to get cirlce + stroke beyond visible edges of pixel grid
        pixels = []
        for ii in range(n_pixels):
            x = int(ii / n_pixels_strut)  # calc x and y coords (x is strut to strut, y is each pixel along strut)
            y = ii % n_pixels_strut
            xnorm = x / n_struts  # normalize pixel coordinates
            ynorm = y / n_pixels_strut
            dist = math.sqrt(math.pow(center_x - xnorm, 2) + math.pow(center_y - ynorm, 2))  # distance between pixel and circle center
            intens = 1 - (math.fabs(rad - dist) / stroke_width)  # bright pixels near circle radius, dimmer further away and toward center
            intens = color_utils.remap(color_utils.clamp(intens, 0, 1), 0, 1, 0, 256)
            r, g, b = intens * r_rand, intens * g_rand, intens * b_rand
            pixels.append((r, g, b))
        client.put_pixels(pixels, channel=0)
        time.sleep(1 / fps)
        last_t_step = t_step

# run
if 'single' in program:
    single(speed)
elif 'strut' in program:
    strutwise(speed)
elif 'span' in program:
    spanwise(speed)
elif 'circ' in program:
    circles(speed)
else:
    print 'program does not exist'
