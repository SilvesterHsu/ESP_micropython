class PCF8591:
    def __init__(self,i2c,addr):
        self.i2c = i2c
        self.addr = addr
        self.control_byte={'zero':0b00000000,
              'out_flag':0b01000000,
              'pro0':0b00000000,
              'pro1':0b00010000,
              'pro2':0b00100000,
              'pro3':0b00110000,
              'incr':0b00000100,
              'chn0':0b00000000,
              'chn1':0b00000001,
              'chn2':0b00000010,
              'chn3':0b00000011
              }
        self._out = self._set_out_mode(False)
        self._pro = self._set_pro_mode(0)
        self._inc = self._set_inc_mode(False)
        self._chn = self._set_chn_mode(0)
        self._last_ctl = self._make_control_byte()
        
    def _make_control_byte(self):
        return  0 | self._out | self._pro | self._inc | self._chn
        
    def _set_out_mode(self,mode=False):
        self._out = self.control_byte['zero'] if mode == False else self.control_byte['out_flag']
        return self._out
        
    def _set_pro_mode(self,mode=0):
        self._pro = self.control_byte[['pro0','pro1','pro2','pro3'][mode]]
        return self._pro
        
    def _set_inc_mode(self,mode=False):
        self._inc = self.control_byte['zero'] if mode == False else self.control_byte['incr']
        return self._inc
        
    def _set_chn_mode(self,mode=0):
        self._chn = self.control_byte[['chn0','chn1','chn2','chn3'][mode]]
        return self._chn
        
    def _read(self,byte=1):
        return self.i2c.readfrom(self.addr, byte)
        
    def _write_control(self, control):
        if self._last_ctl != control:
            print('sent')
            self.i2c.writeto(self.addr, bytes([control]))
        self._read(1)
        return self._read(1) if self._inc == False else self._read(4)
    
    def read(self,chn = 0,pro = 0,inc = False):
        self._set_out_mode(False)
        self._set_pro_mode(pro)
        self._set_inc_mode(inc)
        self._set_chn_mode(chn)
        control = self._make_control_byte()
        if self._inc == False:
            return int(self._write_control(control)[0])*3.3/255
        else:
            return [self._write_control(control)[i]*3.3/255 for i in range(4)]
            
    def write(self, value):
        self._set_out_mode(True)
        self.i2c.writeto(self.addr, bytes([self._make_control_byte(), value]))