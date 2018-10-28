import gc
from machine import I2C, Pin

def LED(t = 0.05,epoch = 10):
    from machine import Pin
    import time
    led=Pin(2,Pin.OUT)
    for i in range(epoch):
        led.on()
        time.sleep(t)
        led.off()
        time.sleep(t)

class WIFI:
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
        time.sleep(1)
        self.net = True if self._wlan.isconnected() == True else False
        self._address()
    def initialWeb(self):
        if self.net == True:
            import webrepl
            webrepl.start()
            self.web = True
        else:
            self.web = False

class OLED:
    def __init__(self,ic2):
        import ssd1306
        import framebuf
        self._screen = ssd1306.SSD1306_I2C(128, 64, ic2)
        self._buf = framebuf.FrameBuffer(bytearray(128 * 64//8), 128, 64, framebuf.MONO_HLSB)
    def text(self,message,x=0,y=0):
        self._buf.text(message, x, y)
    def fill(self,mode=0):
        self._buf.fill(mode)
    def show(self):
        self._screen.blit(self._buf, 0, 0)
        self._screen.show()
    def WIFI(self,wifi):
        if wifi.net == True:
            self.text("Wifi:         OK",x=0,y=0)
            self.text(wifi.addr[0],x=0,y=10)
            if wifi.web == True:
                self.text("Web:          OK",x=0,y=20)
            else:
                self.text("Web:          NO",x=0,y=20)
        else:
            self.text("Wifi:         NO",x=0,y=0)
    def Voltage(self,v):
        self.text("Voltage:    {:.3}v".format(v),x=0,y=40)

LED(0.05,5)

wifi = WIFI()
wifi.connect()
wifi.initialWeb()

i2c_oled = I2C(-1, scl=Pin(4), sda=Pin(5),freq=115200)
oled = OLED(i2c_oled)
oled.fill()
oled.WIFI(wifi)
oled.show()

gc.collect()