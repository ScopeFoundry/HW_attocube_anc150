import serial
import time


class PhiIonGun(object):
    
    def __init__(self, port="COM7", address=3, debug = False):
        self.port = port
        self.debug = debug
        self.address = address
        
        if self.debug: print "Phi Ion Gun init, port=%s" % self.port
        
        self.ser = serial.Serial(port=self.port, baudrate=9600, timeout=0.2)
        
   
    def ask_cmd(self, cmd_id, data=None):
        '''
        serial command format, starts with '~ ' then "address" (03) for muliple devices on one com
        port, then internal ion gun electronics register number "cmd id" then data (if any)
        then hex checksum and 'CR' 
        All commands return status ('address' OK 00 ) and optional data plus checksum
        '''
        self.cmd_id = cmd_id
        msg = "~ %02X %02X " % (self.address, self.cmd_id)

        if data:
            msg += data + " "
    
        checksum = self.checksum_func(msg[1:])
        full_msg = msg + ("%02X\r" % checksum)
        
        if self.debug:
            print "ask_cmd write->", repr(full_msg)
    
        self.ser.write(full_msg)
        resp = self.my_readline()      
        if self.debug:
            print "ask_cmd resp->", repr(resp)
        
        
        #assert resp[0:8] == "%02X OK 00 " % self.address
        #assert self.checksum_func(resp[:-3]) == int(resp[-3:-1],16)
        
        return resp
    
    def close(self):
        self.ser.close()

    def my_readline(self):
        '''serial class does not handle CR end of line'''
        _input = ''
        line = ''
        while _input != '\r':
            _input = self.ser.read()
            if _input != '\r':
                line+= _input
        return line
        
    def parse_data(self, response):
        return response.split()[3]
        
    def checksum_func(self, data):
        checksum = 0x00
        for b in data:
            #print b
            checksum += ord(b)
            checksum = checksum & 0xFF
            #print "[%s] [%02X] [%02X]" %(b,ord(b), checksum)
            
        if self.debug: print "checksum", hex(checksum)
        return checksum
    
    
    def read_version(self):
        """ '~ 03 02 25.' ||| '03 OK 00 3.0.1(Apr 19 2011 @13:13:19) B5.'
        """
        result = self.ask_cmd(0x02, data=None)
        list = result.split()
        text = "Version "
        for str in list[3:-1]:
            text += str + ' '
        return text
    
    ''' hardware commands
        0x10    get condenser lens voltage
        0x11    write float voltage
        0x12    get float voltage
        0x13    write grid supply voltage
        0x15    write objective lens voltage
        0x16    get objective voltage
        0x17    write emission current
        0x18    get emission current
        0x19    get extractor pressure
        0x0A    write energy
        0x0B    write beam voltage
        0x0C    get energy
        0x0D    write bend voltage
        0x0F    get condenser voltage
        0x43    write x size
        0x44    write y size
        0x45    write x off
        0x46    write y off
        
        
    '''

    def read_condenser_v(self):
        resp = self.ask_cmd(0x10)
        value = self.parse_data(resp)
        if self.debug:
            print "condenser_v: ",value 
        return float(value)
    
    def read_emission_current(self): 
        resp = self.ask_cmd(0x18)
        value = self.parse_data(resp)
        if self.debug: print "current (mA):", resp
        return float(value)
    
    def read_energy(self):
        resp = self.ask_cmd(0x0C) 
        value = self.parse_data(resp)
        if self.debug: print "energy:", resp
        return float(value)
    
    def read_extractor_p(self):
        resp = self.ask_cmd(0x19)
        value = self.parse_data(resp)
        if self.debug: print "extractor pressure:", resp
        return float(value)
    
    def read_float(self):
        resp = self.ask_cmd(0x12)
        value = self.parse_data(resp)
        if self.debug: print "float_v", resp
        return float(value)
    
    def read_objective_v(self):
        resp = self.ask_cmd(0x16)
        value = self.parse_data(resp)
        if self.debug: print "objective_v:", resp
        return float(value)
    
    def write_energy(self, data):
        _float = ("%.3f" % data)
        _energy = self.ask_cmd(0x0A, _float)
        return _energy
    
    def write_beam_v(self, data):
        _float = ("%.3f" % data)
        beam_v = self.ask_cmd(0x0B, _float)
        return beam_v 

    def write_grid_v(self, data):
        _float = ("%.3f" % data)
        grid_v = self.ask_cmd(0x13, _float)
        return grid_v

    def write_condenser_v(self, data):
        _float = ("%.3f" % data)
        cond_v = self.ask_cmd(0x0F, _float)
        return cond_v

    def write_objective_v(self, data):
        _float = ("%.3f" % data)
        obj_v = self.ask_cmd(0x15, _float)
        return obj_v

    def write_bend_v(self, data):
        _float = ("%.3f" % float(-1*data))
        bend_v = self.ask_cmd(0x0D, _float)
        return bend_v
    
    def write_emission_current(self, data):
        #Note: This is the same function listed as "Current" in other program
        _float = ("%.3f" % data)
        emi_i = self.ask_cmd(0x17, _float)
        return emi_i

    def write_float_v(self, data):
        _float = ("%.3f" % float(-1*data))
        float_v = self.ask_cmd(0x11, _float)
        return float_v

    def xsize(self, data):
        _float = ("%.2f" % data)
        xmm = self.ask_cmd(0x43, _float)
        return xmm
    
    def ysize(self, data):
        _float = ("%.2f" % data)
        ymm = self.ask_cmd(0x44, _float)
        return ymm
    
    def xoff(self, data):
        _float = ("%.3f" % data)
        _xoff = self.ask_cmd(0x45, _float)
        return _xoff

    def yoff(self, data):
        _float = ("%.3f" % data)
        _yoff = self.ask_cmd(0x46, _float)
        return _yoff

