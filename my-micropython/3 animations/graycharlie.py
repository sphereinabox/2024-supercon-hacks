# is IS31FL3731
# https://www.adafruit.com/product/2946

# default addr 0x74
# can also be 0x75, 0x76 or 0x77
# currently on i2c0

# can output 16x9 grid of grayscale (8 bit) intensity
# has memory for 8 screens of data, recommends using them to get full-screen synchronized display update
# 400kHz max i2c frequency

charliebus = i2c0
charlieaddr = 0x74

def led_init():
    # set page to config bank
    charliebus.writeto_mem(charlieaddr, 0xFD, bytes([0x0B]))
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
    charliebus.writeto_mem(charlieaddr, 0x00, init_bytes)
    
    # reset pages:
    enable_bytes = bytes([0xFF]*18)
    intensity_buf = bytes([0x00]*144)
    for page in range(8):
        # set page
        charliebus.writeto_mem(charlieaddr, 0xFD, bytes([page]))
        # enable outputs
        charliebus.writeto_mem(charlieaddr, 0x00, enable_bytes)
        # set per-pixel intensity
        charliebus.writeto_mem(charlieaddr, 0x24, intensity_buf)
    # set page 0
    charliebus.writeto_mem(charlieaddr, 0xFD, bytes([0]))

def set_pixel_slow(page, address, val):
    # set page (0xFD is BANK_ADDRESSS)
    charliebus.writeto_mem(charlieaddr, 0xFD, bytes([page]))
    # 0x24 is COLOR_OFFSET
    charliebus.writeto_mem(charlieaddr, 0x24+address, bytes([val]))
    
led_init()

# test anim:
# for col in range(16):
#     for row in range(9):
#         addr = 16*row + col
#         set_pixel_slow(0, addr, 64)
#         time.sleep_ms(500)

# plasma

from math import sin, sqrt

# copied from LoLShield_Plasma example
phase = 0.0
phaseIncrement = 0.08
colorStretch = 0.11

display_buf = bytearray([0x00]*144)
def my_setpixel(col, row, color):
    pixel_addr = 16*row + col
    display_buf[pixel_addr] = color


nextfb = 0 # toggle between frames in chip 0/1 to present the entire display at once
while True:
    phase += phaseIncrement

    p1 = ( (sin(phase*1.000)+1.0) * 7.5, (sin(phase*1.310)+1.0) * 4.0 )
    p2 = ( (sin(phase*1.770)+1.0) * 7.5, (sin(phase*2.865)+1.0) * 4.0 )

    for row in range(9):
        row_f = float(row)

        for col in range(16):
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

            # Scale the color up to 0..7 . Max brightness is 7.
            #LedSign::Set( col, row, byte( round(color_f * 7.0) ) );
            #my_setpixel(col, row, int(color_f * 64))
            display_buf[16*row + col] = int(color_f * 64)

    # set page (0xFD is BANK_ADDRESSS)
    #charliebus.writeto_mem(charlieaddr, 0xFD, bytes([nextfb]))
    # write intensity values
    charliebus.writeto_mem(charlieaddr, 0x24, display_buf)
#     # switch to config page
#     charliebus.writeto_mem(charlieaddr, 0xFD, bytes([0x0B]))
#     # change displayed page
#     charliebus.writeto_mem(charlieaddr, 0x00, bytes([nextfb]))

    nextfb = (nextfb + 1) & 0b111
#     update_dur = time() - start_time
#     sleep_dur = 0.015 - update_dur
#     if sleep_dur < 0:
#         print('display update took ', update_dur)
#     else:
#         sleep(sleep_dur)
    #time.sleep_ms(1)
        

