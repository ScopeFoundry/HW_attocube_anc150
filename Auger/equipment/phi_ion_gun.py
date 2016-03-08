import serial
import time

class PhiIonGun(object):
    
    def __init__(self, port="COM7", address=3, debug = False):
        self.port = port
        self.debug = debug
        self.address = address
        
        if self.debug: print "Phi Ion Gun init, port=%s" % self.port
        
        self.ser = serial.Serial(port=self.port, baudrate=9600, timeout=1.0)
        self.ask_in_progress = False        
        self.initialize()
        

        
   
    def ask_cmd(self, cmd_id, data=None):
        '''
        serial command format, starts with '~ ' then "address" (03) for muliple devices on one com
        port, then internal ion gun electronics register number "cmd id" then data (if any)
        then hex checksum and 'CR' 
        All commands return status ('address' OK 00 ) and optional data plus checksum
        '''
        
        for i in range(10):
            if self.ask_in_progress:
                time.sleep(0.1)
            else:
                break
        if self.ask_in_progress:
            raise IOError("phi_ion_gun could not ask_cmd, ask_in_progres")
        
        try:
            self.ask_in_progress = True

            self.cmd_id = cmd_id
            msg = "~ %02X %02X " % (self.address, self.cmd_id)
    
            if data:
                msg += str(data) + " "
        
            checksum = self.checksum_func(msg[1:])
            full_msg = msg + ("%02X\r" % checksum)
            
            if self.debug:
                print "ask_cmd write->", repr(full_msg)
        
            self.ser.write(full_msg)
            resp = self.my_readline()      
            if self.debug:
                print "ask_cmd resp->", repr(resp)

        finally:
            self.ask_in_progress = False
        
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
        chunk = response.split()[3]
        return chunk
        if self.debug:
            print "Chunk:", chunk
             
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
        _list = result.split()
        text = "Version "
        for _str in _list[3:-1]:
            text += _str + ' '
        return text
    
    ''' hardware commands
    
        0x01    get model number
        0x02    get version number
        
        0x05    initialize controller electronics (required before read commands)
    
        0x10    get condenser lens voltage
        0x11    write float voltage
        0x12    get float voltage
        0x13    write grid supply voltage
        0x15    write objective lens voltage
        0x16    get objective voltage
        0x17    write emission current
        0x18    get emission current
        0x19    get extractor pressure
        0x0A    write beam_v            #this one (was previously called energy)
        0x0B    write beam voltage   #investigate this quantity in person
        0x0C    get beam_v                #and this one.
        0x0D    write bend voltage
        0x0F    get condenser voltage
        0x43    write x size
        0x44    write y size
        0x45    write x off
        0x46    write y off
        
        0x28    read status(after write 1C) '03 OK 00 1 1 1 1 1 1 0 F3'
        0x48    read status(after write comfirm) '03 OK 00 0 0 0 0 0 4D'
        
        0x32    write something (shows up in read 0x39) often set as 3
        0x39    read status (always before 1C commmand)
        
        0x36    write shutdown
                    ask_cmd write-> '~ 03 36 2C\r'
                    ask_cmd resp-> '03 OK 00 BD'
        
        0x33    write something (related to internal raster)
                ask_cmd write-> '~ 03 33 29\r'
                ask_cmd resp-> '03 OK 00 BD'

        0x34    write something (related to external raster)
                ask_cmd write-> '~ 03 33 29\r'
                ask_cmd resp-> '03 OK 00 BD'
                
    '''
    
    def initialize(self):
        if self.debug: 
            print "initialize"
        self.ask_cmd(0x01)
        self.ask_cmd(0x02)
        self.ask_cmd(0x05)
        self.ask_cmd(0x33)
        self.ask_cmd(0x1E, 1)
        self.ask_cmd(0x1F)
        self.ask_cmd(0x32, 3)
        self.ask_cmd(0x39)
        self.ask_cmd(0x3C, "1.000 1.000")
        self.ask_cmd(0x39)
        self.State_Data_Packet()
        

    def read_condenser_v(self):
        resp = self.ask_cmd(0x10)
        value = self.parse_data(resp)
        if self.debug:  print "read_condenser_v: ",value 
        return float(value)
    
    def read_emission_current(self): 
        resp = self.ask_cmd(0x18)
        value = self.parse_data(resp)
        if self.debug: print "current (mA):", resp
        return float(value)
    
    def read_beam_v(self):
        resp = self.ask_cmd(0x0C) 
        value = self.parse_data(resp)
        if self.debug: print "read_beam_v:", resp
        return float(value)
    
    def read_extractor_p(self):
        resp = self.ask_cmd(0x19)
        value = self.parse_data(resp)
        if self.debug: print "extractor pressure:", resp
        return float(value)
    
    def read_float(self):
        resp = self.ask_cmd(0x12)
        value = self.parse_data(resp)
        if self.debug: print "float_v:", resp
        return float(value)
    
    def read_objective_v(self):
        resp = self.ask_cmd(0x16)
        value = self.parse_data(resp)
        if self.debug: print "objective_v:", resp
        return float(value)
    


    def write_beam_v(self, data): #was previously write_energy
        _float = ("%.3f" % data)
        _beam_v = self.ask_cmd(0x0A, _float)
        if self.debug: print "write_beam_v"
        return _beam_v
    
    """def write_beam_v(self, data):
        _float = ("%.3f" % data)
        beam_v = self.ask_cmd(0x0B, _float)
        if self.debug:
            print "write_beam_v"
        return beam_v 
    """
    
    def write_grid_v(self, grid_v):
        assert 99 < grid_v < 201
        _float = ("%.3f" % grid_v)
        grid_v = self.ask_cmd(0x13, _float)
        if self.debug: print "write grid_v"
        return grid_v

    def write_condenser_v(self, data):
        _float = ("%.3f" % data)
        cond_v = self.ask_cmd(0x0F, _float)
        if self.debug: print "write_condenser_v"
        return cond_v

    def write_objective_v(self, data):
        _float = ("%.3f" % data)
        obj_v = self.ask_cmd(0x15, _float)
        if self.debug: print "write_objective_v"
        return obj_v

    def write_bend_v(self, data):
        _float = ("%.3f" % float(-1*data))
        bend_v = self.ask_cmd(0x0D, _float)
        if self.debug: print "write_bend_v"
        return bend_v
    
    def write_emission_current(self, data):
        #Note: This is the same function listed as "Current" in other program
        _float = ("%.3f" % data)
        emi_i = self.ask_cmd(0x17, _float)
        if self.debug: print "write_emission_current"
        return emi_i

    def write_float_v(self, data):
        _float = ("%.3f" % float(-1*data))
        float_v = self.ask_cmd(0x11, _float)
        if self.debug: print "write_float_v"
        return float_v

    def xsize(self, data):
        _float = ("%.2f" % data)
        xmm = self.ask_cmd(0x43, _float)
        if self.debug: print "set_xsize"
        return xmm
    
    def ysize(self, data):
        _float = ("%.2f" % data)
        ymm = self.ask_cmd(0x44, _float)
        if self.debug: print "set_ysize"
        return ymm
    
    def xoff(self, data):
        _float = ("%.3f" % data)
        _xoff = self.ask_cmd(0x45, _float)
        if self.debug: print "set_xoff"
        return _xoff

    def yoff(self, data):
        _float = ("%.3f" % data)
        _yoff = self.ask_cmd(0x46, _float)
        if self.debug: print "set_yoff"
        return _yoff

