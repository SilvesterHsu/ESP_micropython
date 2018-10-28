from machine import Pin,I2C
from PCF8591 import PCF8591
i2c = I2C(-1,scl=Pin(12),sda=Pin(14),freq = 115200)
address = i2c.scan()
if len(address)>0:
    screen.show('Voltage: {:.2}v'.format(
    PCF8591(i2c,address[0]).read(inc=True)[0]),x=0,y=30)