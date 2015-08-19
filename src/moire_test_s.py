#!/usr/bin/env python

from __future__ import division
import time
import math
import random
import sys
import colorsys
sys.path.append('vendor/openpixelcontrol/python_clients') # TODO: use dependency management so we don't need to explicitly point the file to dependent vendor soures
import opc
import color_utils
from rainbow import Rainbow


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
n_struts = 32
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


#def hsv_to_rgb(h, s, v):
#    if s == 0.0: v*=255; return [v, v, v]
#    i = int(h*6.) # XXX assume int() truncates!
#    f = (h*6.)-i; p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
#    if i == 0: return [v, t, p]
#    if i == 1: return [q, v, p]
#    if i == 2: return [p, v, t]
#    if i == 3: return [p, q, v]
#    if i == 4: return [t, p, v]
#    if i == 5: return [v, p, q]


def rainbow(cycle_secs):
    if cycle_secs == 0:
        cycle_secs = 4
    shape = Rainbow(n_struts, n_pixels_strut, cycle_secs)
    shape.set_x(0.0)
    shape.set_y(0.0)
    while True:
        pixels = shape.render()
        client.put_pixels(pixels, channel=0)
        time.sleep(1 / fps)

def rainbow2(cycle_secs):
    if cycle_secs == 0:
        cycle_secs = 4
    c1 = 1000
    i = 0

    shapes = [Rainbow(n_struts//2, n_pixels_strut, cycle_secs) for i in range(2)]
    shapes[0].set_x(0)
    shapes[1].set_y(0)
    shapes[0].set_f1(0.00001)
    shapes[1].set_f1(0.00001)

    while True:
        
        if (i // c1) % 2 == 0:
            print "phase 1"
            shapes[0].inc_x(1/c1)
            shapes[0].inc_y(-1/c1)
            shapes[1].inc_x(-1/c1)
            shapes[1].inc_y(1/c1)
        else:
            print "phase 2"
            shapes[0].inc_x(-1/c1)
            shapes[0].inc_y(1/c1)
            shapes[1].inc_x(1/c1)
            shapes[1].inc_y(-1/c1)

        pixels = shapes[0].render()
        pixels += shapes[1].render()
        i+= 1
        client.put_pixels(pixels, channel=0)
        time.sleep(1 / fps)

    
#    while True:
#        pixels = []
#        t = time.time() - start_time
#        t_step = t % cycle_secs
#        t_norm = t_step / cycle_secs
#        
#        #        if last_t_step > t_step:
#        #            ext = 0.0
#        #            inn = -0.3*dist_max
#        #        x_factor += 0.01
#        #        y_factor -= 0.1
#        
#        a = t * 400 # 2
#        col_val = 0
#        
#        if ext < dist_max:
#            ext += 0.2 * dist_max / cycle_secs
#        
#        if inn < dist_max and t_norm > 0.5:
#            inn += 0.2 * dist_max / cycle_secs
#    
#        for ii in range(n_pixels):
#            color = (0, 0, 0)
#            x = int(ii / n_pixels_strut)  # calc x and y coords (x is strut to strut, y is each pixel along strut)
#            y = ii % n_pixels_strut
#            dist_r = math.sqrt(math.pow(x_factor*(center_x - x), 2) + math.pow(y_factor*(center_y - y), 2))  # distance between pixel and circle center
#            
#            if dist_r < ext:# and t_norm <= 0.5:
#                diff = dist_r - ext
#                col_val = 360*((math.sin((dist_r*dist_r*(1+0.0000*a) - a)*0.000005) + 1) / 2) # TODO: maybe change with normalized distances - should a be added instead of subtracted then?
#                alpha = math.exp(-0.01*diff*diff)#math.pow(dist_r, 2) / math.pow(ext, 2)
#                val = 255 - 255*alpha#255-255*alpha
#                color = colorsys.hsv_to_rgb(col_val, 0.8, val)
#            
#            #            if t_norm > 0.5 and dist_r > inn:
#            #                diff = dist_r - inn
#            #                col_val = 360*((math.sin((dist_r*dist_r - a)*0.000005) + 1) / 2)
#            #                alpha = math.exp(-0.01*diff*diff)#math.pow((dist_max - dist_r), 2) / math.pow((inn), 2)
#            #                val = 255 - 255*alpha
#            #                color = colorsys.hsv_to_rgb(col_val, 1, val)
#            
#            pixels.append(color)
#        client.put_pixels(pixels, channel=0)
#        time.sleep(1 / fps)
#    last_t_step = t_step


# run
if 'single' in program:
    single(speed)
elif 'strut' in program:
    strutwise(speed)
elif 'span' in program:
    spanwise(speed)
elif 'rainbow' in program:
    rainbow(speed)
elif 'rain2' in program:
    rainbow2(speed)
else:
    print 'program does not exist'
