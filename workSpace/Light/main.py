import BlynkLib,LocalTime,Light,network,machine,time
from BlynkTimer import BlynkTimer

def reboot():
  print('Rebooting')
  time.sleep(0.1)
  machine.reset()

def wifiConnect(WIFI_SSID='Live-lot',WIFI_PASS='live941003'):
  AP = network.WLAN(network.AP_IF)
  AP.active(False)
  wifi = network.WLAN(network.STA_IF)
  wifi.active(True)
  wifi.connect(WIFI_SSID, WIFI_PASS)
  print("Connecting to WiFi...",end="")
  while wifi.status() == network.STAT_CONNECTING:
    print(".",end="")
    time.sleep(0.2)
  if wifi.status() != network.STAT_GOT_IP:
    wifiConnect()
  print('\nIP:', wifi.ifconfig()[0])
  return wifi
  
def BlynkConnect():
  try:
    print("Connecting to Blynk...")
    blynk = BlynkLib.Blynk('a480cf0b21c84f9b882409c347f2757d')
    @blynk.ON("connected")
    def blynk_connected(ping):
      #blynk.sync_virtual(4,5)
      print('Blynk ready. Ping:', ping, 'ms')
  except:
    print("Retrying...")
    time.sleep(3)
    blynk = BlynkConnect()
  finally:
    return blynk
 
def BlynkInterface(blynk):
  @blynk.VIRTUAL_WRITE(4) #Pin 4
  def v3_write_handler(value):
    print('Pin4: {}'.format(value[0]))
    led.set_light(4,value[0])

  @blynk.VIRTUAL_WRITE(5) #Pin 5
  def v3_write_handler(value):
    print('Pin5: {}'.format(value[0]))
    led.set_light(5,value[0])
  
  @blynk.VIRTUAL_WRITE(6) #Pin 6  
  def v3_write_handler(value):
    reboot()


led = Light.light()
wifi = wifiConnect()
timer = LocalTime.Timer(5)
blynk = BlynkConnect()
BlynkInterface(blynk)
btimer = BlynkTimer()
server_reconnect = False

def reconnect():
  print("Reconnect")
  global server_reconnect
  server_reconnect = True

def checkWifi():
  global wifi
  while wifi.status() != network.STAT_GOT_IP:
      print("Reconnect wifi...")
      wifi.disconnect()
      wifi = wifiConnect()
  

@blynk.VIRTUAL_WRITE(8) #Pin 8 
def v3_write_handler(value):
  reconnect()

@blynk.VIRTUAL_READ(1)
@blynk.VIRTUAL_READ(2)
@blynk.VIRTUAL_READ(3)
def my_read_handler():
    blynk.virtual_write(1, timer.gettime())
    blynk.virtual_write(2, int(led.cur['4']*2.55))
    blynk.virtual_write(3, int(led.cur['5']*2.55))

btimer.set_interval(0.5, my_read_handler)
btimer.set_interval(1200, reboot)

server_reconnect = False
while True:
  try:
    checkWifi()
    if server_reconnect == True:
      checkWifi()
      print("Reconnect server...")
      blynk = BlynkConnect()
      BlynkInterface(blynk)
      server_reconnect = False
    blynk.run()
    btimer.run()
  except KeyboardInterrupt:
    raise
  except OSError or ValueError:
    print("Error")
    server_reconnect = True
    #machine.reset()
  gc.collect()
  machine.idle()






