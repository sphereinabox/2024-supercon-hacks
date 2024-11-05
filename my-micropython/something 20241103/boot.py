## HAL / devices here

from machine import I2C, Pin
import time

PETAL_ADDRESS      = 0x00
TOUCHWHEEL_ADDRESS = 0x54

# Testing options
bootLED = Pin("LED", Pin.OUT)
bootLED.on()

## buttons
buttonA = Pin(8, Pin.IN, Pin.PULL_UP)
buttonB = Pin(9, Pin.IN, Pin.PULL_UP)
buttonC = Pin(28, Pin.IN, Pin.PULL_UP)

# I2C
I2C0_SDA = Pin(0)
I2C0_SCL = Pin(1)
I2C1_SDA = Pin(26)
I2C1_SCL = Pin(27)
## Initialize I2C peripherals
i2c0 = I2C(0, sda=I2C0_SDA, scl=I2C0_SCL, freq=400_000)
i2c1 = I2C(1, sda=I2C1_SDA, scl=I2C1_SCL, freq=400_000)

## GPIOs
gpio11 = Pin(7, Pin.IN, Pin.PULL_UP)
gpio12 = Pin(6, Pin.IN, Pin.PULL_UP)

gpio21 = Pin(5, Pin.IN, Pin.PULL_UP)
gpio22 = Pin(4, Pin.IN, Pin.PULL_UP)

gpio31 = Pin(3, Pin.IN, Pin.PULL_UP)
gpio32 = Pin(2, Pin.IN, Pin.PULL_UP)

gpio41 = Pin(22, Pin.IN, Pin.PULL_UP)
gpio42 = Pin(21, Pin.IN, Pin.PULL_UP)

gpio51 = Pin(20, Pin.IN, Pin.PULL_UP)
gpio52 = Pin(19, Pin.IN, Pin.PULL_UP)

gpio61 = Pin(18, Pin.IN, Pin.PULL_UP)
gpio62 = Pin(17, Pin.IN, Pin.PULL_UP)

GPIOs = [ [gpio11, gpio12], [gpio21, gpio22], [gpio31, gpio32], [gpio41, gpio42],  [gpio51, gpio52], [gpio61, gpio62] ]

SAO_DERPS = (
    (0, I2C0_SDA, I2C0_SCL, gpio11, gpio12),
    (0, I2C0_SDA, I2C0_SCL, gpio21, gpio22),
    (0, I2C0_SDA, I2C0_SCL, gpio31, gpio32),
    (1, I2C1_SDA, I2C1_SCL, gpio41, gpio42),
    (1, I2C1_SDA, I2C1_SCL, gpio51, gpio52),
    (1, I2C1_SDA, I2C1_SCL, gpio61, gpio62))

## GPIOs


def which_bus_has_device_id(i2c_id, debug=False):
    '''Returns a list of i2c bus objects that have the requested id on them.
    Note this can be of length 0, 1, or 2 depending on which I2C bus the id is found'''

    i2c0_bus = i2c0.scan() 
    if debug:
        print("Bus 0: ")
        print(str([hex(x) for x in i2c0_bus]))

    i2c1_bus = i2c1.scan()
    if debug:
        print("Bus 1: ")
        print(str([hex(x) for x in i2c1_bus]))

    busses = []
    if i2c_id in i2c0_bus:
        busses.append(i2c0)
    if i2c_id in i2c1_bus:
        busses.append(i2c1)

    return(busses)


def petal_init(bus):
    """configure the petal SAO"""
    bus.writeto_mem(PETAL_ADDRESS, 0x09, bytes([0x00]))  ## raw pixel mode (not 7-seg) 
    bus.writeto_mem(PETAL_ADDRESS, 0x0A, bytes([0x09]))  ## intensity (of 16) 
    bus.writeto_mem(PETAL_ADDRESS, 0x0B, bytes([0x07]))  ## enable all segments
    bus.writeto_mem(PETAL_ADDRESS, 0x0C, bytes([0x81]))  ## undo shutdown bits 
    bus.writeto_mem(PETAL_ADDRESS, 0x0D, bytes([0x00]))  ##  
    bus.writeto_mem(PETAL_ADDRESS, 0x0E, bytes([0x00]))  ## no crazy features (default?) 
    bus.writeto_mem(PETAL_ADDRESS, 0x0F, bytes([0x00]))  ## turn off display test mode 

