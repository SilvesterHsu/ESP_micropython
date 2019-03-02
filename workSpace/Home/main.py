import BlynkLib,network,machine,time
import dht

def wifi_connect():
  WIFI_SSID = 'Live-lot'
  WIFI_PASS = 'live941003'
  print("Connecting to WiFi...")
  wifi = network.WLAN(network.STA_IF)
  wifi.active(True)
  wifi.connect(WIFI_SSID, WIFI_PASS)
  while not wifi.isconnected():
      pass
  print('IP:', wifi.ifconfig()[0])
  
wifi_connect()

def blynk_connect():
  print("Connecting to Blynk...")
  BLYNK_AUTH = '408ec879d04e4da7a548bea5745f43f5'
  blynk = BlynkLib.Blynk(BLYNK_AUTH)
  @blynk.ON("connected")
  def blynk_connected(ping):
      print('Blynk ready. Ping:', ping, 'ms')
  return blynk

blynk = blynk_connect() 
need_connect = False
d = dht.DHT11(machine.Pin(5))

@blynk.VIRTUAL_WRITE(1)
def v3_write_handler(value):
    print('Current slider value: {}'.format(value[0]))    
@blynk.VIRTUAL_READ(2)
@blynk.VIRTUAL_READ(3)
@blynk.VIRTUAL_READ(4)
def my_read_handler():
    # this widget will show some time in seconds..
    d.measure()
    temp = d.temperature() # eg. 23
    humi = d.humidity()    # eg. 41
    timer = int(time.time())
    #print("Timer: {}, Temperature: {}, Humidity: {}".format(timer,temp,humi))
    blynk.virtual_write(2, timer)
    blynk.virtual_write(3, temp)
    blynk.virtual_write(4, humi)

while True:
    try:
      if need_connect == True:
        wifi_connect()
        blynk = blynk_connect()
        need_connect = False
      blynk.run()
      my_read_handler()
    except OSError:
      print("OSError: wifi timeout")
      need_connect = True
    except ValueError:
      print("ValueError: server timeout")
      need_connect = True
      time.sleep(25)
    machine.idle()

