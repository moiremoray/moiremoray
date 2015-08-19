import time
import math
import colorsys

class Rainbow:

    def __init__(self, n_st, n_pix_str, cycle_s):
        self.n_struts = n_st
        self.n_pixels_strut = n_pix_str
        self.n_pixels = self.n_struts * self.n_pixels_strut
        self.cycle_secs = cycle_s
        self.start_time = time.time()
        self.center_x, self.center_y = 0.5 * self.n_struts, 0.5 * self.n_pixels_strut
        self.dist_max = math.sqrt(math.pow(self.n_struts, 2) + math.pow(self.n_pixels_strut, 2))
        self.ext = 0
        self.x_factor = 1.0
        self.y_factor = 1.0
        self.f1 = 5e-06

    def set_x(self, x):
        self.x_factor = x

    def set_y(self, y):
        self.y_factor = y

    def inc_x(self, n):
        self.x_factor += n

    def inc_y(self, n):
        self.y_factor += n

    def get_x(self):
        return self.x_factor

    def get_y(self):
        return self.y_factor

    def set_f1(self, n):
        self.f1 = n

    def render(self):
        t = time.time() - self.start_time
        t_step = t % self.cycle_secs
        self.pixels = []
        a = t * 400
        col_val = 0
        if self.ext < self.dist_max:
            self.ext += 0.2 * self.dist_max / self.cycle_secs
        for ii in range(self.n_pixels):
            color = (0, 0, 0)
            x = int(ii / self.n_pixels_strut)
            y = ii % self.n_pixels_strut
            dist_r = math.sqrt(math.pow(self.x_factor * (self.center_x - x), 2) + math.pow(self.y_factor * (self.center_y - y), 2))
            if dist_r < self.ext:
                diff = dist_r - self.ext
                col_val = 360 * ((math.sin((dist_r * dist_r * (1 + 0.0 * a) - a) * self.f1) + 1) / 2)
                alpha = math.exp(-0.01 * diff * diff)
                val = 255 - 255 * alpha
                color = colorsys.hsv_to_rgb(col_val, 0.8, val)
            self.pixels.append(color)

        return self.pixels
