class Sixteen9Sao:
    def __init__(self, i2c_bus, xform = None, i2c_addr = 0x74):
        self.xform = xform or (0,0,0.0,1.0) # xform_x, xform_y, xform_sin, xform_cos
        
        self.i2c = i2c_bus
        self.i2c_addr = i2c_addr        
        self.display_buf = bytearray([0x00]*144)
        self.led_locations = [(10.0, 45.0), (10.0, 42.46), (10.0, 39.92), (10.0, 37.38), (10.0, 34.84), (10.0, 32.3), (10.0, 29.76), (10.0, 27.22), (10.0, 24.68), (10.0, 22.14), (10.0, 19.6), (10.0, 17.06), (10.0, 14.52), (10.0, 11.98), (10.0, 9.440002), (10.0, 6.900002), (7.46, 45.0), (7.46, 42.46), (7.46, 39.92), (7.46, 37.38), (7.46, 34.84), (7.46, 32.3), (7.46, 29.76), (7.46, 27.22), (7.46, 24.68), (7.46, 22.14), (7.46, 19.6), (7.46, 17.06), (7.46, 14.52), (7.46, 11.98), (7.46, 9.440002), (7.46, 6.900002), (4.92, 45.0), (4.92, 42.46), (4.92, 39.92), (4.92, 37.38), (4.92, 34.84), (4.92, 32.3), (4.92, 29.76), (4.92, 27.22), (4.92, 24.68), (4.92, 22.14), (4.92, 19.6), (4.92, 17.06), (4.92, 14.52), (4.92, 11.98), (4.92, 9.440002), (4.92, 6.900002), (2.38, 45.0), (2.38, 42.46), (2.38, 39.92), (2.38, 37.38), (2.38, 34.84), (2.38, 32.3), (2.38, 29.76), (2.38, 27.22), (2.38, 24.68), (2.38, 22.14), (2.38, 19.6), (2.38, 17.06), (2.38, 14.52), (2.38, 11.98), (2.38, 9.440002), (2.38, 6.900002), (-0.1599998, 45.0), (-0.1599998, 42.46), (-0.1599998, 39.92), (-0.1599998, 37.38), (-0.1599998, 34.84), (-0.1599998, 32.3), (-0.1599998, 29.76), (-0.1599998, 27.22), (-0.1599998, 24.68), (-0.1599998, 22.14), (-0.1599998, 19.6), (-0.1599998, 17.06), (-0.1599998, 14.52), (-0.1599998, 11.98), (-0.1599998, 9.440002), (-0.1599998, 6.900002), (-2.7, 45.0), (-2.7, 42.46), (-2.7, 39.92), (-2.7, 37.38), (-2.7, 34.84), (-2.7, 32.3), (-2.7, 29.76), (-2.7, 27.22), (-2.7, 24.68), (-2.7, 22.14), (-2.7, 19.6), (-2.7, 17.06), (-2.7, 14.52), (-2.7, 11.98), (-2.7, 9.440002), (-2.7, 6.900002), (-5.24, 45.0), (-5.24, 42.46), (-5.24, 39.92), (-5.24, 37.38), (-5.24, 34.84), (-5.24, 32.3), (-5.24, 29.76), (-5.24, 27.22), (-5.24, 24.68), (-5.24, 22.14), (-5.24, 19.6), (-5.24, 17.06), (-5.24, 14.52), (-5.24, 11.98), (-5.24, 9.440002), (-5.24, 6.900002), (-7.779999, 45.0), (-7.779999, 42.46), (-7.779999, 39.92), (-7.779999, 37.38), (-7.779999, 34.84), (-7.779999, 32.3), (-7.779999, 29.76), (-7.779999, 27.22), (-7.779999, 24.68), (-7.779999, 22.14), (-7.779999, 19.6), (-7.779999, 17.06), (-7.779999, 14.52), (-7.779999, 11.98), (-7.779999, 9.440002), (-7.779999, 6.900002), (-10.32, 45.0), (-10.32, 42.46), (-10.32, 39.92), (-10.32, 37.38), (-10.32, 34.84), (-10.32, 32.3), (-10.32, 29.76), (-10.32, 27.22), (-10.32, 24.68), (-10.32, 22.14), (-10.32, 19.6), (-10.32, 17.06), (-10.32, 14.52), (-10.32, 11.98), (-10.32, 9.440002), (-10.32, 6.900002)]
        # transform x/y coordinates for each light
        xform_x, xform_y, xform_sin, xform_cos = self.xform
        for i,thing in enumerate(self.led_locations):
            # transform by rotation then translation
            x,y = thing
            xnew = xform_cos * x - xform_sin * y + xform_x
            ynew = xform_sin * x + xform_cos * y + xform_y
            self.led_locations[i] = (xnew, ynew)
    def init(self):
        # set page to config bank
        self.i2c.writeto_mem(self.i2c_addr, 0xFD, bytes([0x0B]))
        # write config
        init_bytes = bytes([
            # 0x00: configuration register
            0b000_00_000,
            # 0x01 picture display register
            0b00000_000,
            # 0x02 auto play control
            0b0_000_0_000,
            # 0x03 auto play control 2
            0b00_00000,
            # 0x04 reserved (no function)
            0x00,
            # 0x05 display option
            0b00_0_0_0_000,
            # 0x06 audio synchronization register
            0b0000000_0,
            # 0x07 frame state
            0b000_0_0_000,
            # 0x08 breath control
            0b0_000_0_000,
            # 0x09 breath control 2
            0b000_0_0_000,
            # 0x0A shutdown, normal operation
            0b0000000_1,
            # 0x0B AGC control
            0b000_0_0_000,
            # 0x0C audio ADC rate
            0b0000_0000
            ])
        self.i2c.writeto_mem(self.i2c_addr, 0x00, init_bytes)
    
        # reset pages:
        enable_bytes = bytes([0xFF]*18)
        intensity_buf = bytes([0x00]*144)
        for page in range(8):
            # set page
            self.i2c.writeto_mem(self.i2c_addr, 0xFD, bytes([page]))
            # enable outputs
            self.i2c.writeto_mem(self.i2c_addr, 0x00, enable_bytes)
            # set per-pixel intensity
            self.i2c.writeto_mem(self.i2c_addr, 0x24, intensity_buf)
        # set page 0
        self.i2c.writeto_mem(self.i2c_addr, 0xFD, bytes([0]))
    def set_pixel_slow(page, address, val):
        # set page (0xFD is BANK_ADDRESSS)
        self.i2c.writeto_mem(self.i2c_addr, 0xFD, bytes([page]))
        # 0x24 is COLOR_OFFSET
        self.i2c.writeto_mem(self.i2c_addr, 0x24+address, bytes([val]))
    def flip_off(self):
        for i in range(144):
            self.display_buf[i] = 0
        self.flip()
    def flip(self):
        self.i2c.writeto_mem(self.i2c_addr, 0x24, self.display_buf)
        # change active page?
    def setpixel(self, row, col, intensity):
        pixel_addr = 16*row + col
        self.display_buf[pixel_addr] = intensity
    def update_leds_by_func_slower(self,func):
        # row 0 is rightmost column
        # column 0 is topmost row
        # todo: optimize the computations out of this
        for row in range(9):
            x = 10.0 -2.54 * row
            for col in range(16):
                y = 45.0 - 2.54 * col
                
                # transform
                xform_x, xform_y, xform_sin, xform_cos = self.xform
                xnew = xform_cos * x - xform_sin * y + xform_x
                ynew = xform_sin * x + xform_cos * y + xform_y

                color_f = func(xnew, ynew)

                # Square the color_f value to weight it towards 0. The image will be darker and have higher contrast.
                color_f *= color_f
                self.display_buf[16*row + col] = int(color_f * 64)
    def update_leds_by_func(self,func):
        for i, xy in enumerate(self.led_locations):
            color_f = func(*xy)
            # Square the color_f value to weight it towards 0. The image will be darker and have higher contrast.
            color_f *= color_f
            self.display_buf[i] = int(color_f * 64)
    def derp(self):
        result = [None]*144
        # row 0 is rightmost column
        # column 0 is topmost row
        # todo: optimize the computations out of this
        for row in range(9):
            x = 10.0 -2.54 * row
            for col in range(16):
                y = 45.0 - 2.54 * col
                
                result[16*row + col] = (x,y)
        print(result)