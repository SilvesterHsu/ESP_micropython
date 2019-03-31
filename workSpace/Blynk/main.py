import BlynkLib
import network
import machine

WIFI_SSID = 'Live-lot'
WIFI_PASS = 'live941003'

BLYNK_AUTH = 'a480cf0b21c84f9b882409c347f2757d'

print("Connecting to WiFi...")
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)
while not wifi.isconnected():
    pass

print('IP:', wifi.ifconfig()[0])

print("Connecting to Blynk...")
blynk = BlynkLib.Blynk(BLYNK_AUTH)

@blynk.ON("connected")
def blynk_connected(ping):
    print('Blynk ready. Ping:', ping, 'ms')

@blynk.VIRTUAL_READ(8)
def v2_read_handler():
    # This widget will show some time in seconds..
    blynk.virtual_write(8, time.ticks_ms() // 1000)

def runLoop():
    while True:
        blynk.run()
        machine.idle()

# Run blynk in the main thread:
runLoop()