##---------- Commonly found entities----------##
    def Header(self):
        _header = self.ask_cmd(0x39)
        if self.debug:
            print _header
        return _header
        
    def Footer(self):
        _header = self.ask_cmd(0x48)
        if self.debug:
            print _header
        return _header

    def Write_Confirmation(self):
        statement = self.ask_cmd(0x28)
        if self.debug:
            print statement
        return statement

    def Gun_Inactive(self):
        Gun_off = self.ask_cmd(0x36)
        if self.debug:
            print "Gun Inactive:", Gun_off
        return Gun_off

    def Gun_Active(self):
        Gun_on = self.ask_cmd(0x35)
        if self.debug:
            print "Gun active: ", Gun_on
        return Gun_on

    def Set_Internal_Raster_Mode(self):
        if self.debug:
            print "Set_Internal_Raster_Mode"
        _header = self.ask_cmd(0x33)
        if self.debug:
            print _header
        _data = self.ask_cmd(0x1E, "1")
        if self.debug:
            print _data
        _verify = self.ask_cmd(0x1F)
        if self.debug:
            print "Verify.", repr(_verify)
        _verify2 = self.ask_cmd(0x1F)
        if self.debug:
            print "Verify Again.", repr(_verify2)

        ## Test the following function on Portmon:

    def Set_External_Raster_Mode(self):
        _data = self.ask_cmd(0x1E, "0")
        if self.debug: 
            print _data
        return _data
        _verify = self.ask_cmd(0x1F)
        if self.debug:
            print "verify:", repr(_verify)
        return _verify
        _verify2 = self.ask_cmd(0x1F)
        if self.debug:
            print "verify 2:", repr(_verify2)
        return _verify2
        _footer = self.ask_cmd(0x34)
        if self.debug:
            print _footer
        return _footer
        self.Header()
        if self.debug:
            print "External Raster Set!"

    def State_Data_Packet(self, _beamv=0, _gridv=0, _condv=0, _objv=0, _bendv=0, _emiv=0, Blanking=False, Standby=False, Neutralize=False, Sputter=False, Gun_Firing_On=False):
        beamv = ("%.3f " % _beamv)
        gridv = ("%.3f " % _gridv)
        objv = ("%.3f " % _objv)
        if Standby==True:
            condv = ("%.3f " % _condv)
            bendv = ("%.3f " % -7)
            Gun_Firing_On=False
        elif Blanking == True:
            condv = ("%.3f " % 320)
            bendv = ("%.3f" % -35)
            Gun_Firing_On=False
        elif Neutralize==True:
            condv = ("%.3f " % _condv)
            bendv = ("%.3f " % float(-1*_bendv))
            Gun_Firing_On=True
        elif Sputter==True:
            condv = ("%.3f " % _condv)
            bendv = ("%.3f " % float(-1*_bendv))
            Gun_Firing_On=True
        else:
            condv = ("%.3f " % _condv)
            bendv = ("%.3f " % float(-1*_bendv))
        emiv = ("%.3f " % _emiv)
        state_address = ""
        if Gun_Firing_On==False:
            States = 0,0,0,0
            for i in States:
                state = ("%.3f" % i)
                state_address += state + " "
            if self.debug:
                print (state_address)
        else:
            States = 1,1,0,0
            for i in States:
                state = ("%.3f" % i)
                state_address += state + " "
            if self.debug:
                print (state_address)
        state_data = "1 " + beamv + gridv + condv + objv + bendv + "0.000 " + emiv + "51 1 " + state_address[:-1]
        #Note: The above function is not used to set the float voltage. Use specific command to write your float voltage.
        set_state = self.ask_cmd(0x1C, state_data)
        return set_state
        

    ## The following functions initialize writes to equipment, setting the conditions for which the functions are named.
    ## For example: If you wish to switch to blanking, enter the values you wish to set into the appropriately named function.
    ## In this case, the blanking function would be under "Off_standby_blanking" function, the only differences are the values
    ## within State_Data_Packet.

    def Startup_Commands(self):
        _model = self.ask_cmd(0x01)
        if self.debug:
            print(_model)
        _firmware = self.ask_cmd(0x02)
        if self.debug:
            print(_firmware)
        _initialize = self.ask_cmd(0x05)
        if self.debug:
            print(_initialize)
        self.Set_Internal_Raster_Mode()
        _unknown1 = self.ask_cmd(0x32)
        if self.debug:
            print(_unknown1)
        self.Header()
        _unknown2 = self.ask_cmd(0x3C, "1.000 1.000")
        if self.debug:
            print(_unknown2)
        self.Header()
        self.State_Data_Packet()
        self.Write_Confirmation()
        _unknown3 = self.ask_cmd(0x1A, "0")
        if self.debug:
            print(_unknown3)
        self.Footer()


    def Off_standby_blanking(self, _beamv=0, _gridv=0, _condv=0, _objv=0, _bendv=0, _emiv=0, Standby=False, Blanking=False): 
        self.beamv = float("%.3f" % _beamv)
        self.gridv = float("%.3f" % _gridv)
        self.condv = float("%.3f" % _condv)
        self.objv = float("%.3f" % _objv)
        self.bendv = float("%.3f" % _bendv)
        self.emiv = float("%.3f" % _emiv) 
        self.Header()
        if Standby==True:   
            self.State_Data_Packet(self.beamv, self.gridv, self.condv, self.objv, self.bendv, self.emiv, Standby=True) # Need non-zero value input method
        elif Blanking==True:
            self.State_Data_Packet(self.beamv, self.gridv, self.condv, self.objv, self.bendv, self.emiv, Blanking=True)
        else:
            self.State_Data_Packet()
        self.Write_Confirmation()
        self.Footer()
        self.Gun_Inactive()


    def Standby_to_neutralize(self, _beamv=0, _gridv=0, _condv=0, _objv=0, _bendv=0, _emiv=0): 
        self.beamv = float("%.3f" % _beamv)
        self.gridv = float("%.3f" % _gridv)
        self.condv = float("%.3f" % _condv)
        self.objv = float("%.3f" % _objv)
        self.bendv = float("%.3f" % _bendv)
        self.emiv = float("%.3f" % _emiv) 
        self.Gun_Active()
        self.Header()
        self.State_Data_Packet(self.beamv, self.gridv, self.condv, self.objv, self.bendv, self.emiv, Neutralize=True, Gun_Firing_On=True) # Need non-zero value input method, Gun_Firing_On=True
        self.Write_Confirmation()
        self.Footer()
        self.Set_Internal_Raster_Mode()
    
    def Neutralize_to_standby(self, _beamv=0, _gridv=0, _condv=0, _objv=0, _bendv=0, _emiv=0): 
        self.beamv = float("%.3f" % _beamv)
        self.gridv = float("%.3f" % _gridv)
        self.condv = float("%.3f" % _condv)
        self.objv = float("%.3f" % _objv)
        self.bendv = float("%.3f" % _bendv)
        self.emiv = float("%.3f" % _emiv) 
        self.Header()
        self.State_Data_Packet(self.beamv, self.gridv, self.condv, self.objv, self.bendv, self.emiv, Standby=True, Gun_Firing_On=False)
        self.Write_Confirmation()
        self.Footer()
        self.Gun_Inactive()
        
        
