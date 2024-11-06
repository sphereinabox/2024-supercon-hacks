import time # time.sleep_ms

THIRTEEN9_ROW_PERMUTE = [6,7,0,1,2,3,4,5,8]

class Thirteen9Sao:
    def __init__(self, i2c_bus, xform = None, i2c_addr = 0x30):
        self.xform = xform or (0,0,0.0,1.0) # xform_x, xform_y, xform_sin, xform_cos
        
        self.i2c = i2c_bus
        self.i2c_addr = i2c_addr
        self.buf0 = bytearray([0]*180)
        self.buf1 = bytearray([0]*171)        
        # todo: transform x/y coordinates for each light
        
        # [(x,y,start addr, red offset, g offset, b offset)]
        self.buf0_map = [(-17.5, 9.0, 0, 2, 1, 0), (-14.5, 9.0, 3, 1, 0, 2), (-11.5, 9.0, 6, 2, 1, 0), (-8.5, 9.0, 9, 1, 0, 2), (-5.5, 9.0, 12, 2, 1, 0), (-2.5, 9.0, 15, 1, 0, 2), (0.5, 9.0, 18, 2, 1, 0), (3.5, 9.0, 21, 1, 0, 2), (6.5, 9.0, 24, 2, 1, 0), (9.5, 9.0, 27, 1, 0, 2), (-17.5, 12.0, 30, 2, 1, 0), (-14.5, 12.0, 33, 1, 0, 2), (-11.5, 12.0, 36, 2, 1, 0), (-8.5, 12.0, 39, 1, 0, 2), (-5.5, 12.0, 42, 2, 1, 0), (-2.5, 12.0, 45, 1, 0, 2), (0.5, 12.0, 48, 2, 1, 0), (3.5, 12.0, 51, 1, 0, 2), (6.5, 12.0, 54, 2, 1, 0), (9.5, 12.0, 57, 1, 0, 2), (-17.5, 15.0, 60, 2, 1, 0), (-14.5, 15.0, 63, 1, 0, 2), (-11.5, 15.0, 66, 2, 1, 0), (-8.5, 15.0, 69, 1, 0, 2), (-5.5, 15.0, 72, 2, 1, 0), (-2.5, 15.0, 75, 1, 0, 2), (0.5, 15.0, 78, 2, 1, 0), (3.5, 15.0, 81, 1, 0, 2), (6.5, 15.0, 84, 2, 1, 0), (9.5, 15.0, 87, 1, 0, 2), (-17.5, 18.0, 90, 2, 1, 0), (-14.5, 18.0, 93, 1, 0, 2), (-11.5, 18.0, 96, 2, 1, 0), (-8.5, 18.0, 99, 1, 0, 2), (-5.5, 18.0, 102, 2, 1, 0), (-2.5, 18.0, 105, 1, 0, 2), (0.5, 18.0, 108, 2, 1, 0), (3.5, 18.0, 111, 1, 0, 2), (6.5, 18.0, 114, 2, 1, 0), (9.5, 18.0, 117, 1, 0, 2), (-17.5, 21.0, 120, 2, 1, 0), (-14.5, 21.0, 123, 1, 0, 2), (-11.5, 21.0, 126, 2, 1, 0), (-8.5, 21.0, 129, 1, 0, 2), (-5.5, 21.0, 132, 2, 1, 0), (-2.5, 21.0, 135, 1, 0, 2), (0.5, 21.0, 138, 2, 1, 0), (3.5, 21.0, 141, 1, 0, 2), (6.5, 21.0, 144, 2, 1, 0), (9.5, 21.0, 147, 1, 0, 2), (-17.5, 24.0, 150, 2, 1, 0), (-14.5, 24.0, 153, 1, 0, 2), (-11.5, 24.0, 156, 2, 1, 0), (-8.5, 24.0, 159, 1, 0, 2), (-5.5, 24.0, 162, 2, 1, 0), (-2.5, 24.0, 165, 1, 0, 2), (0.5, 24.0, 168, 2, 1, 0), (3.5, 24.0, 171, 1, 0, 2), (6.5, 24.0, 174, 2, 1, 0), (9.5, 24.0, 177, 1, 0, 2)]
        self.buf1_map = [(-17.5, 3.0, 0, 2, 1, 0), (-14.5, 3.0, 3, 1, 0, 2), (-11.5, 3.0, 6, 2, 1, 0), (-8.5, 3.0, 9, 1, 0, 2), (-5.5, 3.0, 12, 2, 1, 0), (-2.5, 3.0, 15, 1, 0, 2), (0.5, 3.0, 18, 2, 1, 0), (3.5, 3.0, 21, 1, 0, 2), (6.5, 3.0, 24, 2, 1, 0), (9.5, 3.0, 27, 1, 0, 2), (12.5, 3.0, 144, 2, 1, 0), (15.5, 3.0, 147, 1, 0, 2), (18.5, 3.0, 150, 1, 0, 2), (-17.5, 6.0, 30, 2, 1, 0), (-14.5, 6.0, 33, 1, 0, 2), (-11.5, 6.0, 36, 2, 1, 0), (-8.5, 6.0, 39, 1, 0, 2), (-5.5, 6.0, 42, 2, 1, 0), (-2.5, 6.0, 45, 1, 0, 2), (0.5, 6.0, 48, 2, 1, 0), (3.5, 6.0, 51, 1, 0, 2), (6.5, 6.0, 54, 2, 1, 0), (9.5, 6.0, 57, 1, 0, 2), (12.5, 6.0, 153, 2, 1, 0), (15.5, 6.0, 156, 1, 0, 2), (18.5, 6.0, 159, 1, 0, 2), (12.5, 9.0, 90, 2, 1, 0), (15.5, 9.0, 93, 1, 0, 2), (18.5, 9.0, 96, 1, 0, 2), (12.5, 12.0, 99, 2, 1, 0), (15.5, 12.0, 102, 1, 0, 2), (18.5, 12.0, 105, 1, 0, 2), (12.5, 15.0, 108, 2, 1, 0), (15.5, 15.0, 111, 1, 0, 2), (18.5, 15.0, 114, 1, 0, 2), (12.5, 18.0, 117, 2, 1, 0), (15.5, 18.0, 120, 1, 0, 2), (18.5, 18.0, 123, 1, 0, 2), (12.5, 21.0, 126, 2, 1, 0), (15.5, 21.0, 129, 1, 0, 2), (18.5, 21.0, 132, 1, 0, 2), (12.5, 24.0, 135, 2, 1, 0), (15.5, 24.0, 138, 1, 0, 2), (18.5, 24.0, 141, 1, 0, 2), (-17.5, 27.0, 60, 2, 1, 0), (-14.5, 27.0, 63, 1, 0, 2), (-11.5, 27.0, 66, 2, 1, 0), (-8.5, 27.0, 69, 1, 0, 2), (-5.5, 27.0, 72, 2, 1, 0), (-2.5, 27.0, 75, 1, 0, 2), (0.5, 27.0, 78, 2, 1, 0), (3.5, 27.0, 81, 1, 0, 2), (6.5, 27.0, 84, 2, 1, 0), (9.5, 27.0, 87, 1, 0, 2), (12.5, 27.0, 162, 2, 1, 0), (15.5, 27.0, 165, 1, 0, 2), (18.5, 27.0, 168, 1, 0, 2)]
        
        # transform positions
        xform_x, xform_y, xform_sin, xform_cos = self.xform
        for i,thing in enumerate(self.buf0_map):
            # transform by rotation then translation
            x,y,start,r,g,b = thing
            xnew = xform_cos * x - xform_sin * y + xform_x
            ynew = xform_sin * x + xform_cos * y + xform_y
            self.buf0_map[i] = (xnew, ynew, start, r, g, b)
        for i,thing in enumerate(self.buf1_map):
            # transform by rotation then translation
            x,y,start,r,g,b = thing
            xnew = xform_cos * x - xform_sin * y + xform_x
            ynew = xform_sin * x + xform_cos * y + xform_y
            self.buf1_map[i] = (xnew, ynew, start, r, g, b)
    def _unlock(self):
        self.i2c.writeto_mem(self.i2c_addr, 0xFE, bytes([0xC5]))
    def _fillbufs(self,val):
        for i in range(180):
            self.buf0[i] = val
        for i in range(171):
            self.buf1[i] = val
    def init(self):
        # page 4
        self._unlock()
        self.i2c.writeto_mem(self.i2c_addr, 0xFD, bytes([0x04])) # page 4
        # reset
        self.i2c.writeto_mem(self.i2c_addr, 0x3F, bytes([0x01])) # datasheet doesn't say what to write here
        
        time.sleep_ms(10)
        
        # set scaling defaults:
        self._fillbufs(0xFF)
        # page 2 scaling
        self._unlock()
        self.i2c.writeto_mem(self.i2c_addr, 0xFD, bytes([0x02]))
        self.i2c.writeto_mem(self.i2c_addr, 0x00, self.buf0)
        # page 3 scaling
        self._unlock()
        self.i2c.writeto_mem(self.i2c_addr, 0xFD, bytes([0x03]))
        self.i2c.writeto_mem(self.i2c_addr, 0x00, self.buf1)
            
        # set pwm defaults:
        self._fillbufs(0x00)
        # page 0 pwm
        self._unlock()
        self.i2c.writeto_mem(self.i2c_addr, 0xFD, bytes([0x00]))
        self.i2c.writeto_mem(self.i2c_addr, 0x00, self.buf0)
        # page 1 pwm
        self._unlock()
        self.i2c.writeto_mem(self.i2c_addr, 0xFD, bytes([0x01]))
        self.i2c.writeto_mem(self.i2c_addr, 0x00, self.buf1)
        
        # page 4 configuration
        self._unlock()
        self.i2c.writeto_mem(self.i2c_addr, 0xFD, bytes([0x04]))
        # global current
        self.i2c.writeto_mem(self.i2c_addr, 0x01, bytes([0xFE]))
        # configuration (enable)
        self.i2c.writeto_mem(self.i2c_addr, 0x00, bytes([0b0000_1_00_1]))

    def setpixel(self, row, col, r, g, b):
        # row: 0..8 from bottom to top
        # col: 0..12 from left to right
        # set rgb values into self.buf0/self.buf1
        
        # rows aren't in order on PCB, re-order them
        row = THIRTEEN9_ROW_PERMUTE[row]
        
        # color channels alternate BGR RGB except last column?
        if col == 12: r,g,b = g,r,b
        elif col % 2: r,g,b = g,r,b
        else: r,g,b = b,g,r

        if col >= 10:
            # buf_1 0x5A-0xAA
            startaddr = 0x5A+3*(col-10)+9*row
            self.buf1[startaddr] = r
            self.buf1[startaddr+1] = g
            self.buf1[startaddr+2] = b
        elif row >= 6:
            # buf_1 0x00-0x59
            startaddr = 3*col + 30*(row-6)
            self.buf1[startaddr] = r
            self.buf1[startaddr+1] = g
            self.buf1[startaddr+2] = b
        else:
            # buf_0
            startaddr = 3*col + 30*row
            self.buf0[startaddr] = r
            self.buf0[startaddr+1] = g
            self.buf0[startaddr+2] = b
    def flip(self):
        # page 0 pwm
        self._unlock()
        self.i2c.writeto_mem(self.i2c_addr, 0xFD, bytes([0x00]))
        self.i2c.writeto_mem(self.i2c_addr, 0x00, self.buf0)
        # page 1 pwm
        self._unlock()
        self.i2c.writeto_mem(self.i2c_addr, 0xFD, bytes([0x01]))
        self.i2c.writeto_mem(self.i2c_addr, 0x00, self.buf1)
    def flip_off(self):
        self._fillbufs(0x00)
        self.flip()
    def update_leds_by_func_slower(self,func):
        # todo: optimize the computations out of this
        for row in range(9):
            y = 3.0 * row + 3.0
            for col in range(13):
                x = 3.0 * col - 17.5

                # transform
                xform_x, xform_y, xform_sin, xform_cos = self.xform
                xnew = xform_cos * x - xform_sin * y + xform_x
                ynew = xform_sin * x + xform_cos * y + xform_y
                
                color_f = func(xnew, ynew)
                color_f = color_f * color_f
                
                # todo: color gradient
                r = g = b = int(color_f * 255)
                #r,g,b = mygradient(color_f)
                
                self.setpixel(row, col, r, g, b)
    def update_leds_by_func(self,func):
        for x,y,start,ro,go,bo in self.buf0_map:
            color_f = func(x, y)
            color_f = color_f * color_f
            # todo: color gradient
            r = g = b = int(color_f * 255)
            self.buf0[start+ro] = r
            self.buf0[start+go] = g
            self.buf0[start+bo] = b
        for x,y,start,ro,go,bo in self.buf1_map:
            color_f = func(x, y)
            color_f = color_f * color_f
            # todo: color gradient
            r = g = b = int(color_f * 255)
            self.buf1[start+ro] = r
            self.buf1[start+go] = g
            self.buf1[start+bo] = b