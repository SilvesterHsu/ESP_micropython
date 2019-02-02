import uos, gc, machine, time

def lightup(end=False):
  led=machine.Pin(2,machine.Pin.OUT)
  for j in range(8):
    led.off()
    time.sleep_ms(3)
    led.on()
    time.sleep_ms(30)
    if end == True:
      led.off()

class WIFI:
  def __init__(self,SSID,passwd):
    import network
    self._wlan = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(False)
    self.SSID = SSID
    self.passwd = passwd
  
  def connect(self):
    self._wlan.active(True)
    while not self._wlan.isconnected():
      self._wlan.connect(self.SSID,self.passwd)
      time.sleep(1)
    '''
    if web:
      import webrepl
      webrepl.start()'''
    for i in range(5):
      lightup(False)
      time.sleep(0.2)
        
wifi = WIFI('Live-A-C','live941003')
wifi.connect()
print(wifi._wlan.ifconfig())
gc.collect()




