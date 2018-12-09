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
        y_a,x_a = data['AX']-data_org['AX'],data['AY']-data_org['AY']
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

led=Pin(2,Pin.OUT)
if wifi._wlan.isconnected():
     led.off()
else:
     led.on()

import pblynk 
import time,machine,ds18x20,dht
import onewire

def EnvData(pin_ds=14,pin_dht=12):
     ow = onewire.OneWire(machine.Pin(14)) 
     ds = ds18x20.DS18X20(ow)
     roms = ds.scan()
     ds.convert_temp()
     time.sleep_ms(750)
     for rom in roms:
         ds_tem = ds.read_temp(rom)
     d = dht.DHT11(machine.Pin(12))
     d.measure()
     dht_tem=d.temperature() # eg. 23 (°C)
     dht_hum=d.humidity()    # eg. 41 (% RH)
     return ds_tem,dht_tem,dht_hum

token = '408ec879d04e4da7a548bea5745f43f5'
#token = '79f074cc53034ca48f9ccda3d1273546'
server = '185.186.146.243'
port = 9442
b = pblynk.Blynk(token, server, port, True)
b.add_virtual_pin(0)
b.add_virtual_pin(1)

def checknet():
     led=Pin(2,Pin.OUT)
     if wifi._wlan.isconnected():
          led.off()
     else:
          led.on()
          
def Tfunc(st):
    # write to (terminal style) rlogger at APP on vp 21  
    ds_tem,dht_tem,dht_hum = EnvData()
    b.virtual_write(0, ds_tem)
    b.virtual_write(1, dht_hum)
    
b.Ticker(Tfunc,200) # 1 secs

b.run()

