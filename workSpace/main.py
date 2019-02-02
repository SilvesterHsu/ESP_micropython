_VERSION = "1.10"

import struct
import time

import machine
gettime = lambda: time.ticks_ms()

def dummy(*args):
    pass 

MSG_RSP = const(0)
MSG_LOGIN = const(2)
MSG_PING  = const(6)

MSG_TWEET = const(12)
MSG_EMAIL = const(13)
MSG_NOTIFY = const(14)
MSG_BRIDGE = const(15)
MSG_HW_SYNC = const(16)
MSG_INTERNAL = const(17)
MSG_PROPERTY = const(19)
MSG_HW = const(20)
MSG_EVENT_LOG = const(64)

MSG_REDIRECT  = const(41)
MSG_DBG_PRINT  = const(55)

STA_SUCCESS = const(200)
STA_INVALID_TOKEN = const(9)

DISCONNECTED = const(0)
CONNECTING = const(1)
CONNECTED = const(2)

def welcome():
    print("""
        ___  __          __
       / _ )/ /_ _____  / /__
      / _  / / // / _ \\/  '_/
     /____/_/\\_, /_//_/_/\\_\\
            /___/ for MicroPython v""" + _VERSION + "\n")

class BlynkProtocol:
    def __init__(self, auth, heartbeat=10, buffin=1024, log=None):
        self.callbacks = {}
        self.heartbeat = heartbeat*1000
        self.buffin = buffin
        self.log = log or dummy
        self.auth = auth
        self.state = DISCONNECTED
        self.connect()
        
    def sendMsg(self, cmd, *args, **kwargs):
        if "id" in kwargs:
            id = kwargs.id
        else:
            id = self.msg_id
            self.msg_id += 1
            if self.msg_id > 0xFFFF:
                self.msg_id = 1
                
        if cmd == MSG_RSP:
            data = b''
            dlen = args[0]
        else:
            data = ('\0'.join(map(str, args))).encode('ascii')
            dlen = len(data)
        
        self.log('<', cmd, id, '|', *args)
        msg = struct.pack("!BHH", cmd, id, dlen) + data
        self.lastSend = gettime()
        self._send(msg)
        
    def connect(self):
        if self.state != DISCONNECTED: return
        self.msg_id = 1
        (self.lastRecv, self.lastSend, self.lastPing) = (gettime(), 0, 0)
        self.bin = b""
        self.state = CONNECTING
        self.sendMsg(MSG_LOGIN, self.auth)
    def process(self, data=b''):
        if not (self.state == CONNECTING or self.state == CONNECTED): return
        now = gettime()
        if now - self.lastRecv > self.heartbeat+(self.heartbeat/2):
            return self.disconnect()
        if (now - self.lastPing > self.heartbeat/10 and
            (now - self.lastSend > self.heartbeat or
             now - self.lastRecv > self.heartbeat)):
            self.sendMsg(MSG_PING)
            self.lastPing = now
        
        if data != None and len(data):
            self.bin += data
        #return True

        while True:
            if len(self.bin) < 5: return
            
            cmd, i, dlen = struct.unpack("!BHH", self.bin[:5])
            if i == 0: return self.disconnect()
                      
            self.lastRecv = now
            if cmd == MSG_RSP:
                self.bin = self.bin[5:]

                self.log('>', cmd, i, '|', dlen)
                if self.state == CONNECTING and i == 1:
                    if dlen == STA_SUCCESS:
                        self.state = CONNECTED
                        dt = now - self.lastSend
                        self.sendMsg(MSG_INTERNAL, 'ver', _VERSION, 'h-beat', self.heartbeat//1000, 'buff-in', self.buffin, 'dev', 'python')
                        self.emit('connected', ping=dt)
                    else:
                        if dlen == STA_INVALID_TOKEN:
                            print("Invalid auth token")
                        return self.disconnect()
            else:
                if dlen >= self.buffin:
                    print("Cmd too big: ", dlen)
                    return self.disconnect()
            
                if len(self.bin) < 5+dlen: return
                
                data = self.bin[5:5+dlen]
                self.bin = self.bin[5+dlen:]

                args = list(map(lambda x: x.decode('ascii'), data.split(b'\0')))

                self.log('>', cmd, i, '|', ','.join(args))
                if cmd == MSG_PING:
                    self.sendMsg(MSG_RSP, STA_SUCCESS, id=i)
                elif cmd == MSG_HW or cmd == MSG_BRIDGE:
                    if args[0] == 'vw':
                        self.emit("V"+args[1], args[2:])
                    elif args[0] == 'vr':
                        self.emit("readV"+args[1])
                elif cmd == MSG_INTERNAL:
                    pass
                else:
                    print("Unexpected command: ", cmd)
                    return self.disconnect()


import socket
class Blynk(BlynkProtocol):
    def __init__(self, auth, **kwargs):
        welcome()
        BlynkProtocol.__init__(self, auth, **kwargs)
        
    def connect(self):
        try:
            self.conn = socket.socket()
            self.conn.connect(socket.getaddrinfo("www.seel.ink", 9442)[0][4])
            self.conn.settimeout(0.05)
            '''BlynkProtocol.connect(self)'''
        except:
            raise ValueError('connection with the Blynk servers failed')

    def _send(self, data):
        self.conn.send(data)

    def run(self):
        data = b''
        try:
            data = self.conn.recv(self.buffin)
        except KeyboardInterrupt:
            raise
        except:
            pass
        self.process(data)

# Test
BLYNK_AUTH = '408ec879d04e4da7a548bea5745f43f5'
blynk = Blynk(BLYNK_AUTH)
blynk.run()
