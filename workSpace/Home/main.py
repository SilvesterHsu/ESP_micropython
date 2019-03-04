import BlynkLib,network,machine,time
import dht

def wifi_connect():
  WIFI_SSID = 'Live-lot'
  WIFI_PASS = 'live941003'
  AP = network.WLAN(network.AP_IF)
  AP.active(False)
  wifi = network.WLAN(network.STA_IF)
  wifi.active(True)
  wifi.connect(WIFI_SSID, WIFI_PASS)
  print("Connecting to WiFi...",end="")
  while wifi.status() == network.STAT_CONNECTING:
    print(".",end="")
    time.sleep(0.2)
  print('\nIP:', wifi.ifconfig()[0])
  return wifi

def blynk_connect():
  print("Connecting to Blynk...")
  BLYNK_AUTH = '408ec879d04e4da7a548bea5745f43f5'
  blynk = BlynkLib.Blynk(BLYNK_AUTH)
  @blynk.ON("connected")
  def blynk_connected(ping):
      print('Blynk ready. Ping:', ping, 'ms')
  return blynk
  
wifi = wifi_connect()
blynk = blynk_connect() 
server_reconnect = False
d = dht.DHT11(machine.Pin(5))

@blynk.VIRTUAL_WRITE(1)
def v3_write_handler(value):
    print('Current slider value: {}'.format(value[0]))    
@blynk.VIRTUAL_READ(2)
@blynk.VIRTUAL_READ(3)
@blynk.VIRTUAL_READ(4)
def my_read_handler():
    d.measure()
    temp = d.temperature() # eg. 23
    humi = d.humidity()    # eg. 41
    timer = int(time.time())
    blynk.virtual_write(2, timer)
    blynk.virtual_write(3, temp)
    blynk.virtual_write(4, humi)

while True:
  try:
    while wifi.status() != network.STAT_GOT_IP:
      wifi.disconnect()
      wifi = wifi_connect()
    if server_reconnect == True:
      blynk = blynk_connect()
      server_reconnect = False
    blynk.run()
    my_read_handler()
  except OSError:
    print("OSError: wifi timeout")
    server_reconnect = True
  except ValueError:
    print("ValueError: server timeout")
    server_reconnect = True
  machine.idle()


