"""
Controls written collaboratively by Alan Buckley, Ed Barnard, Frank Ogletree
Modified 12/12/16 DFO
"""

import serial
import time

PORT = 'COM7'   #our COM port
GUN_ADDRESS = 03    #defined by PHI??
#PHI gun commands
GET_VERSION = 0x02  #firmware version
SET_BEAM_V =  0x0A  #set beam voltage
GET_BEAM_V =  0x0B  #get beam voltage (was 0x0C before, did not work)
SET_BEND_V =  0x0D  #set beam bending voltage (no bend electrode in Auger ion gun)
SET_COND_V =  0x0F  #set condenser voltage
GET_COND_V =  0x10  #get condenser voltage
SET_FLOAT_V = 0x11  #set float voltage
GET_FLOAT_V = 0x12  #get float voltage
SET_GRID_V =  0x13  #set grid voltage, cannot read back
SET_OBJ_V =   0x15  #set objective voltage
GET_OBJ_V =   0x16  #get objective lens voltage
SET_EMISS_A = 0x17  #set emission target current in mA
GET_EMISS_A = 0x18  #get emission current in mA
GET_PRESSURE= 0x19  #get pressure in mPa for emission 25 mA
SET_STATE =   0x1C  #sets multiple parameters and flags, including beam, cond, obj, emiss, grid
CONFIRM =     0x28  #exact purpose not known, appears to be communication test
HEADER =      0x39  #exact purpose not known, used in some observed command sequences
FOOTER =      0x48  #exact purpose not known, used in some observed command sequences
GUN_ENABLE =  0x35  #probably enables gun, not confirmed
GUN_DISABLE = 0x36  #probably disables gun, not confirmed
    #raster size calculated in electronics based on voltage, reset when voltage changed
SET_X_SIZE =  0x43  #set/request x raster size in mm
SET_Y_SIZE =  0x44  #set/request x raster size in mm
SET_X_OFF  =  0x45  #set/request x raster offset in mm
SET_Y_OFF  =  0x46  #set/request x raster offset in mm

