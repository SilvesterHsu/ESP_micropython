class OLED:
    '''
    x: abscissa
    y: ordinate
    c: brightness
    ------------------------------------------
    example:
    oled = OLED(your_i2c)
    # static
    oled.fill(0)
    oled.text("Hello World!")
    oled.show()
    # dynamic
    for i in range(100):
        oled.fill(0)
        oled.text("Hello World!")
        oled.show()
    '''
    def __init__(self,ic2):
        import ssd1306
        import framebuf
        self._screen = ssd1306.SSD1306_I2C(128, 64, ic2)
        self._buf = framebuf.FrameBuffer(bytearray(128 * 64//8), 128, 64, framebuf.MONO_HLSB)
        self._c = 1
    def text(self,message,x=0,y=0):
        self._buf.text(message, x, y)
    def fill(self,mode=0):
        self._buf.fill(mode)
    def rect(self,x=0,y=0,w=10,h=10):
        self._buf.rect(x,y,w,h,self._c)
    def fill_rect(self,x=0,y=0,w=10,h=10):
        self._buf.fill_rect(x,y,w,h,self._c)
    def show(self):
        self._screen.blit(self._buf, 0, 0)
        self._screen.show()
    def showWIFI(self,wifi):
        if wifi.net == True:
            self.text("Wifi:         OK",x=0,y=0)
            self.text(wifi.addr[0],x=0,y=10)
            if wifi.web == True:
                self.text("Web:          OK",x=0,y=20)
            else:
                self.text("Web:          NO",x=0,y=20)
        else:
            self.text("Wifi:         NO",x=0,y=0)
    def showVoltage(self,v):
        self.text("Voltage:    {:.3}v".format(v),x=0,y=40)
