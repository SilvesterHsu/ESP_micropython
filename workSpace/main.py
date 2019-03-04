import machine,time

def get_dht():
  import dht
  d = dht.DHT11(machine.Pin(5))
  d.measure()
  temp = d.temperature() # eg. 23
  humi = d.humidity()    # eg. 41
  return temp,humi

def get_ds18x20():
  import onewire
  ow = onewire.OneWire(machine.Pin(4))
  import time, ds18x20
  ds = ds18x20.DS18X20(ow)
  roms = ds.scan()
  ds.convert_temp()
  time.sleep_ms(750)
  temp = ds.read_temp(roms[-1])
  return temp
  
  
temp = get_ds18x20()
_,humi = get_dht()
print(temp,humi)
