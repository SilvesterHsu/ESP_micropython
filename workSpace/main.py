import BlynkLib,network,machine,time

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
  BLYNK_AUTH = 'a480cf0b21c84f9b882409c347f2757d'
  blynk = BlynkLib.Blynk(BLYNK_AUTH)
  @blynk.ON("connected")
  def blynk_connected(ping):
      print('Blynk ready. Ping:', ping, 'ms')
  return blynk
 
 
wifi = wifi_connect()
blynk = blynk_connect() 
server_reconnect = False

@blynk.VIRTUAL_WRITE(4)
def v3_write_handler(value):
    print('Current slider value: {}'.format(value[0]))    
@blynk.VIRTUAL_READ(7)
def my_read_handler():
    timer = int(time.time())
    blynk.virtual_write(7, timer)

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
    time.sleep(5)
    server_reconnect = True
  except ValueError:
    print("ValueError: server timeout")
    time.sleep(5)
    server_reconnect = True
  machine.idle()





