from ntptime import settime
import utime,machine

class Timer:
  def __init__(self,try_time=3):
    print("Getting time from network...")
    self.try_time = try_time
    reset = 0
    while True:
      try:
        print("Setting time...")
        settime()
        break
      except:
        print("Retrying...")
        reset+=1
      if reset > self.try_time:
        machine.reset()

  def gettime(self):
    timer = self._gettime()
    return timer

  def _gettime(self):
    ctime = lambda t: "0"+str(t) if t < 10 else str(t)
    now=utime.time()+28800
    (year, month, mday, hour, minute, second, weekday, yearday)=utime.localtime(now)
    timer = list(map(ctime,[month, mday, hour, minute, second]))
    timer = "Time:   {}-{}  {}:{}:{}".format(*timer)
    return timer