class PhiIonGun(object):
    """
    Class Description: Equipment level controls written for ion gun control via RS232/USB
    """
    def __init__(self, port=PORT, address=GUN_ADDRESS, debug = False):
        self.port = port
        self.debug = debug
        self.address = address
        
        if self.debug: print "Phi Ion Gun init, port=%s" % self.port
        
        self.ser = self.com_open(self.port)
        self.ask_in_progress = False        
        self.initialize()       
   
    #serial interface functions=============================
    
    def close(self):
        self.ser.close()

    def com_open(self,com_port):
        return serial.Serial(port=com_port, baudrate=9600, timeout=1.0)
    
    #gun command protocol functions
    
    def ask_cmd(self, cmd_id, data=None):
        '''
        Serial command format (reverse engineered)
        Each command starts with '~ ' then "address" (03) for multiple devices on one com
        port, then internal ion gun electronics register number "cmd id" then data (if any)
        followed by hex checksum (excluding leading ~) and 'CR' 
        All commands return status ('address' OK 00 ) and optional data then checksum then 'CR'

        Module handles synthesis and submission of user commands. 
        Creates and submits command if self.ask_in_progress flag is False. 
        '''
        
        for i in range(10): #is this still needed? DFO - yes, monitor loop may be in conflict with GUI
            if self.ask_in_progress:
                time.sleep(0.13)
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
            resp = self.phi_readline()      
            if self.debug:
                print "ask_cmd resp->", repr(resp)

        finally:
            self.ask_in_progress = False       
        return resp
    
    def phi_readline(self):
        '''Reads chars until CR, returns string not including CR'''
        in_char = ''
        line = ''
        while in_char != '\r':
            in_char = self.ser.read() #needs error handling
            if in_char != '\r':
                line+= in_char
        return line
        
    def checksum_func(self, data):
        '''Function calculates the checksum of each command.'''
        checksum = 0x00
        for b in data:
            checksum += ord(b)
            checksum = checksum & 0xFF
        return checksum
    
    def parse_data(self, response):
        '''This is a slicing function meant to extract numeric values from RS232 messages received from the ion gun.'''
        chunk = response.split()[3]
        return chunk             

    #ion gun control functions=============================
   
    def read_version(self):
        """Function returns the ion gun firmware timestamp. Tells you the age of the installed firmware."""
        result = self.ask_cmd(GET_VERSION, data=None)
        _list = result.split()
        text = "Version "
        for _str in _list[3:-1]:
            text += _str + ' '
        return text
        
    
    def initialize(self):
        """Standard startup routine upon startup and RS232 transmission start."""
        if self.debug: 
            print "initialize"
        self.ask_cmd(0x01)
        self.ask_cmd(GET_VERSION)
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
        """Inquires after the condenser lens voltage. A response is given in volts."""
        resp = self.ask_cmd(GET_COND_V)
        value = self.parse_data(resp)
        if self.debug:  print "read_condenser_v: ",value 
        return float(value)
    
    def read_emission_current(self):
        """Inquires after the ion gun emission current. A response is given in milliamperes."""
        resp = self.ask_cmd(GET_EMISS_A)
        value = self.parse_data(resp)
        if self.debug: print "current (mA):", resp
        return float(value)
    
    def read_beam_v(self):
        """Inquires after the ion beam voltage. A response is given in volts."""
        resp = self.ask_cmd(GET_BEAM_V) 
        value = self.parse_data(resp)
        if self.debug: print "read_beam_v:", resp
        return float(value)
    
    def read_extractor_p(self):
        """Inquires after the extractor pressure value in millipascals (mPa)."""
        resp = self.ask_cmd(GET_PRESSURE)
        value = self.parse_data(resp)
        if self.debug: print "extractor pressure:", resp
        return float(value)
    
    def read_float(self):
        """Inquires after the value of the ion gun's float voltage. A response is given in volts."""
        resp = self.ask_cmd(GET_FLOAT_V)
        value = self.parse_data(resp)
        if self.debug: print "float_v:", resp
        return float(value)
    
    def read_objective_v(self):
        """Inquires after the value of the ion gun's objective lens voltage. A response is given in volts."""
        resp = self.ask_cmd(GET_OBJ_V)
        value = self.parse_data(resp)
        if self.debug: print "objective_v:", resp
        return float(value)

    def write_beam_v(self, data): 
        #was previously write_energy
        #"""def write_beam_v(self, data):
        #_float = ("%.3f" % data)
        #beam_v = self.ask_cmd(0x0B, _float)
        #if self.debug:
        #    print "write_beam_v"
        #return beam_v 
        #"""
        """Sets the ion beam potential in volts."""
        value = ("%.3f" % data)
        beam_v = self.ask_cmd(SET_BEAM_V, value)
        if self.debug: print "write_beam_v"
        return beam_v
       
    def write_grid_v(self, grid_v):
        """Sets grid voltage of a charged mesh which encloses ion beam origin."""
        assert 99 < grid_v < 201
        value = ("%.3f" % grid_v)
        grid_v = self.ask_cmd(SET_GRID_V, value)
        if self.debug: print "write grid_v"
        return grid_v

    def write_condenser_v(self, data):
        """Sets ion gun condenser lens voltage"""
        value = ("%.3f" % data)
        cond_v = self.ask_cmd(SET_COND_V, value)
        if self.debug: print "write_condenser_v"
        return cond_v

    def write_objective_v(self, data):
        """Sets ion gun objective lens voltage."""
        _float = ("%.3f" % data)
        obj_v = self.ask_cmd(SET_OBJ_V, _float)
        if self.debug: print "write_objective_v"
        return obj_v

    def write_bend_v(self, data):
        """Sets ion gun bend voltage, which affects the beam by electrostatic repulsion. 
        Bending of the beam is dependent on electric field strength determined by this voltage.
        Not implemented in Auger system ion gun
        """
        value = ("%.3f" % float(-1*data))
        bend_v = self.ask_cmd(SET_BEND_V, value)
        if self.debug: print "write_bend_v"
        return bend_v
    
    def write_emission_current(self, data):
        """Sets the ion gun emission current value in milliamperes."""
        #Note: This is the same function listed as "Current" in other program
        value = ("%.3f" % data)
        emi_i = self.ask_cmd(SET_EMISS_A, value)
        if self.debug: print "write_emission_current"
        return emi_i

    def write_float_v(self, data):
        """Sets ion gun float voltage in volts"""
        value = ("%.3f" % float(-1*data))
        float_v = self.ask_cmd(SET_FLOAT_V, value)
        if self.debug: print "write_float_v"
        return float_v

    def xsize(self, data):
        """Sets raster size along the (horizontal) x-axis in millimeters."""
        x_value = ("%.2f" % data)
        xmm = self.ask_cmd(SET_X_SIZE, x_value)
        if self.debug: print "set_xsize"
        return xmm
    
    def ysize(self, data):
        """Sets raster size along the (vertical) y-axis in millimeters."""
        y_value = ("%.2f" % data)
        ymm = self.ask_cmd(SET_Y_SIZE, y_value)
        if self.debug: print "set_ysize"
        return ymm
    
    def xoff(self, data):
        """Sets the value of raster offset along the (horizontal) x-axis in millimeters."""   
        x_value = ("%.3f" % data)
        xoff = self.ask_cmd(SET_X_OFF, x_value)
        if self.debug: print "set_xoff"
        return xoff

    def yoff(self, data):
        """Sets the value of raster offset along the (vertical) y-axis in millimeters."""
        y_value = ("%.3f" % data)
        yoff = self.ask_cmd(SET_Y_OFF, y_value)
        if self.debug: print "set_yoff"
        return yoff

