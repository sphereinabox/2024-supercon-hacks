# import temp
# i2c0 = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
# i2c1 = I2C(1, sda=Pin(26), scl=Pin(27), freq=400_000)

from machine import I2C, Pin
import time
import random


from math import sin, sqrt, atan2, pi

# sao port details
#          (i2c, center x mm, center y mm, sin(rot), cos(rot))
# positive X is right
# positive Y is up
# positions in mm
SAOPORT1 = (i2c0,(-39.8092840669552,41.7447148391697,0.82884182856445,0.559482996365341))
SAOPORT2 = (i2c0,(-50.7804010062788,-1.56395523633945,0.990265908825569,-0.139188468695761))
SAOPORT3 = (i2c0,(-23.7828841671575,-35.6802290789135,0.484040578742604,-0.875045552031736))
SAOPORT4 = (i2c1,(27.2230848359365,-34.1291385356213,-0.469479092174177,-0.88294358937098))
SAOPORT5 = (i2c1,(50.7816051191583,1.56325486332061,-0.997540969165425,-0.070085767717167))
SAOPORT6 = (i2c1,(44.3366302098128,45.2315852576333,-0.71940146061741,0.694594513699567))
SAO_PORTS = (SAOPORT1,SAOPORT2,SAOPORT3,SAOPORT4,SAOPORT5,SAOPORT6)

petal_leds = None
thirteen9_leds = None
sixteen9_leds = None
dksao = None
from petalsao import PetalSao
from thirteen9sao import Thirteen9Sao
from sixteen9sao import Sixteen9Sao
from dksao import DkSao

def scan_init_petals():
    global petal_leds
    petal_leds = None
    global thirteen9_leds
    thirteen9_leds = None
    global sixteen9_leds
    sixteen9_leds = None
    global dksao
    dksao = None

    sao_port_scan()
    for i in range(6):
        sao_flags = sao_mapping[i]
        
        if sao_flags == 0x10:
            print("DK SAO Setup")
            global dksao
            dksao = DkSao(*SAO_PORTS[i])
            dksao.flip_off()
        if sao_flags == 0x180 or sao_flags == 0x100:
            # not sure why this is different sometimes
            print("Petal SAO Setup")
            petal_leds = PetalSao(*SAO_PORTS[i])
            petal_leds.init()
            petal_leds.flip_off()
        if sao_flags == 0x40:
            print("Sixteen9 SAO Setup")
            sixteen9_leds = Sixteen9Sao(*SAO_PORTS[i])
            sixteen9_leds.init()
            sixteen9_leds.flip_off()
        if sao_flags == 0x60:
            print("Thirteen9 SAO Setup")
            thirteen9_leds = Thirteen9Sao(*SAO_PORTS[i])
            thirteen9_leds.init()
            thirteen9_leds.flip_off()
        if sao_flags == 0x80:
            print("Hallowing M0 SAO Setup")
            # hallowing m0
            pass


scan_init_petals()

t = 0.0
def t_advance(elapsed_millis):
    global t
    t += 0.001 * elapsed_millis
def linear_wave_anim_x(x,y):
    return ((x+t*20)*.05) % 1.0
def linear_wave_anim_y(x,y):
    return ((y+t*20)*.05) % 1.0
def rotary_wave_anim(x,y):
    angle_radians = atan2(y,x)
    return (angle_radians/pi*2-t*pi/4) % 1.0
def concentric_wave_anim(x,y):
    return ((sqrt(x*x+y*y)+t*20)*.03) % 1.0    

phase = 0.0
phaseIncrement = 0.008
colorStretch = 1/1200.
p1 = p2 = (0.0,0.0)
def plasma_advance(elapsed_millis):
    global phase, phaseIncrement, p1, p2
    phase += phaseIncrement
    p1 = ( (sin(phase*1.000)+1.0) * 150, (sin(phase*1.310)+1.0) * 16 + 120)
    p2 = ( (sin(phase*1.770)+1.0) * 150, (sin(phase*2.865)+1.0) * 16 + 100)    
def plasma(x,y):
    # plasma
    # Calculate the distance between this LED, and p1.
    dist1 = ( x - p1[0], y - p1[1] ) # The vector from p1 to this LED.
    distance = dist1[0]*dist1[0] + dist1[1]*dist1[1]

    # Calculate the distance between this LED, and p2.
    dist2 = ( x - p2[0], y - p2[1] ) # The vector from p2 to this LED.
    # Multiply this with the other distance, this will create weird plasma values :)
    distance *= dist2[0]*dist2[0] + dist2[1]*dist2[1]
    distance = sqrt(distance)

    # Warp the distance with a sin() function. As the distance value increases, the LEDs will get light,dark,light,dark,etc...
    # You can use a cos() for slightly different shading, or experiment with other functions. Go crazy!
    intensity = (sin( distance * colorStretch ) + 1.0) * 0.5 # range: 0.0...1.0

    # Square the color_f value to weight it towards 0. The image will be darker and have higher contrast.
    #intensity *= intensity
    return intensity


# anim, anim_advance = linear_wave_anim_x, t_advance
anim, anim_advance = plasma, plasma_advance
# anim, anim_advance = rotary_wave_anim, t_advance
# anim, anim_advance = concentric_wave_anim, t_advance
anim_prev_ms = time.ticks_ms()
while True:
    try:
        if petal_leds: petal_leds.update_leds_by_func(anim) #6ms
        if thirteen9_leds: thirteen9_leds.update_leds_by_func(anim)#10ms
        if sixteen9_leds: sixteen9_leds.update_leds_by_func(anim)#12-13ms
        if dksao: dksao.update_leds_by_func(anim)

        if petal_leds: petal_leds.flip()#1ms
        if thirteen9_leds: thirteen9_leds.flip()#10ms
        if sixteen9_leds: sixteen9_leds.flip()#4ms
        if dksao: dksao.flip()
    except OSError as e:
        print("Exception During Animation!")
        print(e)
        print("Setting up SAOs Again")
        try:
            # re-scan
            scan_init_petals()
        except OSError as e:
            print("Exception Scanning/init SAOs!")
            print(e)
    
