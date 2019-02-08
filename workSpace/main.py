import BlynkLib
import time
BLYNK_AUTH = '408ec879d04e4da7a548bea5745f43f5'
blynk = BlynkLib.Blynk(BLYNK_AUTH)
@blynk.VIRTUAL_READ(2)
def my_user_task():
    blynk.virtual_write(2, time.ticks_ms()//1000)
    print(gc.mem_free())
    gc.collect()
    print(gc.mem_free())
blynk.set_user_task(my_user_task, 1000)
blynk.run()

