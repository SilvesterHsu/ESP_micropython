import BlynkLib,network,machine,time,utime,json
from ntptime import settime
from machine import PWM,Pin

def set_light(pin=4,aim=50,now=0):
  for i in range(1,int(abs(aim-now)*2)+1):
    pt = now + i/2 if aim>now else now-i/2
    print(pt)
    PWM(Pin(pin), freq=1000, duty=int(1023*(100-pt)/100))
    time.sleep(0.005)
rec = {}
try:
  with open('light.txt', 'r') as f:
    js = f.read()
    rec = json.loads(js)
except:
  rec = {'4':50,'5':50}
set_light(4,rec['4'],0)
set_light(5,rec['5'],0)

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

def gettime():
  ctime = lambda t: "0"+str(t) if t < 10 else str(t)
  now=utime.time()+28800
  (year, month, mday, hour, minute, second, weekday, yearday)=utime.localtime(now)
  timer = list(map(ctime,[month, mday, hour, minute, second]))
  timer = "Time:   {}-{}  {}:{}:{}".format(*timer)
  return timer
res=0
while True:
  try:
    print("Getting time from network...")
    settime()
    print("Connecting to Blynk...")
    blynk = BlynkLib.Blynk('a480cf0b21c84f9b882409c347f2757d')
    break
  except:
    res += 1
    pass
  if res > 3:
    machine.reset()

@blynk.ON("connected")
def blynk_connected(ping):
  print('Blynk ready. Ping:', ping, 'ms')

@blynk.VIRTUAL_WRITE(4) #Pin 4
def v3_write_handler(value):
  print('Current slider value: {}'.format(value[0]))
  set_light(4,float(value[0]),rec['4'])
  rec['4'] = float(value[0])
  with open('light.txt', 'w') as f:
    js = json.dumps(rec)
    f.write(js)
@blynk.VIRTUAL_WRITE(5) #Pin 5
def v3_write_handler(value):
  print('Current slider value: {}'.format(value[0]))
  set_light(5,float(value[0]),rec['5'])
  rec['5'] = float(value[0])
  with open('light.txt', 'w') as f:
    js = json.dumps(rec)
    f.write(js)

@blynk.VIRTUAL_READ(1)
@blynk.VIRTUAL_READ(2)
@blynk.VIRTUAL_READ(3)
def my_read_handler():
    timer = gettime()
    blynk.virtual_write(1, timer)
    blynk.virtual_write(2, rec['4'])
    blynk.virtual_write(3, rec['5'])


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
  gc.collect()
  machine.idle()




