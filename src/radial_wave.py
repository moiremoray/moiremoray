import time
import math
import random
import color_utils


class RadialWave:

    n_pixels = 0
    n_struts = 0
    n_pixels_strut = 0
    cycle_secs = 0
    randomize_center = False
    randomize_stroke = False
    randomize_cycle = False
    randomize_color = False

    def __init__(self):
        self.start_time = time.time()
        # self.t_change_pos = -10000
        self.center_x, self.center_y = 0.5, 0.5
        self.r_rand, self.g_rand, self.b_rand = 1, 1, 1
        self.stroke_width = 0.125
        self.last_t_step = self.start_time + 100000
        self.r_max = 1

    def render(self):
        t = time.time() - self.start_time
        t_step = t % self.cycle_secs
        t_norm = t_step / self.cycle_secs
        rad = t_norm * self.r_max  # ease_out_quartic(t_step, 0, 1, cycle_secs)
        if self.last_t_step > t_step:  # - t_change_pos > cycle_secs:  # every cycle_secs...
            # t_change_pos = time
            # random.seed(self)
            if self.randomize_center:
                self.center_x, self.center_y = random.random(), random.random()  # change circle center
            if self.randomize_color:
                self.r_rand, self.g_rand, self.b_rand = random.random(), random.random(), random.random()  # adjust color
            if self.randomize_stroke:
                self.stroke_width = 0.0625 + random.random() * 0.15  # change circle stroke width
            self.r_max = max(self.center_x, self.center_y, 1 - self.center_x, 1 - self.center_y) + self.stroke_width * 2  # max radius required to get cirlce + stroke beyond visible edges of pixel grid
            if self.randomize_cycle:
                self.cycle_secs = 3 + int(random.random() * 5)

        self.pixels = []
        domain = math.pi * 2
        for ii in range(self.n_pixels):
            n_pixels_strut = float(self.n_pixels_strut)
            x = int(ii / n_pixels_strut)  # calc x and y coords (x is strut to strut, y is each pixel along strut)
            y = ii % n_pixels_strut
            xnorm = x / float(self.n_struts)  # normalize pixel coordinates
            ynorm = y / n_pixels_strut
            dist = 2 * math.sqrt(math.pow(self.center_x - xnorm, 2) + math.pow(self.center_y - ynorm, 2))  # distance between pixel and circle center
            intens = math.sin(t_norm * dist * domain * 10)
            intens = color_utils.remap(intens, -1, 1, 0, 256)
            # intens = 1 - (math.fabs(rad - dist) / self.stroke_width)  # bright pixels near circle radius, dimmer further away and toward center
            # intens = color_utils.remap(color_utils.clamp(intens, 0, 1), 0, 1, 0, 256)
            r, g, b = intens * self.r_rand, intens * self.g_rand, intens * self.b_rand
            self.pixels.append(r)
            self.pixels.append(g)
            self.pixels.append(b)
        self.last_t_step = t_step
        return self.pixels
