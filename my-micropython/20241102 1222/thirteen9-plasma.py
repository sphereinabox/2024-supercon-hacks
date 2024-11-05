# is31FL3741 i2c pwm LED matrix driver
# adafruit https://www.adafruit.com/product/5201

# i2c addr 0x30
# alternate addresses 0x31, 0x32, 0x33


thirteen9_i2c = i2c0
thirteen9_addr = 0x30
thirteen9_buf0 = bytearray([0]*180)
thirteen9_buf1 = bytearray([0]*171)

def thirteen9_unlock():
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0xFE, bytes([0xC5]))
def thirteen9_fillbufs(val):
    for i in range(180):
        thirteen9_buf0[i] = val
    for i in range(171):
        thirteen9_buf1[i] = val

def thirteen9_init():
    # page 4
    thirteen9_unlock()
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0xFD, bytes([0x04])) # page 4
    # reset
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0x3F, bytes([0x01])) # datasheet doesn't say what to write here
    
    time.sleep_ms(10)
    
    # set scaling defaults:
    thirteen9_fillbufs(0xFF)
    # page 2 scaling
    thirteen9_unlock()
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0xFD, bytes([0x02]))
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0x00, thirteen9_buf0)
    # page 3 scaling
    thirteen9_unlock()
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0xFD, bytes([0x03]))
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0x00, thirteen9_buf1)
        
    # set pwm defaults:
    thirteen9_fillbufs(0x00)
    # page 0 pwm
    thirteen9_unlock()
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0xFD, bytes([0x00]))
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0x00, thirteen9_buf0)
    # page 1 pwm
    thirteen9_unlock()
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0xFD, bytes([0x01]))
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0x00, thirteen9_buf1)
    
    # page 4 configuration
    thirteen9_unlock()
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0xFD, bytes([0x04]))
    # global current
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0x01, bytes([0xFE]))
    # configuration (enable)
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0x00, bytes([0b0000_1_00_1]))    

thirteen9_row_permute = [6,7,0,1,2,3,4,5,8]
def thirteen9_setpixel(row, col, r, g, b):
    # row: 0..8
    # col: 0..12
    # set rgb values into thirteen9_buf0/thirteen9_buf1
    
    # rows aren't in order on PCB, re-order them
    row = thirteen9_row_permute[row]
    
    # color channels alternate BGR RGB except last column?
    if col == 12: r,g,b = g,r,b
    elif col % 2: r,g,b = g,r,b
    else: r,g,b = b,g,r

    if col >= 10:
        # buf_1 0x5A-0xAA
        startaddr = 0x5A+3*(col-10)+9*row
        thirteen9_buf1[startaddr] = r
        thirteen9_buf1[startaddr+1] = g
        thirteen9_buf1[startaddr+2] = b
    elif row >= 6:
        # buf_1 0x00-0x59
        startaddr = 3*col + 30*(row-6)
        thirteen9_buf1[startaddr] = r
        thirteen9_buf1[startaddr+1] = g
        thirteen9_buf1[startaddr+2] = b
    else:
        # buf_0
        startaddr = 3*col + 30*row
        thirteen9_buf0[startaddr] = r
        thirteen9_buf0[startaddr+1] = g
        thirteen9_buf0[startaddr+2] = b
        

def thirteen9_sendbuf():
    # page 0 pwm
    thirteen9_unlock()
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0xFD, bytes([0x00]))
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0x00, thirteen9_buf0)
    # page 1 pwm
    thirteen9_unlock()
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0xFD, bytes([0x01]))
    thirteen9_i2c.writeto_mem(thirteen9_addr, 0x00, thirteen9_buf1)


thirteen9_init()

# for row in range(9):
#     for col in range(13):
#         thirteen9_setpixel(row, col, 0, 0, 127)
#         thirteen9_sendbuf()
#         time.sleep_ms(250)
#         thirteen9_setpixel(row, col, 0, 0, 0)
#         thirteen9_sendbuf()
        
# 
# def thirteen9_setaddr_slow(addr, val):
#     if addr < 180:
#         # page 0
#         thirteen9_unlock()
#         thirteen9_i2c.writeto_mem(thirteen9_addr, 0xFD, bytes([0x00]))
#         thirteen9_i2c.writeto_mem(thirteen9_addr, addr, bytes([val]))
#     else:
#         # page 1
#         thirteen9_unlock()
#         thirteen9_i2c.writeto_mem(thirteen9_addr, 0xFD, bytes([0x01]))
#         thirteen9_i2c.writeto_mem(thirteen9_addr, addr - 180, bytes([val]))
# for addr in range(350):
#     thirteen9_setaddr_slow(addr, 128)
#     time.sleep_ms(250)
#     thirteen9_setaddr_slow(addr, 0)


gr = (0.0,0.0,1.0,0.0)
gg = (0.0,0.0,0.0,1.0)
gb = (0.0,1.0,0.0,0.0)

# def mygradient(f):
#     f = min(1.0,max(0,f))
#     fi = int(f*3)
#     ff = 3*(f % 0.33)
#     ff2 =1-ff
#     return (
#         int(255*(gr[fi]*ff+gr[fi+1]*ff2)),
#         int(255*(gg[fi]*ff+gg[fi+1]*ff2)),
#         int(255*(gb[fi]*ff+gb[fi+1]*ff2)))
    

# plasma
from math import sin, sqrt

# copied from LoLShield_Plasma example
phase = 0.0
phaseIncrement = 0.08
colorStretch = 0.11

while True:
    phase += phaseIncrement

    p1 = ( (sin(phase*1.000)+1.0) * 7.5, (sin(phase*1.310)+1.0) * 4.0 )
    p2 = ( (sin(phase*1.770)+1.0) * 7.5, (sin(phase*2.865)+1.0) * 4.0 )

    for row in range(9):
        row_f = float(row)

        for col in range(13):
            col_f = float(col)

            # Calculate the distance between this LED, and p1.
            dist1 = ( col_f - p1[0], row_f - p1[1] ) # The vector from p1 to this LED.
            distance = dist1[0]*dist1[0] + dist1[1]*dist1[1]

            # Calculate the distance between this LED, and p2.
            dist2 = ( col_f - p2[0], row_f - p2[1] ) # The vector from p2 to this LED.
            # Multiply this with the other distance, this will create weird plasma values :)
            distance *= dist2[0]*dist2[0] + dist2[1]*dist2[1]
            distance = sqrt(distance)

            # Warp the distance with a sin() function. As the distance value increases, the LEDs will get light,dark,light,dark,etc...
            # You can use a cos() for slightly different shading, or experiment with other functions. Go crazy!
            color_f = (sin( distance * colorStretch ) + 1.0) * 0.5 # range: 0.0...1.0

            # Square the color_f value to weight it towards 0. The image will be darker and have higher contrast.
            color_f *= color_f
            #color_f *= color_f*color_f*color_f # Uncomment this line to make it even darker :)
            
            # todo: color gradient
            r = g = b = int(color_f * 255)
            #r,g,b = mygradient(color_f)
            
            thirteen9_setpixel(row, col, r, g, b)

    thirteen9_sendbuf()
    #time.sleep_ms(1)
        
    