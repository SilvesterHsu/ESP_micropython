from machine import PWM,Pin
import json,time

class light():
  def __init__(self,lum = 50):
    # set Pin
    self.Pin = {'4':4,'5':5}
    # read from file
    try:
      self.cur = self._read()
    except:
      self.cur = {'4':lum,'5':lum}
      self._save()
    # open the light
    self._light_up()
    self.lum= {'4':self.cur['4'],'5':self.cur['5']}

  def _read(self):
    with open('light.txt', 'r') as f:
      js = f.read()
      rec = json.loads(js)
      return rec
  def _save(self):
    with open('light.txt', 'w') as f:
      js = json.dumps(self.cur)
      f.write(js)
  def _light_up(self):
    for i in self.Pin:
      PWM(Pin(self.Pin[i]), freq=800, duty=int(1023*(100-self.cur[i])/100))
  def _smooth(self,step=1,stime=0.005):
    tar = {'4':0,'5':0}
    for i in self.Pin:
      tar[i] = 1 if self.cur[i] < self.lum[i] else -1
    for i in range(100):
      if self.cur == self.lum:
        break
      for j in self.Pin:
        if self.cur[j] != self.lum[j]:
          self.cur[j] += tar[j]*step
      self._light_up()
      time.sleep(stime)
    self._save()
 
  def set_light(self,pin,rate):
    pin = pin if type(pin)==type('') else str(pin)
    rate = int(rate)
    self.lum[pin] = rate

    self._smooth()






