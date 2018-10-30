import gc
from machine import I2C, Pin
from OLED import OLED

def LED(t = 0.05,epoch = 10):
    '''
    t: hold time
    epoch: flash times
    '''
    from machine import Pin
    import time
    led=Pin(2,Pin.OUT)
    for i in range(epoch):
        led.on()
        time.sleep(t)
        led.off()
        time.sleep(t)

class WIFI:
    '''
    # open and connect wifi
    wifi = WIFI()
    wifi.connect('SSID','passwd')
    # open WebRepl
    wifi.initialWeb()
    '''
    def __init__(self):
        import network
        self._wlan = network.WLAN(network.STA_IF)
        self.net = False
        self.web = False
        self.addr = self._address()
    def _address(self):
        self.addr = self._wlan.ifconfig() if self.net == True else ()
        return self.addr
    def connect(self,SSID='Live-A-C',passwd='live941003'):
        import time
        self._wlan.active(True)
        self._wlan.connect(SSID,passwd)
        time.sleep(1.5)
        self.net = True if self._wlan.isconnected() == True else False
        self._address()
    def initialWeb(self):
        if self.net == True:
            import webrepl
            webrepl.start()
            self.web = True
        else:
            self.web = False

# boot signal
LED(0.05,5)
# turn on wifi module
wifi = WIFI()
wifi.connect()
wifi.initialWeb()
# turn on oled module
i2c_oled = I2C(-1, scl=Pin(4), sda=Pin(5),freq=115200)
oled = OLED(i2c_oled)
oled.fill()
oled.showWIFI(wifi)
oled.show()
# collect trash
gc.collect()