# ## can't use scan logic for petal b/c it's at address 0
# ## so wrapping the init routine it try: blocks should also work
# ## later on can test if petal_bus is None
# petal_bus = None
# try:
#     petal_init(i2c0)
#     petal_bus = i2c0
# except: 
#     pass
# try:
#     petal_init(i2c1)
#     petal_bus = i2c1
# except:
#     pass
# if not petal_bus:
#     print(f"Warning: Petal not found.")
# 
# 
# ## waiting for wheel with a yellow light
# if petal_bus:
#     petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x80]))
#     petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))

## touchwheel last, with a wait loop,  b/c it doesn't init until animation is over
## probably need to implement a timeout here?
# touchwheel_bus = None
# touchwheel_counter = 0
# while not touchwheel_bus:
#     try:
#         touchwheel_bus =  which_bus_has_device_id(0x54)[0]
#     except:
#         pass
#     time.sleep_ms(100)
#     touchwheel_counter = touchwheel_counter + 1
#     if touchwheel_counter > 50:
#         break
# if not touchwheel_bus:
#     print(f"Warning: Touchwheel not found.")


def touchwheel_read(bus):
    """Returns 0 for no touch, 1-255 clockwise around the circle from the south"""
    return(touchwheel_bus.readfrom_mem(84, 0, 1)[0])

def touchwheel_rgb(bus, r, g, b):
    """RGB color on the central display.  Each 0-255"""
    touchwheel_bus.writeto_mem(84, 15, bytes([r]))
    touchwheel_bus.writeto_mem(84, 16, bytes([g]))
    touchwheel_bus.writeto_mem(84, 17, bytes([b]))

# 
# ## goes green if wheel configured
# if touchwheel_bus and petal_bus:
#     petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x00]))
# if petal_bus:
#     petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
#     time.sleep_ms(200)
#     petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x00]))


# whether to check for connections between i2c pins and SAO P1/P2 pins
DO_I2C_CHECKS = False

sao_mapping = [0] * 6
SAO_JUMPER_SDA_P1 = 0x0001
SAO_JUMPER_SDA_P2 = 0x0002
SAO_JUMPER_SCL_P1 = 0x0004
SAO_JUMPER_SCL_P2 = 0x0008
SAO_JUMPER_P1_P2  = 0x0010
SAO_P1_HIGH       = 0x0020
SAO_P2_HIGH       = 0x0040
SAO_P1_LOW        = 0x0080
SAO_P2_LOW        = 0x0100