##---------- Commonly found entities----------##
    def Header(self):
        """Command is issued by convention in certain versions of the manufacturer software."""
        header = self.ask_cmd(HEADER)
        if self.debug:
            print "Header:", header
        return header
        
    def Footer(self):
        """Command is issued by convention in certain versions of the manufacturer software."""
        footer = self.ask_cmd(FOOTER)
        if self.debug:
            print "Footer:", footer
        return footer

    def Write_Confirmation(self):
        """Command is not necessary for operation of the ion gun. In manufacturer software, 
        this command is issued as a means of command delivery verification"""
        statement = self.ask_cmd(CONFIRM)
        if self.debug:
            print "Write confirm:", statement
        return statement

    def Gun_Disable(self):
        """We suspect this function sets a flag at the hardware level denoting the ion gun is inactive."""

        Gun_off = self.ask_cmd(GUN_DISABLE)
        if self.debug:
            print "Gun Disable:", Gun_off
        return Gun_off

    def Gun_Enable(self):
        """We suspect this function sets a flag at the hardware level denoting the ion gun is active."""
        Gun_on = self.ask_cmd(GUN_ENABLE)
        if self.debug:
            print "Gun Enable: ", Gun_on
        return Gun_on

    def Set_Raster_Mode(self, State='OFF'):
        """Allows user to switch between available raster modes in ion gun software. 
        Options are as follows: OFF, INTERNAL, EXTERNAL.
        """
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
            while self.parse_data(self.ask_cmd(0x1F)) != str(1):
                self.ask_cmd(0x1F)
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
            self.Header()
            if self.debug:
                print "External Raster Set!"
        
        elif State == 'OFF':
            self.ask_cmd(0x36)
            

##--edited below--##
    def State_Data_Packet(self, beamv=0, gridv=0, condv=0, objv=0, bendv=0, emiv=0, State='OFF'):
        """Allows user to switch between available modes of operation in ion gun software. 
        Options are as follows: OFF, BLANK, STANDBY, ACTIVE.

        Ion gun is meant to bombard sample with ionized particles when gun is set to ACTIVE.
        See operating manual for details on other modes of operation.
        """

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
        set_state = self.ask_cmd(SET_STATE, state_data)
        
        if self.debug:
            print(set_state)
        return set_state
        





    

        
        
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
    