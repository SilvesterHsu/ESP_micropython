import struct
import time
import socket

import machine
gettime = lambda: time.ticks_ms()

HDR_LEN = const(5)
HDR_FMT = "!BHH"

MAX_MSG_PER_SEC = const(20)

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

MSG_REDIRECT  = const(41)  # TODO: not implemented
MSG_DBG_PRINT  = const(55) # TODO: not implemented

STA_SUCCESS = const(200)

HB_PERIOD = const(10)
NON_BLK_SOCK = const(0)
MIN_SOCK_TO = const(1) # 1 second
MAX_SOCK_TO = const(5) # 5 seconds, must be < HB_PERIOD
RECONNECT_DELAY = const(1) # 1 second
TASK_PERIOD_RES = const(50) # 50 ms
IDLE_TIME_MS = const(5) # 5 ms

RE_TX_DELAY = const(2)
MAX_TX_RETRIES = const(3)

MAX_VIRTUAL_PINS = const(32)

DISCONNECTED = const(0)
CONNECTING = const(1)
AUTHENTICATING = const(2)
AUTHENTICATED = const(3)

EAGAIN = const(11)

LOGO = """
    ___  __          __
   / _ )/ /_ _____  / /__
  / _  / / // / _ \\/  '_/
 /____/_/\\_, /_//_/_/\\_\\
        /___/

  Give Blynk a Github star! => https://github.com/vshymanskyy/blynk-library-python
"""

class VrPin:
    def __init__(self, read=None, write=None):
        self.read = read
        self.write = write

