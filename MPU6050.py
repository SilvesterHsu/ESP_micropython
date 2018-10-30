class MPU6050():
    def __init__(self, i2c, addr=0x68):
        self.iic = i2c
        self.addr = addr
        self.iic.start()
        self.iic.writeto(self.addr, bytearray([107, 0]))
        self.iic.stop()
32768
    def get_raw_values(self):
        self.iic.start()
        byte_read = self.iic.readfrom_mem(self.addr, 0x3B, 14)#(2byte*(3*2+1)sensors)
        self.iic.stop()
        return byte_read

    def bytes_toint(self, firstbyte, secondbyte):
        # The highest bit is the sign bit, and the complement is inverted +1
        if not firstbyte & 0x80:
            return firstbyte << 8 | secondbyte
        return - (((firstbyte ^ 255) << 8) | (secondbyte ^ 255) + 1)

    def get_values(self):
        raw_ints = self.get_raw_values()
        vals = {}
        vals["AX"] = self.bytes_toint(raw_ints[0], raw_ints[1])
        vals["AY"] = self.bytes_toint(raw_ints[2], raw_ints[3])
        vals["AZ"] = self.bytes_toint(raw_ints[4], raw_ints[5])
        vals["Tp"] = self.bytes_toint(raw_ints[6], raw_ints[7]) / 340.00 + 36.53
        vals["GX"] = self.bytes_toint(raw_ints[8], raw_ints[9])
        vals["GY"] = self.bytes_toint(raw_ints[10], raw_ints[11])
        vals["GZ"] = self.bytes_toint(raw_ints[12], raw_ints[13])
        return vals  # returned in range of Int16
        # 2**(7+8)=32768, vals range from -32768 to 32767
