
PETAL_ADDRESS = 0x00

class PetalSao:
    def __init__(self, i2c_bus, xform = None):
        xform_x, xform_y, xform_sin, xform_cos = xform or (0,0,0.0,1.0)
        
        self.petal_bus = i2c_bus
        self.b_alloff = bytearray([0x0]*8)
        # pixel buffer, for 2-bit intensity
        self.bl = bytearray([0x0]*8)
        self.bh = bytearray([0x0]*8)
        # update all at once:
        #petal_bus.writeto_mem(PETAL_ADDRESS, 1, b)
        self.petal_leds = [
            # byte, mask, x, y
            (0,0x40,7.60191520000012,48.2754939999999),#0A 
            (0,0x20,3.05531520000022,47.8945448),#0B 
            (0,0x10,-1.23725940000008,46.3705448),#0C 
            (0,0x08,-4.43765940000003,43.5257194),#0D 
            (0,0x04,-6.6982594000001,39.7411193999999),#0E 
            (0,0x02,-7.48151919999987,34.9029019999999),#0F 
            (0,0x01,-5.19968479999989,30.9527701999999),#0G 
            (1,0x40,-7.35868479999976,49.0883447999998),#1A 
            (1,0x20,-10.1018847999999,45.1513447999998),#1B 
            (1,0x10,-11.4576605999998,40.6382219999998),#1C 
            (1,0x08,-11.8141749999998,35.9559098),#1D 
            (1,0x04,-11.2956594,31.4607447999999),#1E 
            (1,0x02,-9.05718279999996,27.6478491999999),#1F 
            (1,0x01,-4.84032559999969,26.6498323999999),#1G 
            (1,0x80,-0.199898000000076,29.809948),#1P Red (pkg center)
            (2,0x40,-16.3248593999999,37.6329448),#2A 
            (2,0x20,-16.5026593999999,33.0609448),#2B 
            (2,0x10,-15.5374594,28.6921447999999),#2C 
            (2,0x08,-13.1244594,24.8821447999999),#2D 
            (2,0x04,-9.6700593999999,22.1389701999999),#2E 
            (2,0x02,-5.02191019999964,21.8849701999999),#2F 
            (2,0x01,-1.31351019999988,24.2979448),#2G 
            (2,0x80,-0.199898000000076,29.809948),#2P Green (pkg center)
            (3,0x40,-16.1724594,21.2499701999999),#3A 
            (3,0x20,-13.5054848,18.3543447999999),#3B 
            (3,0x10,-9.64468479999982,16.8049701999998),#3C 
            (3,0x08,-5.58068479999997,16.7287702),#3D 
            (3,0x04,-1.74528480000004,18.1511701999999),#3E 
            (3,0x02,1.37888980000025,20.9451447999999),#3F 
            (3,0x01,3.02988980000032,24.8313194),#3G 
            (3,0x80,-0.199898000000076,29.809948),#3P Blue (pkg center)
            (4,0x40,-7.94288479999977,11.4709955999999),#4A 
            (4,0x20,-3.26931019999961,11.7249448),#4B 
            (4,0x10,0.896289800000204,13.2489448),#4C 
            (4,0x08,4.09668980000038,16.0937701999999),#4D 
            (4,0x04,6.35728980000022,19.8783702),#4E 
            (4,0x02,7.13168500000006,24.7162066),#4F 
            (4,0x01,4.85871520000001,28.6667193999999),#4G 
            (5,0x40,7.01771520000011,10.5311447999999),#5A 
            (5,0x20,9.76088980000031,14.4681447999999),#5B 
            (5,0x10,11.1166910000002,18.9812675999999),#5C 
            (5,0x08,11.4732054000001,23.6635798),#5D 
            (5,0x04,11.0054898000001,28.1587447999999),#5E 
            (5,0x02,8.71621320000008,31.9716404),#5F 
            (5,0x01,4.49935600000026,32.9696317999999),#5G 
            (6,0x40,15.9838898000003,21.7325447999999),#6A 
            (6,0x20,16.1616898000004,26.5331447999999),#6B 
            (6,0x10,15.1964898000001,30.9273447999999),#6C 
            (6,0x08,12.9358898000003,34.7373447999998),#6D 
            (6,0x04,9.32908980000025,37.2265193999999),#6E 
            (6,0x02,4.68094060000021,37.7345194),#6F 
            (6,0x01,0.972540600000002,35.3215448),#6G 
            (7,0x40,15.8314898000001,38.3695193999999),#7A 
            (7,0x20,13.1645152000001,41.2651193999999),#7B 
            (7,0x10,9.30371519999994,42.8145193999999),#7C 
            (7,0x08,5.23971520000009,42.8907194),#7D 
            (7,0x04,1.40431520000016,41.4683193999999),#7E 
            (7,0x02,-1.7198593999999,38.6743447999999),#7F 
            (7,0x01,-3.37085939999997,34.7881447999999),#7G
            ]
        # transform positions
        for i,thing in enumerate(self.petal_leds):
            # transform by rotation then translation
            digit, mask, x, y = thing
            xnew = xform_cos * x - xform_sin * y + xform_x
            ynew = xform_sin * x + xform_cos * y + xform_y
            self.petal_leds[i] = (digit, mask, xnew, ynew)
    def init(self):
        self.petal_bus.writeto_mem(PETAL_ADDRESS, 0x09, bytes([0x00]))  ## raw pixel mode (not 7-seg) 
        self.petal_bus.writeto_mem(PETAL_ADDRESS, 0x0A, bytes([0x09]))  ## intensity (of 16) 
        self.petal_bus.writeto_mem(PETAL_ADDRESS, 0x0B, bytes([0x07]))  ## enable all segments
        self.petal_bus.writeto_mem(PETAL_ADDRESS, 0x0C, bytes([0x81]))  ## undo shutdown bits 
        self.petal_bus.writeto_mem(PETAL_ADDRESS, 0x0D, bytes([0x00]))  ##  
        self.petal_bus.writeto_mem(PETAL_ADDRESS, 0x0E, bytes([0x00]))  ## no crazy features (default?) 
        self.petal_bus.writeto_mem(PETAL_ADDRESS, 0x0F, bytes([0x00]))  ## turn off display test mode 
    def flip(self):
        self.petal_bus.writeto_mem(PETAL_ADDRESS, 1, self.bh)
    def flip_grays_slow(self):
        # slow 2-bit grayscale
        self.petal_bus.writeto_mem(PETAL_ADDRESS, 1, bl)
        time.sleep_us(800)
        self.petal_bus.writeto_mem(PETAL_ADDRESS, 1, bh)
        time.sleep_ms(5)
    def flip_off(self):
        self.petal_bus.writeto_mem(PETAL_ADDRESS, 1, self.b_alloff)
    def flip_amberon(self):
        self.petal_bus.writeto_mem(PETAL_ADDRESS, 1, bytearray([0b01111111]*8))
    def update_leds_by_func(self,func):
        for digit, mask, x, y in self.petal_leds:
            intensity = func(x,y)
            ib = int((intensity * intensity) * 4)
            hb = ib & 0x2
            lb = ib & 0x1
#             hb = 0.5 < intensity
#             lb = (0.35 < intensity) and (intensity < 0.5) or (0.8 < intensity)
            if lb: self.bl[digit] = self.bl[digit] | mask
            else: self.bl[digit] = self.bl[digit] & ~mask
            if hb: self.bh[digit] = self.bh[digit] | mask
            else: self.bh[digit] = self.bh[digit] & ~mask



