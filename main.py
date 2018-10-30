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
    oled.showWIFI(wifi)
    oled.show()
'''
# Test Voltage   
i2c_vol = I2C(-1,scl=Pin(12),sda=Pin(14),freq = 115200)
Voltage(i2c_vol,oled)
'''

def Gyro(i2c,oled,t=50):
    from MPU6050 import MPU6050
    accelerometer = MPU6050(i2c)
    data_org = accelerometer.get_values()
    x,y = 128//2,64//2
    h,w = 10,20
    sensitivity=60
    for i in range(t):
        data = accelerometer.get_values()
        y_a,x_a = data['AcX']-data_org['AcX'],data['AcY']-data_org['AcY']
        x,y = x-x_a/32767*sensitivity,y-y_a/32767*sensitivity
        x,y = int(min(max(x,0),128-w)),int(min(max(y,0),64-h))
        oled.fill(0)
        oled.rect(x,y,w,h)
        oled.show()
'''
# Test Gyro         
i2c_gyro = I2C(scl=Pin(12), sda=Pin(14))
Gyro(i2c_gyro,oled)
'''
