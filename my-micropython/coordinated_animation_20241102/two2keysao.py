class Two2KeySao:
    def __init__(self, i2c_bus, xform = None, i2c_addr = 0x5A):
        self.xform = xform or (0,0,0.0,1.0) # xform_x, xform_y, xform_sin, xform_cos
        
        self.i2c = i2c_bus
        self.i2c_addr = i2c_addr
        self.buf = bytearray([0]*12)
        
        # [(x,y,start addr, red offset, g offset, b offset)]
        self.led_locations = [(-9.52,26.0),(9.52,26.0),(-9.52,6.98),(9.52,6.98)]
        
        # transform positions
        xform_x, xform_y, xform_sin, xform_cos = self.xform
        for i,thing in enumerate(self.led_locations):
            # transform by rotation then translation
            x,y = thing
            xnew = xform_cos * x - xform_sin * y + xform_x
            ynew = xform_sin * x + xform_cos * y + xform_y
            self.led_locations[i] = (xnew, ynew)
    def init(self):
        pass

    def setpixel(self, row, col, r, g, b):
        # row: 0..1 from top to bottom
        # col: 0..1 from left to right
        self.buf[col*3 + row*6] = r
        self.buf[col*3 + row*6+1] = g
        self.buf[col*3 + row*6+2] = b
    def flip(self):
        self.i2c.writeto_mem(self.i2c_addr, 0x01, self.buf)
    def flip_off(self):
        for i in range(12):
            self.buf[i] = 0x00
        self.flip()
    def update_leds_by_func(self,func):
        for i, xy in enumerate(self.led_locations):
            color_f = func(*xy)
            # Square the color_f value to weight it towards 0. The image will be darker and have higher contrast.
            color_f *= color_f
            # todo: color gradient
            r = g = b = int(color_f * 255)
            self.buf[i*3] = r
            self.buf[i*3+1] = g
            self.buf[i*3+2] = b
