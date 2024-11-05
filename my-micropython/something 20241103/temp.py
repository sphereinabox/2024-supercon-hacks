# try to find which SAO is on which port

from machine import I2C, Pin
import time # sleep_ms

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


I2C0_SDA = Pin(0)
I2C0_SCL = Pin(1)
I2C1_SDA = Pin(26)
I2C1_SCL = Pin(27)

SAO_DERPS = (
    (0, I2C0_SDA, I2C0_SCL, gpio11, gpio12),
    (0, I2C0_SDA, I2C0_SCL, gpio21, gpio22),
    (0, I2C0_SDA, I2C0_SCL, gpio31, gpio32),
    (1, I2C1_SDA, I2C1_SCL, gpio41, gpio42),
    (1, I2C1_SDA, I2C1_SCL, gpio51, gpio52),
    (1, I2C1_SDA, I2C1_SCL, gpio61, gpio62))

DO_I2C_CHECKS = False

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
        
    time.sleep_ms(10)

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
        time.sleep_ms(1)

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
        time.sleep_ms(1)
        
        if (0 == p1_before and 0 == p2_before and
            1 == p1.value() and 1 == p2.value()):
                sao_mapping[i] |= SAO_JUMPER_P1_P2
        
        if DO_I2C_CHECKS:
            # check for SDA->P1 or P2 jumper
            p1.init(Pin.IN, Pin.PULL_DOWN)
            p2.init(Pin.IN, Pin.PULL_DOWN)
            sda.value(1)
            scl.value(0)
            time.sleep_ms(1)
            
            if 0 == p1_before and 1 == p1.value():
                sao_mapping[i] |= SAO_JUMPER_SDA_P1
            if 0 == p2_before and 1 == p2.value():
                sao_mapping[i] |= SAO_JUMPER_SDA_P2
                
             # check for SDA->P1 or P2 jumper
            p1.init(Pin.IN, Pin.PULL_DOWN)
            p2.init(Pin.IN, Pin.PULL_DOWN)
            sda.value(0)
            scl.value(1)
            time.sleep_ms(1)
            
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
        time.sleep_ms(1)
        
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
    for i in range(9):
        I2C0_SCL.value(0)
        I2C1_SCL.value(0)
        time.sleep_us(10)
        I2C0_SCL.value(1)
        I2C1_SCL.value(0)
        time.sleep_us(10)

    time.sleep_ms(1)

    # reconfigure pins for i2c
    I2C0_SDA.init(Pin.ALT_I2C, Pin.PULL_UP)
    I2C0_SCL.init(Pin.ALT_I2C, Pin.PULL_UP)
    I2C1_SDA.init(Pin.ALT_I2C, Pin.PULL_UP)
    I2C1_SCL.init(Pin.ALT_I2C, Pin.PULL_UP)

sao_port_scan()
print([(n+1, hex(val)) for n,val in enumerate(sao_mapping)])