class Blynk:
    def __init__(self, token, server='www.seel.ink', port=9442, connect=True, ssl=False):
        self._vr_pins = {}
        self._do_connect = False
        self._on_connect = None
        self._task = None
        self._task_period = 0
        self._token = token
        if isinstance (self._token, str):
            self._token = token.encode('ascii')
        self._server = server
        if port is None:
            if ssl:
                port = 8441
            else:
                port = 80
        self._port = port
        self._do_connect = connect
        self._ssl = ssl
        self.state = DISCONNECTED
        print(LOGO)

    def _format_msg(self, msg_type, *args):
        data = ('\0'.join(map(str, args))).encode('ascii')
        return struct.pack(HDR_FMT, msg_type, self._new_msg_id(), len(data)) + data

    def _handle_hw(self, data):
        params = list(map(lambda x: x.decode('ascii'), data.split(b'\0')))
        cmd = params.pop(0)
        if cmd == 'pm':
            pass
        elif cmd == 'dr' or cmd == 'dw' or cmd == 'ar' or cmd == 'aw':
            print("Warning: Digital/Analog pins not supported. Please use Virtual pins")
            pass
        elif cmd == 'vw':
            pin = int(params.pop(0))
            if pin in self._vr_pins and self._vr_pins[pin].write:
                for param in params:
                    self._vr_pins[pin].write(param)
            else:
                print("Warning: Virtual write to unregistered pin %d" % pin)
        elif cmd == 'vr':
            pin = int(params.pop(0))
            if pin in self._vr_pins and self._vr_pins[pin].read:
                self._vr_pins[pin].read()
            else:
                print("Warning: Virtual read from unregistered pin %d" % pin)
        else:
            raise ValueError("Unknown message cmd: %s" % cmd)

    def _new_msg_id(self):
        self._msg_id += 1
        if (self._msg_id > 0xFFFF):
            self._msg_id = 1
        return self._msg_id

    def _settimeout(self, timeout):
        if timeout != self._timeout:
            self._timeout = timeout
            self.conn.settimeout(timeout)

    def _recv(self, length, timeout=0):
        self._settimeout (timeout)
        try:
            self._rx_data += self.conn.recv(length)
        except socket.timeout:
            return b''
        except socket.error as e:
            if e.args[0] ==  EAGAIN:
                return b''
            else:
                raise
        if len(self._rx_data) >= length:
            data = self._rx_data[:length]
            self._rx_data = self._rx_data[length:]
            return data
        else:
            return b''

    def _send(self, data, send_anyway=False):
        if self._tx_count < MAX_MSG_PER_SEC or send_anyway:
            retries = 0
            while retries <= MAX_TX_RETRIES:
                try:
                    self.conn.send(data)
                    self._tx_count += 1
                    break
                except socket.error as er:
                    if er.args[0] != EAGAIN:
                        raise
                    else:
                        time.sleep_ms(RE_TX_DELAY)
                        retries += 1

    def _close(self, emsg=None):
        self.conn.close()
        self.state = DISCONNECTED
        time.sleep(RECONNECT_DELAY)
        if emsg:
            print('Error: %s, connection closed' % emsg)

    def _server_alive(self):
        c_time = int(time.time())
        if self._m_time != c_time:
            self._m_time = c_time
            self._tx_count = 0
            if self._last_hb_id != 0 and c_time - self._hb_time >= MAX_SOCK_TO:
                return False
            if c_time - self._hb_time >= HB_PERIOD and self.state == AUTHENTICATED:
                self._hb_time = c_time
                self._last_hb_id = self._new_msg_id()
                self._send(struct.pack(HDR_FMT, MSG_PING, self._last_hb_id, 0), True)
        return True

    def _run_task(self):
        if self._task:
            c_millis = time.ticks_ms()
            if c_millis - self._task_millis >= self._task_period:
                self._task_millis += self._task_period
                self._task()

    def virtual_write(self, pin, val):
        if self.state == AUTHENTICATED:
            self._send(self._format_msg(MSG_HW, 'vw', pin, val))

    def VIRTUAL_READ(blynk, pin):
        class Decorator():
            def __init__(self, func):
                self.func = func
                blynk._vr_pins[pin] = VrPin(func, None)
                #print(blynk, func, pin)
            def __call__(self):
                return self.func()
        return Decorator

    def VIRTUAL_WRITE(blynk, pin):
        class Decorator():
            def __init__(self, func):
                self.func = func
                blynk._vr_pins[pin] = VrPin(None, func)
            def __call__(self):
                return self.func()
        return Decorator

    def set_user_task(self, task, ms_period):
        if ms_period % TASK_PERIOD_RES != 0:
            raise ValueError('the user task period must be a multiple of %d ms' % TASK_PERIOD_RES)
        self._task = task
        self._task_period = ms_period

    def connect(self):
        self._do_connect = True

    def run(self):
        self._start_time = time.ticks_ms()
        self._task_millis = self._start_time
        self._hw_pins = {}
        self._rx_data = b''
        self._msg_id = 1
        self._timeout = None
        self._tx_count = 0
        self._m_time = 0
        self.state = DISCONNECTED

        while True:
            while self.state != AUTHENTICATED:
                self._run_task()
                if self._do_connect:
                    try:
                        self.state = CONNECTING
                        if self._ssl:
                            import ssl
                            print('SSL: Connecting to %s:%d' % (self._server, self._port))
                            ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_SEC)
                            self.conn = ssl.wrap_socket(ss, cert_reqs=ssl.CERT_REQUIRED, ca_certs='/flash/cert/ca.pem')
                        else:
                            print('TCP: Connecting to %s:%d' % (self._server, self._port))
                            self.conn = socket.socket()
                        self.conn.connect(socket.getaddrinfo(self._server, self._port)[0][4])
                    except:
                        self._close('connection with the Blynk servers failed')
                        continue
                    self.state = AUTHENTICATING
                    hdr = struct.pack(HDR_FMT, MSG_LOGIN, self._new_msg_id(), len(self._token))
                    print('Blynk connection successful, authenticating...')
                    self._send(hdr + self._token, True)
                    data = self._recv(HDR_LEN, timeout=MAX_SOCK_TO)
                    if not data:
                        self._close('Blynk authentication timed out')
                        continue

                    msg_type, msg_id, status = struct.unpack(HDR_FMT, data)
                    if status != STA_SUCCESS or msg_id == 0:
                        self._close('Blynk authentication failed')
                        continue

                    self.state = AUTHENTICATED
                    self._send(self._format_msg(MSG_INTERNAL, 'ver', '0.1.3', 'buff-in', 4096, 'h-beat', HB_PERIOD, 'dev', 'darwin'+'-py'))
                    print('Access granted, happy Blynking!')
                    if self._on_connect:
                        self._on_connect()
                else:
                    self._start_time = sleep_from_until(self._start_time, TASK_PERIOD_RES)

            self._hb_time = 0
            self._last_hb_id = 0
            self._tx_count = 0
            while self._do_connect:
                try:
                    data = self._recv(HDR_LEN, NON_BLK_SOCK)
                except:
                    pass
                if data:
                    msg_type, msg_id, msg_len = struct.unpack(HDR_FMT, data)
                    if msg_id == 0:
                        self._close('invalid msg id %d' % msg_id)
                        break
                    # TODO: check length
                    if msg_type == MSG_RSP:
                        if msg_id == self._last_hb_id:
                            self._last_hb_id = 0
                    elif msg_type == MSG_PING:
                        self._send(struct.pack(HDR_FMT, MSG_RSP, msg_id, STA_SUCCESS), True)
                    elif msg_type == MSG_HW or msg_type == MSG_BRIDGE:
                        data = self._recv(msg_len, MIN_SOCK_TO)
                        if data:
                            self._handle_hw(data)
                    elif msg_type == MSG_INTERNAL: # TODO: other message types?
                        break
                    else:
                        self._close('unknown message type %d' % msg_type)
                        break
                else:
                    self._start_time = sleep_from_until(self._start_time, IDLE_TIME_MS)
                if not self._server_alive():
                    self._close('Blynk server is offline')
                    break
                self._run_task()

            if not self._do_connect:
                self._close()
                print('Blynk disconnection requested by the user')

BLYNK_AUTH = '408ec879d04e4da7a548bea5745f43f5'
blynk = Blynk(BLYNK_AUTH)
@blynk.VIRTUAL_READ(2)
def my_user_task():
    blynk.virtual_write(2, time.ticks_ms()//1000)
    gc.collect()
blynk.set_user_task(my_user_task, 1000)
blynk.run()



