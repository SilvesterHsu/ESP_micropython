def Voltage(i2c,oled,t=50):
    from PCF8591 import PCF8591
    address = i2c.scan()
    if len(address)==0:
        return
    v={}
    for i in range(t):
        oled.fill(0)
        for i in range(4):
            v[i]= str(PCF8591(i2c,address[0]).read(inc=True)[i])
            oled.text("Voltage_{:}:  {:.3}v".format(i,v[i]),x=0,y=i*10)
        oled.show()
    oled.fill()
    oled.WIFI(wifi)
    oled.show()
    
# Test Voltage   
#i2c_vol = I2C(-1,scl=Pin(12),sda=Pin(14),freq = 115200)
#Voltage(i2c_vol,oled)