def sao_port_scan():
    # scan SAOs by looking at their P1/P2 pin connections
    # result saved in sao_mapping

    # set IO pins as inputs, pullup
    for i, derp in enumerate(SAO_DERPS):
        i2c_num, sda, scl, p1, p2 = derp
        p1.init(Pin.IN, Pin.PULL_DOWN)
        p2.init(Pin.IN, Pin.PULL_DOWN)

    if DO_I2C_CHECKS:
        # i2c pins as outputs, low
        I2C0_SDA.init(Pin.OUT)
        I2C0_SCL.init(Pin.OUT)
        I2C1_SDA.init(Pin.OUT)
        I2C1_SCL.init(Pin.OUT)
        I2C0_SDA.value(0)
        I2C0_SCL.value(0)
        I2C1_SDA.value(0)
        I2C1_SCL.value(0)
        
    time.sleep_ms(2)

    # starting with p1,p1 pulled low...
    for i, derp in enumerate(SAO_DERPS):
        i2c_num, sda, scl, p1, p2 = derp
        
        # reset flags
        sao_mapping[i] = 0
            
        p1.init(Pin.IN, Pin.PULL_DOWN)    
        p2.init(Pin.IN, Pin.PULL_DOWN)

        if DO_I2C_CHECKS:
            sda.value(0)
            scl.value(0)
        time.sleep_ms(2)

        # with i2c pins low, check p1/p2 pins, both pulled-down by internal resistors
        p1_before = p1.value()
        p2_before = p2.value()
        
        if p1_before:
            sao_mapping[i] |= SAO_P1_HIGH
        if p2_before:
            sao_mapping[i] |= SAO_P2_HIGH
        
        # check for P1/P2 jumper
        p1.init(Pin.IN, Pin.PULL_UP)    
        p2.init(Pin.IN)
        if DO_I2C_CHECKS:
            sda.value(0)
            scl.value(0)
        time.sleep_ms(2)
        
        if (0 == p1_before and 0 == p2_before and
            1 == p1.value() and 1 == p2.value()):
                sao_mapping[i] |= SAO_JUMPER_P1_P2
        
        if DO_I2C_CHECKS:
            # check for SDA->P1 or P2 jumper
            p1.init(Pin.IN, Pin.PULL_DOWN)
            p2.init(Pin.IN, Pin.PULL_DOWN)
            sda.value(1)
            scl.value(0)
            time.sleep_ms(2)
            
            if 0 == p1_before and 1 == p1.value():
                sao_mapping[i] |= SAO_JUMPER_SDA_P1
            if 0 == p2_before and 1 == p2.value():
                sao_mapping[i] |= SAO_JUMPER_SDA_P2
                
             # check for SDA->P1 or P2 jumper
            p1.init(Pin.IN, Pin.PULL_DOWN)
            p2.init(Pin.IN, Pin.PULL_DOWN)
            sda.value(0)
            scl.value(1)
            time.sleep_ms(2)
            
            if 0 == p1_before and 1 == p1.value():
                sao_mapping[i] |= SAO_JUMPER_SCL_P1
            if 0 == p2_before and 1 == p2.value():
                sao_mapping[i] |= SAO_JUMPER_SCL_P2
            
        # reconfigure pins
        p1.init(Pin.IN, Pin.PULL_UP)
        p2.init(Pin.IN, Pin.PULL_UP)
        if DO_I2C_CHECKS:
            sda.value(1)
            scl.value(1)
        time.sleep_ms(2)
        
        # check for p1/p2 pulled to gnd
        if 0 == p1_before and 0 == p1.value():
            sao_mapping[i] |= SAO_P1_LOW
        if 0 == p2_before and 0 == p2.value():
            sao_mapping[i] |= SAO_P2_LOW
        
        # leave pin configuration pulled high?
        p1.init(Pin.IN, Pin.PULL_UP)
        p2.init(Pin.IN, Pin.PULL_UP)

    # TODO: clock out a bunch of clocks to i2c bus because I've been messing with it randomly
    I2C0_SDA.value(1)
    I2C0_SCL.value(1)
    I2C1_SDA.value(1)
    I2C1_SCL.value(1)
    for i in range(18):
        I2C0_SCL.value(0)
        I2C1_SCL.value(0)
        time.sleep_us(50)
        I2C0_SCL.value(1)
        I2C1_SCL.value(0)
        time.sleep_us(50)

    time.sleep_ms(2)
    
    # set i2c pins
    I2C0_SDA.init(Pin.IN, Pin.PULL_UP)
    I2C0_SCL.init(Pin.IN, Pin.PULL_UP)
    I2C1_SDA.init(Pin.IN, Pin.PULL_UP)
    I2C1_SCL.init(Pin.IN, Pin.PULL_UP)
    time.sleep_ms(2)
    
    i2c_fail = False
    if 0 == I2C0_SDA.value():
        print("I2C0_SDA IS LOW!!!!!")
        i2c_fail = True
    if 0 == I2C0_SCL.value():
        print("I2C0_SDA IS LOW!!!!!")
        i2c_fail = True
    if 0 == I2C1_SDA.value():
        print("I2C1_SDA IS LOW!!!!!")
        i2c_fail = True
    if 0 == I2C1_SCL.value():
        print("I2C1_SCL IS LOW!!!!!")
        i2c_fail = True
        
    if i2c_fail:
        while True:
            print("I2C Fail")
            bootLED.on()
            time.sleep_ms(500)
            bootLED.off()
            time.sleep_ms(500)

    # reconfigure pins for i2c
    I2C0_SDA.init(Pin.ALT_I2C, Pin.PULL_UP)
    I2C0_SCL.init(Pin.ALT_I2C, Pin.PULL_UP)
    I2C1_SDA.init(Pin.ALT_I2C, Pin.PULL_UP)
    I2C1_SCL.init(Pin.ALT_I2C, Pin.PULL_UP)
    # re-enable i2c:
    i2c0 = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
    i2c1 = I2C(1, sda=Pin(26), scl=Pin(27), freq=400_000)
    
    print("SAOs Found:")
    print([(n+1, hex(val)) for n,val in enumerate(sao_mapping)])


sao_port_scan()

