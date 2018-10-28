import gc

def initialWeb():
    import webrepl
    webrepl.start()

def connectWIFI():
    import network
    import time
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('Live-A-C', 'live941003')
    time.sleep(1)
    if wlan.isconnected() == True:
        ip_address = wlan.ifconfig()[0]
        initialWeb()
        return ip_address
    else:
        return False

class OLED:
    def __init__(self):
        from machine import I2C,Pin
        import ssd1306
        i2c = I2C(-1,Pin(4),Pin(5))
        self.display = ssd1306.SSD1306_I2C(128,64,i2c)
    def show(self,message,x=0,y=0,fill=False):
        if fill == True:
            self.display.fill(0)
        self.display.text(message,x,y)
        self.display.show()

def LED(t = 0.05,epoch = 10):
    from machine import Pin
    import time
    led=Pin(2,Pin.OUT)
    for i in range(epoch):
        led.on()
        time.sleep(t)
        led.off()
        time.sleep(t)

def printWIFI(ip_address,screen):
    if ip_address == False:
        screen.show("Wifi:         No",fill=True)
    else:
        screen.show("Wifi:         OK",fill=True)
        screen.show(ip_address,x=0,y=10)

LED(0.05,10)
ip_address = connectWIFI()
screen = OLED()
printWIFI(ip_address,screen)

gc.collect()