if __name__ == '__main__':
    phi = PhiIonGun(debug=False)
    #phi.ask_cmd(0x01)
    #phi.read_version()
    phi.Startup_Commands()
    #time.sleep(2)
    #phi.Off_standby_blanking(100, 150, 100, 71.8, 7, 25, Standby=True)
    #time.sleep(2)
    phi.Standby_to_neutralize(500, 150, 500, 359, 22.5, 25)
    #phi.read_condenser_v()
    print "Emission {:.1f} mA".format(phi.read_current())
    print "Beam {:.1f} V".format(phi.read_energy())
    print "Condenser {:.1f} V".format(phi.read_condenser_v())
    print "Objective {:.1f} V".format(phi.read_objective_v())
    print "Float {:.1f} V".format(phi.read_float())
    print phi.read_version()
    for i in range(10):
        time.sleep(0.1)
        print "Emission {:.2f} mA".format(phi.read_current())
    time.sleep(1)
    #phi.Neutralize_to_standby(100, 150, 100, 71.8, 7, 25)
    #time.sleep(1)
    #phi.Off_standby_blanking()
    #time.sleep(1)
    phi.Standby_to_neutralize(1000, 150, 660, 720, 0, 25)
    print "Beam On"
    time.sleep(1)
    print "Emission {:.1f} mA".format(phi.read_current())
    print "Beam {:.1f} V".format(phi.read_energy())
    print "Condenser {:.1f} V".format(phi.read_condenser_v())
    print "Objective {:.1f} V".format(phi.read_objective_v())
    print "Float {:.1f} V".format(phi.read_float())
    time.sleep(2)
    phi.Off_standby_blanking()
    time.sleep(0.5)
    print "Emission {:.1f} mA".format(phi.read_current())
    print "Beam {:.1f} V".format(phi.read_energy())
    print "Condenser {:.1f} V".format(phi.read_condenser_v())
    print "Objective {:.1f} V".format(phi.read_objective_v())
    print "Float {:.1f} V".format(phi.read_float())

    phi.close()
    