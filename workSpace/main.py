import time
from machine import Pin,PWM
time.sleep(2)
print("Hello")
with open('light.txt', 'r') as f:
    print(f.read())

def set_light(pin=4,aim=20,now=50):
  for i in range(int(abs(aim-now)*10)):
    pt = now + i/10 if aim>now else now-i/10
    PWM(Pin(pin), freq=1000, duty=int(1023*(pt)/100))
    time.sleep(0.002)

PWM(Pin(4), freq=1000, duty=int(1023*(100)/100))
time.sleep(3)
set_light(4,0,100)
set_light(4,100,0)
