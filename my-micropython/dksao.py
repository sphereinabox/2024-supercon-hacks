class DkSao:
    def __init__(self, i2c_bus, xform = None, i2c_addr = 0x4B):
        self.xform = xform or (0,0,0.0,1.0) # xform_x, xform_y, xform_sin, xform_cos
        
        self.i2c = i2c_bus
        self.i2c_addr = i2c_addr        
        self.buf = bytearray([0x00]*11)
        # todo:
        self.led_locations = [(13.0, 3.0), (13.0, 12.0), (13.0, 21.0), (13.0, 30.0)]
        # transform x/y coordinates for each light
        xform_x, xform_y, xform_sin, xform_cos = self.xform
        for i,thing in enumerate(self.led_locations):
            # transform by rotation then translation
            x,y = thing
            xnew = xform_cos * x - xform_sin * y + xform_x
            ynew = xform_sin * x + xform_cos * y + xform_y
            self.led_locations[i] = (xnew, ynew)
    def init(self):
        self.flip_off()
    def set_pixel(n, val):
        self.buf[n] = val
    def flip_off(self):
        # also mutes tone
        for i in range(11):
            self.buf[i] = 0
        self.flip()
    def flip(self):
        self.i2c.writeto_mem(self.i2c_addr, 0x00, self.buf)
    def update_leds_by_func(self,func):
        for i, xy in enumerate(self.led_locations):
            color_f = func(*xy)
            # Square the color_f value to weight it towards 0. The image will be darker and have higher contrast.
            color_f *= color_f
            self.buf[i] = int(color_f * 255)
    # todo: tone/noTone
    def tone(self, freq):
        # tone doesn't work right now, haven't tried to find why
        if freq > 0:
            self.buf[4] = 1 # play tone
            self.buf[7] = freq & 0xFF
            self.buf[8] = (freq & 0xFF00) >> 8 
            self.buf[9] = (freq & 0xFF0000) >> 16
            self.buf[10] = (freq & 0xFF000000) >> 24
        else:
            self.noTone()
    def noTone(self):
        self.buf[4] = 0 # no tone
        self.buf[7] = 0
        self.buf[8] = 0
        self.buf[9] = 0
        self.buf[10] = 0        
