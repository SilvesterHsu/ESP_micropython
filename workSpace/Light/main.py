import BlynkLib,LocalTime,Light,network,machine,time

led = Light.light()

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
if wifi.status() != network.STAT_GOT_IP:
  machine.reset()
print('\nIP:', wifi.ifconfig()[0])

timer = LocalTime.Timer()
for i in range(3):
  try:
    print("Connecting to Blynk...")
    blynk = BlynkLib.Blynk('a480cf0b21c84f9b882409c347f2757d')
    break
  except:
    print("Retrying...")
  if i == 2:
    machine.reset()

@blynk.ON("connected")
def blynk_connected(ping):
  print('Blynk ready. Ping:', ping, 'ms')

@blynk.VIRTUAL_WRITE(4) #Pin 4
def v3_write_handler(value):
  print('Pin4: {}'.format(value[0]))
  led.set_light(4,value[0])

@blynk.VIRTUAL_WRITE(5) #Pin 5
def v3_write_handler(value):
  print('Pin5: {}'.format(value[0]))
  led.set_light(5,value[0])

@blynk.VIRTUAL_READ(1)
@blynk.VIRTUAL_READ(2)
@blynk.VIRTUAL_READ(3)
def my_read_handler():
    blynk.virtual_write(1, timer.gettime())
    blynk.virtual_write(2, led.cur['4'])
    blynk.virtual_write(3, led.cur['5'])

while True:
  try:
    blynk.run()
    my_read_handler()
  except OSError as e:
    print(e)
    machine.reset()
  except ValueError as e:
    print(e)
    machine.reset()
  time.sleep(0.1)
  gc.collect()
  machine.idle()


