import serial

"""

Electrical standards are RS-232-C; connector pin usage is out- lined in Table 7-1. 
Characters consist of 1 start bit, 8 data bits (low order first with 8th bit always set to zero), and 1 stop bit.
There is no parity bit used. All characters will be printable ASCII characters. 
Control characters (0-1FH) are ignored except for car- riage return (0DH).

Table 7-1 External control connector serial pin connections
    Pin No.
    Name
    Use
    1
    CHASSIS GROUND
    Used to connect to the shield of the interconnect cable.
    2
    RECEIVE
    Serial interface data input. Standard RS-232-C signal levels.
    3
    TRANSMIT
    Serial interface data output. Standard RS-232-C signal levels.
    4
    REQUEST TO SEND
    RTS chain - RS-232-C input is buff- ered and connected to pin 21.
    5
    CLEAR TO SEND
    CTS buffered RS-232-C output of pin 25 input.
    6
    +11 VDC
    DATA SET READY is held on.
    7
    COMMON
    Signal common for all signals.
    8
    +11 VDC
    DATA CARRIER DETECT is held on.
    9
    +5 VDC
    Test Voltage.
    10
    -11 VDC
    Negative test voltage.
    14
    TRANSMIT CHAIN
    Serial data from next unit.
    16
    RECEIVE CHAIN
    Serial data to next unit.
    21
    RTS CHAIN
    RTS buffered RS-232-C output of pin 4 input.
    25
    CTS CHAIN
    CTS chain -RS-232-C input is buffered and connected to pin 5.

    NOTE: Only pins 2, 3, and 7 are required for serial interface to one controller.
    
"""
"""
Factory controller default settings are baud rate 9600 and unit ID #6.
"""

"""
The frame format for data transfers from the network controller is as follows:
    destination\acknowledgement\message source \length\message\checksum\[CR]
    
    * The destination is the 1-digit unit identification number of the instrument to receive the message.
    
    * Acknowledgment is one character to indicate the success of the previous transmission. 
        There are three possibilities: 
            (1) E means error, resend the message immediately (E is sent by the network controller only. 
                  Other units signify errors by not replying; causing the controller to resend the message). 
            (2) B means busy, resend message at next poll. 
            (3) R signifies previous message was received.
    
    * Message source is the unit ID of the unit that originated the message. 
        If there is no message, this location is a space (20H).
    
    * Length is the length of the message in 2 digit, hexadecimal format. 
        Maximum length is 256, with 256 being represented by a 00. 
        This field is eliminated if there are no messages.
    
    * Message field is the area where the actual information is located.
        The maximum length is 256 characters long.
    
    * Checksum is also a 2 digit hexadecimal number. 
        This number, when added to all the previous characters in the message 
        (excluding control characters), will result in a sum.
        If there are no errors, the result of modulo 256 division of this sum should be 0.
    
"""

def dasnet_convert(unitnum, msg):
    
    #destination\acknowledgement\message source \length\message\checksum\[CR]
    out = ""
    if unitnum is not None:
        out += str(unitnum)
    out += 'R'
    if msg == 'R':
        out += " \x00" # the null character seems wrong
    else:
        out += "%3.3X%s" % (len(msg), msg)
    
    sum_ = 0 
    for x in out:
        sum_ += ord(x)
    sum_ = (0x100-sum_) & 0xFF
    
    out += "%X" % sum_
    out += "\r"
    return out

def dasnet_validate(msg):
    sum_ = 0 
    for x in msg[:-3]:
        sum_ += ord(x)
    sum_ = (0x100-sum_) & 0xFF
    assert msg[-1] == '\r', "DASNET msg missing carriage return"
    assert msg[-3:-1] == "%X" % sum_, "DASNET checksum mismatch [%s]: %s != %X" % (repr(msg), repr(msg[-3:-1]), sum_)
    return msg

def dasnet_parse_response(msg):
    dasnet_validate(msg)
    assert msg[0] == 'R'
    msg_src = msg[1]
    if msg_src == ' ':
        return " "
    else:
        msg_src = int(msg_src)
    msg_len = int('0x'+msg[2:3])
    msg_field = msg[4:-3]
    assert len(msg_field) == msg_len
    return msg_field

def _dasnet_tests():
    dasnet_validate("R304STOPD1\r")
    try:
        dasnet_validate("R304STOPD2\r")
    except AssertionError as err:
        print err
    
    print repr(dasnet_convert(None, "R"))
    dasnet_validate(dasnet_convert(None, "R"))
    
    print repr(dasnet_convert(1, "R"))

    print repr(dasnet_convert(6, "R"))
    
    print repr(dasnet_convert(6, "IDENTIFY"))
    
    print repr(dasnet_convert(6, "REMOTE"))
    
    print repr(dasnet_convert(6, "CONST FLOW"))
    
    print repr(dasnet_convert(6, "FLOW=1.00"))
    
    print repr(dasnet_convert(6, "RUN"))
    
    print repr(dasnet_parse_response("R 8E\r"))
    
    #print repr(dasnet_parse_response("R027SERIES=1240-0221, Model 260D PUMP, REV FFB4\r"))


class TeledyneDSeriesSyringePump(object):
    
    def __init__(self, port, unitnum=6, baud=9600):
        self.port = port
        self.unitnum = int(unitnum)
        
        self.ser = serial.Serial(port=self.port, baud=baud, timeout=0.5)
    
    
    def ask(self, cmd):
        dasnet_cmd = dasnet_convert(self.unitnum, cmd)
        if self.debug: print "TdyneD ask:", repr(cmd), "-->", repr(dasnet_cmd)
        self.ser.write(dasnet_cmd)
        resp = self.ser.readline()
        resp = dasnet_validate(resp)
        

    def poll(self):
        return self.ask("R")

    def identify(self):
        self.ask("IDENTIFY")
        
    def read_analog_raw(self, num=1):
        assert num in (1,2,3,4,5,6)
        resp = self.ask("ALOG%i"%num)
        return int(resp)
    
    def read_analog_volt(self, num=1):
        raw = self.read_analog_raw(num)
        volts = (raw-7500.)/5000.
        return volts
    
    def read_pressure(self):
        resp = self.ask("PRESSA")
        return resp
    
    def read_get_all(self):
        resp = self.ask("G&")
        return resp
    
    def stop(self):
        resp = self.ask("STOP")
        return resp
    
if __name__ == '__main__':
    _dasnet_tests()
    
    for ii in range(16):
        #print hex(ii), 
        print dasnet_convert(None, "SERIES=1240-021, Model 260D PUMP, REV %X" % ii)
        if dasnet_convert(None, "SERIES=1240-0221, Model 260D PUMP, REV %02X" % ii)[-3:-1] == 'B4': print "="*20, ii