##---------- Commonly found entities----------##
    def Header(self):
        _header = self.ask_cmd(0x39)
        if self.debug:
            print "Header:", _header
        return _header
        
    def Footer(self):
        _footer = self.ask_cmd(0x48)
        if self.debug:
            print "Footer:", _footer
        return _footer

    def Write_Confirmation(self):
        statement = self.ask_cmd(0x28)
        if self.debug:
            print "Write confirm:", statement
        return statement

    def Gun_Inactive(self):
        Gun_off = self.ask_cmd(0x36)
        if self.debug:
            print "Gun Inactive:", Gun_off
        return Gun_off

    def Gun_Active(self):
        Gun_on = self.ask_cmd(0x35)
        if self.debug:
            print "Gun Active: ", Gun_on
        return Gun_on

    def Set_Raster_Mode(self, State='OFF'):
        assert State in ['OFF', 'INTERNAL', 'EXTERNAL']
        t = 0.2
        
        if State == 'INTERNAL':
            if self.debug:
                print "Set_Internal_Raster_Mode"
            _header = self.ask_cmd(0x33)
            time.sleep(t)
            if self.debug:
                print _header
            _data = self.ask_cmd(0x1E, "1")
            time.sleep(t)
            if self.debug:
                print _data
            _verify = self.ask_cmd(0x1F)
            time.sleep(t)
            if self.debug:
                print "Verify.", repr(_verify)
            _verify2 = self.ask_cmd(0x1F)
            time.sleep(t)
            if self.debug:
                print "Verify Again.", repr(_verify2)
            time.sleep(t)
        elif State == 'EXTERNAL':
            _data = self.ask_cmd(0x1E, "0")
            if self.debug: 
                print _data
            time.sleep(t)
            while self.parse_data(self.ask_cmd(0x1F)) != str(0):
                self.ask_cmd(0x1F)
            
            time.sleep(t)
            _footer = self.ask_cmd(0x34)
            if self.debug:
                print _footer
            time.sleep(t)
            self.Header() #0x39
            if self.debug:
                print "External Raster Set!"

