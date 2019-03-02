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

def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('Live-lot', 'live941003')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    for i in range(5):
      lightup(False)
      time.sleep(0.2)
do_connect()
gc.collect()