#     time_start = time.ticks_ms()
#     # test code goes here
#     dur_ms = time.ticks_ms() - time_start
#     print(dur_ms)

    ticks_ms = time.ticks_ms()
    anim_advance(ticks_ms - anim_prev_ms)
#     print("anim_dur_ms", (ticks_ms - anim_prev_ms))
    anim_prev_ms = ticks_ms
    # slow enough to update we don't need to sleep
    
    if not buttonA.value():
        # plasma
        anim, anim_advance = plasma, plasma_advance
    if not buttonB.value():
        # linear
        if anim == linear_wave_anim_x:
            anim, anim_advance = linear_wave_anim_y, t_advance
        else:
            anim, anim_advance = linear_wave_anim_x, t_advance
        # wait for button release
        while not buttonB.value(): time.sleep_ms(100)
    if not buttonC.value():
        if anim == concentric_wave_anim:
            # rotary wave
            anim, anim_advance = rotary_wave_anim, t_advance
        else:
            # concentric rings
            anim, anim_advance = concentric_wave_anim, t_advance
        # wait for button release
        while not buttonC.value(): time.sleep_ms(100)


#             petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
#         else:
#             petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x00]))


#     
#     phase = 0.0
#     phaseIncrement = 0.05
#     colorStretch = 1/130.
#     
#     cycle_period_ms = 1000
#     start_ms = time.ticks_ms()
#     rnd_prev = 0.0
#     frame_counter = 0
#     t_ms_prev = start_ms
#     while True:
# #        petal_bus.writeto_mem(PETAL_ADDRESS, 1, b_alloff)
#         t_ms = (time.ticks_ms() - start_ms) % cycle_period_ms
#         t = t_ms / cycle_period_ms
#         
#         phase += phaseIncrement
#         p1 = ( (sin(phase*1.000)+1.0) * 15, (sin(phase*1.310)+1.0) * 16 + 18)
#         p2 = ( (sin(phase*1.770)+1.0) * 15, (sin(phase*2.865)+1.0) * 16 + 30)
# 
#         for digit, mask, x, y in petal_leds:
#             # y-wave
#             #intensity = ((y+t*20) % 20) * .05
#             
#             # plasma
#             # Calculate the distance between this LED, and p1.
#             dist1 = ( x - p1[0], y - p1[1] ) # The vector from p1 to this LED.
#             distance = dist1[0]*dist1[0] + dist1[1]*dist1[1]
# 
#             # Calculate the distance between this LED, and p2.
#             dist2 = ( x - p2[0], y - p2[1] ) # The vector from p2 to this LED.
#             # Multiply this with the other distance, this will create weird plasma values :)
#             distance *= dist2[0]*dist2[0] + dist2[1]*dist2[1]
#             distance = sqrt(distance)
# 
#             # Warp the distance with a sin() function. As the distance value increases, the LEDs will get light,dark,light,dark,etc...
#             # You can use a cos() for slightly different shading, or experiment with other functions. Go crazy!
#             intensity = (sin( distance * colorStretch ) + 1.0) * 0.5 # range: 0.0...1.0
# 
#             # Square the color_f value to weight it towards 0. The image will be darker and have higher contrast.
#             intensity *= intensity            
#             
#             
#             ib = int((intensity * intensity) * 4)
#             hb = ib & 0x2
#             lb = ib & 0x1
# #             hb = 0.5 < intensity
# #             lb = (0.35 < intensity) and (intensity < 0.5) or (0.8 < intensity)
#             if lb: bl[digit] = bl[digit] | mask
#             else: bl[digit] = bl[digit] & ~mask
#             if hb: bh[digit] = bh[digit] | mask
#             else: bh[digit] = bh[digit] & ~mask
# #             print((lb,hb,intensity))
# #             break
#         petal_bus.writeto_mem(PETAL_ADDRESS, 1, bl)
#         time.sleep_us(800)
#         petal_bus.writeto_mem(PETAL_ADDRESS, 1, bh)
#         time.sleep_ms(5)
#         # print debug updates per time cycle
#         frame_counter += 1
#         if (t_ms < t_ms_prev):
#             #print(frame_counter)
#             frame_counter = 0
#         t_ms_prev = t_ms
# #         time.sleep_ms(1)
        

# while True:
# 
#     ## display button status on RGB
#     if petal_bus:
#         if not buttonA.value():
#             petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
#         else:
#             petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x00]))
# 
#         if not buttonB.value():
#             petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x80]))
#         else:
#             petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x00]))
# 
#         if not buttonC.value():
#             petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x80]))
#         else:
#             petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x00]))
# 
#     ## see what's going on with the touch wheel
#     if touchwheel_bus:
#         tw = touchwheel_read(touchwheel_bus)
# 
#     ## display touchwheel on petal
#     if petal_bus and touchwheel_bus:
#         if tw > 0:
#             tw = (128 - tw) % 256 
#             petal = int(tw/32) + 1
#         else: 
#             petal = 999
#         for i in range(1,9):
#             if i == petal:
#                 petal_bus.writeto_mem(0, i, bytes([0x7F]))
#             else:
#                 petal_bus.writeto_mem(0, i, bytes([0x00]))
# 
# 
#     
#     time.sleep_ms(20)
#     bootLED.off()