##--edited below--##
    def State_Data_Packet(self, beamv=0, gridv=0, condv=0, objv=0, bendv=0, emiv=0, State='OFF'):
        assert State in ['OFF', 'BLANK', 'STANDBY', 'ACTIVE']
        if State == 'STANDBY':
            bendv = -7.0 
            Gun_Firing_On=False
        elif State == 'BLANK':
            condv = 320.0
            bendv = -35.0
            Gun_Firing_On=False
        elif State == 'ACTIVE':
            Gun_Firing_On=True
        elif State == 'OFF':
            beamv = 0.0
            gridv = 0.0
            objv  = 0.0             
            condv = 0.0
            bendv = 0.0
            emiv  = 0.0
            Gun_Firing_On=False
        if Gun_Firing_On==False:
            States = 0,0,0,0
        else:
            States = 1,1,0,0
        
        state_data = "1 {beamv:.3f} {gridv:.3f} {condv:.3f} {objv:.3f}".format(beamv=beamv, gridv=gridv, condv=condv, objv=objv)
        state_data += " {bendv:.3f} 0.000 {emiv:.3f} 51 1".format(bendv=bendv, emiv=emiv)
        state_data += " {:.3f} {:.3f} {:.3f} {:.3f}".format(*States)
        if self.debug:
            print(">>", state_data)
        #Note: The above function is not used to set the float voltage. Use specific command to write your float voltage.
        set_state = self.ask_cmd(0x1C, state_data)
        
        if self.debug:
            print(set_state)
        return set_state
        

    ## The following functions initialize writes to equipment, setting the conditions for which the functions are named.
    ## For example: If you wish to switch to blanking, enter the values you wish to set into the appropriately named function.
    ## In this case, the blanking function would be under "Off_standby_blanking" function, the only differences are the values
    ## within State_Data_Packet.

'''    def Startup_Commands(self):
        _model = self.ask_cmd(0x01)
        if self.debug:
            print(_model)
        _firmware = self.read_version()
        if self.debug:
            print(_firmware)
        _initialize = self.initialize()
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
'''

    
    
    
    #def Off_Standby_Blanking(self, beamv=0, gridv=0, condv=0, objv=0, bendv=0, emiv=0, State='OFF'):
    #    self.beamv = beamv
    #    self.gridv = gridv
    #    self.condv = condv
    #    self.objv = objv
    #    self.bendv = bendv
    #    self.emiv = emiv
    #    self.Header()
    #    if State=='STANDBY':   
    #        self.State_Data_Packet(self.beamv, self.gridv, self.condv, self.objv, self.bendv, self.emiv, State='STANDBY') # Need non-zero value input method
    #    elif State=='BLANK':
    #        self.State_Data_Packet(self.beamv, self.gridv, self.condv, self.objv, self.bendv, self.emiv, State='BLANK')
    #    else:
    #        self.State_Data_Packet(State='OFF')
    #    self.Write_Confirmation()
    #    self.Footer()
    #    self.Gun_Inactive()


    #def Active(self, beamv=0, gridv=0, condv=0, objv=0, bendv=0, emiv=0, State='ACTIVE'): 
    #    self.beamv = beamv
    #    self.gridv = gridv
    #    self.condv = condv
    #    self.objv = objv
    #    self.bendv = bendv
    #    self.emiv = emiv 
    #    self.Gun_Active()
    #    self.Header()
    #    self.State_Data_Packet(self.beamv, self.gridv, self.condv, self.objv, self.bendv, self.emiv, State='ACTIVE') # Need non-zero value input method, Gun_Firing_On=True
    #    self.Write_Confirmation()
    #    self.Footer()
    #    self.Set_Internal_Raster_Mode()
    

        
        
if __name__ == '__main__':
    phi = PhiIonGun(debug=False)
    #phi.ask_cmd(0x01)
    #phi.read_version()
    phi.initialize()

    #phi.read_condenser_v()
    #print "Emission {:.1f} mA".format(phi.read_current())
    #print "Beam {:.1f} V".format(phi.read_beam_v())
    #print "Condenser {:.1f} V".format(phi.read_condenser_v())
    #print "Objective {:.1f} V".format(phi.read_objective_v())
    #print "Float {:.1f} V".format(phi.read_float())
    #print phi.read_version()
    #for i in range(10):
    #    time.sleep(0.1)
    #    print "Emission {:.2f} mA".format(phi.read_current())
    #time.sleep(1)
    phi.close()
    