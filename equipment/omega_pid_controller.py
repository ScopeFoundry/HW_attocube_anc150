from __future__ import division
import serial
import struct
import numpy as np


class OmegaPIDController(object):
    """ Omega PID Controller 7600 series communicating via RS-485 Modbus ASCII protocol
    
    """
    def __init__(self,port="COM7", address=0x01, debug=False):
        self.port = port
        self.address = address
        self.debug =debug
        
        """If port is a Serial object (or other file-like object)
        use it instead of creating a new serial port"""
        if hasattr(port, 'read'):
            self.ser = self.port
            self.port = None
        else:        
            self.ser = serial.Serial(self.port, baudrate = 9600, bytesize=7, parity='E', 
                    stopbits=1, xonxoff=0, rtscts=0, timeout=0.1)
        
    def read_for_data_log(self):
        self.temp, self.setp = 0.1 * np.array(self.send_analog_read(0x1000, 2))
        self.outp1, self.outp2 = 0.1 * np.array(self.send_analog_read(0x1012, 2))
        return (self.temp, self.setp, self.outp1, self.outp2)
    
    def load_settings(self):
        "Read all settings from controller"

        self.temp, self.setp = 0.1 * np.array(self.send_analog_read(0x1000, 2))
        #need more
        self.read_ctrl_method()
        self.read_heat_cool_ctrl()
        self.outp1, self.outp2 = 0.1 * np.array(self.send_analog_read(0x1012, 2))
        self.software_version = self.send_analog_read(0x102F) 
    
    def read_temp(self):
        self.temp = 0.1 * self.send_analog_read(0x1000)
        return self.temp
    
    def read_setpoint(self):
        self.setp = 0.1 * self.send_analog_read(0x1001)
        return self.setp
        
    def set_setpoint(self, setp):
        self.send_analog_write(0x1001, int(setp*10) )
        self.setp = setp
        return self.setp
    
    def read_output1(self):
        self.outp1 = 0.1 * self.send_analog_read(0x1012)
        return self.outp1
        
    def read_output2(self):
        self.outp2 = 0.1 * self.send_analog_read(0x1013)
        return self.outp2
        
    def set_output1(self, outp1):
        "set output in percent, only in manual control"
        self.send_analog_write(0x1012, int(outp1*10) )
        self.outp1 = outp1
        return self.outp1
        
    def set_output2(self, outp2):
        "set output in percent, only in manual control"
        self.send_analog_write(0x1012, int(outp2*10) )
        self.outp2 = outp2
        return self.outp2


    def read_ctrl_method(self):
        self.ctrl_method_i = self.send_analog_read(0x1005)
        self.ctrl_method_name = self.CTRL_METHODS[self.ctrl_method_i]
        
        return (self.ctrl_method_i, self.ctrl_method_name)
    
    def set_ctrl_method(self, ctrl_method_i):
        
        ctrl_method_i = int(ctrl_method_i)
        assert 0 <= ctrl_method_i <= 3

        self.send_analog_write(0x1005, ctrl_method_i)
        
        self.ctrl_method_i = ctrl_method_i
        self.ctrl_method_name = self.CTRL_METHODS[self.ctrl_method_i]

        return (self.ctrl_method_i, self.ctrl_method_name)

    def read_heat_cool_ctrl(self):
        self.heat_cool_ctrl_i = self.send_analog_read(0x1006)
        self.heat_cool_ctrl_name = self.HEAT_COOL_CTRLS[self.heat_cool_ctrl_i]
        
        return (self.heat_cool_ctrl_i, self.heat_cool_ctrl_name)
    
    def set_heat_cool_ctrl(self, heat_cool_ctrl_i):
        
        heat_cool_ctrl_i = int(heat_cool_ctrl_i)
        assert 0 <= heat_cool_ctrl_i <= 3

        self.send_analog_write(0x1006, heat_cool_ctrl_i)
        
        self.heat_cool_ctrl_i = heat_cool_ctrl_i
        self.heat_cool_ctrl_name = self.HEAT_COOL_CTRLS[self.heat_cool_ctrl_i]

        return (self.heat_cool_ctrl_i, self.heat_cool_ctrl_name)
            
    
        
    def modbus_command(self, command, register, data):
        address = self.address
        message = bytearray([address, command, register >> 8, register % 0x100, data >> 8, data %0x100])
    
        lrc = (0x100 + 1 + ~(sum(message) % 0x100)) % 0x100
        message.append(lrc)          # Add to the end of the message
        
        ascii_message = ":" + "".join( "%02X" % b for b in message) + "\r\n"
        
        if self.debug:print repr(message)
        if self.debug:print repr(ascii_message)
    
        return ascii_message
            
    def analog_read_command(self, register, length):
        return self.modbus_command(0x03, register, data=length)

    def send_analog_read(self, register, length=None):
        """
            sends a analog read command FC 0x03 to device
            and returns an short (16bit) int array of length "length".
        """
        return_single = False
        if length == None:
            return_single = True
            length = 1
        
        register = int(register)
        length = int(length)
        assert 1 <= length <= 8
        
        self.ser.write(self.analog_read_command(register, length))
        output = self.ser.readline() # is \r\n included !?
        ":01030200EA10"

        assert output[0] == ':'
        #create byte array from output
        output_hexstr = output[1:-2] # remove starting ":" and ending \r\n
        output_bytes = bytearray( 
			[ int(output_hexstr[i:i+2], 16) for i in range(0, len(output_hexstr), 2) ] )
        
        if self.debug: print "output_bytes", [hex(a) for a in output_bytes]
        
        lrc = (0x100 + 1 + ~(sum(output_bytes[:-1]) % 0x100)) % 0x100
        assert output_bytes[-1] == lrc # error check
        
        assert output_bytes[0] == self.address
        assert output_bytes[1] == 0x03
        assert output_bytes[2] == length*2
        
        data_bytes = output_bytes[3:-1]
        
        if self.debug: print "data_bytes", [hex(a) for a in data_bytes]
        
        #return struct.unpack("<%ih" % length, data_bytes)
        data_shorts = [
            ( (data_bytes[i] << 8) + data_bytes[i+1] ) 
                for i in range(0, len(data_bytes), 2 ) ]
        if return_single:
            return data_shorts[0]
        else:
            return data_shorts
        
    def analog_write_command(self, register, data):
        return self.modbus_command(0x06, register, data)

    def send_analog_write(self, register, data):
        cmd = self.analog_write_command(register, data)
        self.ser.write(cmd)
        output = self.ser.readline() # need to check to see if output contains \r\n
        # device should echo write command on success
        if self.debug: print "cmd", repr(cmd)
        if self.debug: print "ouput", repr(output)
        assert output == cmd


    CTRL_METHODS = ("PID", "ON/OFF", "Manual", "PID Program Ctrl")
    HEAT_COOL_CTRLS = ("Heating", "Cooling", "Heating/Cooling", "Cooling/Heating")

    _CN7x00_registers = [        
        ( 0x1000 , "Process value (PV)" ),
        ( 0x1001 , "Set point (SV)" ),      # Unit is 0.1, oC or oF
        ( 0x1002 , "Upper-limit of temperature range" ),
        ( 0x1003 , "Lower-limit of temperature range" ),
        ( 0x1004 , "Input temperature sensor type" ), 
        ( 0x1005 , "Control method" ), #0: PID, 1: ON/OFF, 2: manual tuning, 3: PID program control
        ( 0x1006 , "Heating/Cooling control selection" ), #0: Heating, 1: Cooling, 2: Heating/Cooling, 3: Cooling/Heating
        ( 0x1007 , "1st group of Heating/Cooling control cycle" ), 
        ( 0x1008 , "2nd group of Heating/Cooling control cycle" ),
        ( 0x1009 , "PB Proportional band" ),
        ( 0x100A , "Ti Integral time" ),
        ( 0x100B , "Td Derivative time" ),
        ( 0x100C , "Integration default 0~100%, unit is 0.1% " ),
        ( 0x100D , "Proportional control offset error value, when Ti = 0 " ),
        ( 0x100E , "The setting of COEF when Dual Loop output control are used" ),
        ( 0x100F , "The setting of Dead band when Dual Loop output control are used" ),
        ( 0x1010 , "Hysteresis setting value of the 1st output group" ),
        ( 0x1011 , "Hysteresis setting value of the 2nd output group" ),
        ( 0x1012 , "Output value read and write of Output 1" ),
        ( 0x1013 , "Output value read and write of Output 2" ),
        ( 0x1014 , "Upper-limit regulation of analog linear output" ),
        ( 0x1015 , "Lower-limit regulation of analog linear output" ),
        ( 0x1016 , "Temperature regulation value" ),
        ( 0x1017 , "Analog decimal setting" ),
        ( 0x101C , "PID parameter selection" ),
        ( 0x101D , "SV value corresponded to PID value" ),
        ( 0x1020 , "Alarm 1 type" ),
        ( 0x1021 , "Alarm 2 type" ),
        ( 0x1022 , "Alarm 3 type" ),
        ( 0x1023 , "System alarm setting" ),
        ( 0x1024 , "Upper-limit alarm 1" ),
        ( 0x1025 , "Lower-limit alarm 1" ),
        ( 0x1026 , "Upper-limit alarm 2" ),
        ( 0x1027 , "Lower-limit alarm 2" ),
        ( 0x1028 , "Upper-limit alarm 3" ),
        ( 0x1029 , "Lower-limit alarm 3" ),
        ( 0x102A , "Read LED status" ),
        ( 0x102B , "Read push button status" ),
        ( 0x102C , "Setting lock status" ),
        ( 0x102F , "Software version" ),
        ( 0x1030 , "Start pattern number" ),
    ]    
        #1040H~ 1047H ,Actual step number setting inside the correspond pattern 
        #1050H~ 1057H ,Cycle number for repeating the execution of the correspond pattern 
        #1060H~ 1067H ,Link pattern number setting of the correspond pattern 
        #2000H~ 203FH ,Pattern 0~7 temperature set point setting Pattern 0 temperature is set to 2000H~2007H 
        #2080H~ 20BFH ,Pattern 0~7 execution time setting Pattern 0 time is set to 2080H~2087H 


class OmegaPtPIDController(object):
    """ Omega PID Controller Pt Platinum  series via Serial Communications protocol
    
    See Manual M5452
    
    """
    def __init__(self,port="COM7", address=0x01, debug=False):
        self.port = port
        self.address = address
        self.debug =debug
        
        """If port is a Serial object (or other file-like object)
        use it instead of creating a new serial port"""
        if hasattr(port, 'read'):
            self.ser = self.port
            self.port = None
        else:        
            self.ser = serial.Serial(self.port, baudrate = 9600, bytesize=7, parity='E', 
                    stopbits=1, xonxoff=0, rtscts=0, timeout=0.1)
            
    """
    Protocol
    
    The protocol is command/response, based on 4 command classes:
        Get (G), Put (P), Read (R) and Write (W).
        A Get is used to read the current value resident in RAM, 
        a Put is used to write a parameter to RAM without committing it to non-volatile memory.
        A Read is used to retrieve the value of a parameter stored in non-volatile memory and
        a write is used to commit a parameter value to non-volatile memory.
        
    3.2 Command Structure
    The overall structure of a command packet is as follows:
    -- A start of frame (SOF) character -- usually '*'
    -- A command class (GPRW)
    -- A command ID - a hex number identifying the message.
    -- A mandatory space if there are parameters following the command ID.
    -- A parameter List.
    -- An end of frame (EOF) character -- usually a carriage return.
    A unit address is optional.
    An address is a hex-encoded number in the range 0-199 (00 - C7 hex) between the start of frame and the command class.
    For example, to get the current process value, without an address would be: "*G110 <CR>"
    In this case the command class is 'G', the command ID is 110 (hex) and this command takes no parameters.
    If this were addressed to unit 100 (hex value 64), the command would be: "*64G110 <CR>"
    
    ResponseFormat
    
    The response format depends on whether a command echo has been selected. If selected, the address (if present), command class and command ID precede the parameters returned.
    For example, if an echo is selected, the previous command would return:
    "G110+32.0<CR>" (no address)
    "64G110+32.0<CR> (if the unit responding had address = 64 (hex).
    If echo is not selected, in both cases, only "+32.0<CR>" would be returned.
    For put (P) and Write (W) type transactions, only the command is echoed if echo is on. Thus, "*Pxxx yyyyyy<CR>" will echo "Pxxx<CR>".
    """
    
    def send_cmd(self,cmd_class, cmd_name, param_list=None):
        cmd_id, cmd_classes = self._Pt_Params_by_name[cmd_name]
        assert cmd_class in cmd_classes
        out = "*%s%03X" % (cmd_class[0], cmd_id)
        if param_list:
            out = out + " " + param_list +"\r"
        else:
            out += "\r"
        
        self.ser.write(out)
        
        # read response
        if cmd_class in 'GR':
            resp = self.ser.readline()
            assert resp[-1] == '\r'
            return resp[:-1]
        else:
            # if echo need to read echo
            return True
    
    _Pt_Params = [
        (0x100, 'GPRW', "Input_Configuration"),
        (0x101, 'GPRW', "Filter_Constant"),
        (0x110, 'G'   , "Current_Reading"),
        (0x111, 'G'   , "Peak_Reading"),
        (0x112, 'G'   , "Valley_Reading"),
        (0x120, 'GPRW', "TC_Calibration_Type"),
        (0x121, 'GPRW', "TC_Calibration_Single_Point"),
        (0x122, 'GPRW', "TC_Calibration_Double_Point_Low"),
        (0x123, 'GPRW', "TC_Calibration_Double_Point_High"),
        (0x130, 'GPRW', "Process_Reading_1_Low"),
        (0x131, 'GPRW', "Process_Range_Input_1_Low"),
        (0x132, 'GPRW', "Process_Reading_2_High"),
        (0x132, 'GPRW', "Process_Range_Input_2_High"),
        
        (0x200, 'GPRW', "Display_Configuration"),
        (0x210, 'GPRW', "Excitation_Voltage"),
        (0x220, 'GPRW', "Safety_Configuration"),
        (0x221, 'GPRW', "Loop_Break_Configuration"),
        (0x222, 'GPRW', 'Set_Point_Low_Limit'),
        (0x223, 'GPRW', 'Set_Point_High_Limit'),
        
        #0x300's are communication controls
        
        (0x400, 'GPRW', "Setpoint_1"),
        (0x401, 'GPRW', "Remote_Setpoint_Configuration"),
        (0x410, 'GPRW', "Setpoint_2"),
        (0x420, 'GPRW', "Remote_Process_Range_Setpoint_Min"),
        (0x421, 'GPRW', "Remote_Process_Range_Input_Min"),
        (0x422, 'GPRW', "Remote_Process_Range_Setpoint_Max"),
        (0x423, 'GPRW', "Remote_Process_Range_Input_Max"),
        
        (0x500, 'GPRW', "PID_Configuration"),
        (0x501, 'GPRW', "PID_Low_Clamping_Limit"),
        (0x502, 'GPRW', "PID_High_Clamping_Limit"),
        (0x503, 'GPRW', "PID_P_Param"),
        (0x504, 'GPRW', "PID_I_Param"),
        (0x505, 'GPRW', "PID_D_Param"),
        
        (0x600, 'GPRW', "Output_Mode"),
        (0x601, 'GPRW', "Output_Type"),
        (0x610, 'GPRW', "Output_ON_OFF_Configuration"),
        (0x620, 'GPRW', "Output_Alarm_Configuration"),
        (0x621, 'GPRW', "Output_Alarm_High_Value"),
        (0x622, 'GPRW', "Output_Alarm_Low_Value"),
        (0x623, 'GPRW', "Output_Alarm_On_Delay"),
        (0x624, 'GPRW', "Output_Alarm_Off_Delay"),
        (0x625, 'GPRW', "Output_Alarm_HiHi_Mode"),
        (0x626, 'GPRW', "Output_Alarm_HiHi_Offset"),
        
        #More
        
        (0xF20, 'G'   , "Version_Number"),
        (0xF22, 'G'   , "Bootloader_Version"),
        (0xF30, 'P'   , "Set_Factory_Defaults"),
        ]
    
    _Pt_Params_by_name = {cmd_name:(cmd_id, cmd_classes) for cmd_id, cmd_classes,cmd_name in _Pt_Params }
    
    def get_setpoint1(self):
        resp = self.write_cmd("G", "Setpoint_1")
        sv = float(resp)
        return sv
        
    def put_setpoint1(self, sv):
        self.write_cmd('P', "Setpoint_1", "%+1.2f" % sv)
    
    def get_current_reading(self):
        resp = self.write_cmd("G", "Current_Reading")
        pv = float(resp)
        return pv
    
    output_modes = ["OFF", "PID", "ON-OFF", "scaled", "Alarm1", "Alarm2", "RampSoak_RE.ON", "RampSoak_SE.ON"]
    output_mode_ids = {name:ii for ii, name in enumerate(output_modes)}
    
    def get_output_mode(self, nout=1):
        assert nout in (1,2,3,4)
        resp = self.write_cmd("G", "Output_Mode", "%i" % nout)
        mode_num = int(resp)
        mode = self.output_modes[mode_num]
        return mode
    
    def put_output_mode(self, mode_name, nout=1):
        mode_id = self.output_mode_ids[mode_name]
        assert nout in (1,2,3,4)
        return self.write_cmd("G", "Output_Mode", "%i%i" % (nout, mode_id))
    
    def get_version_num(self):
        return self.send_cmd('G', 'Version_Number')
        
    
    
if __name__ == '__main__':
    pid1 = OmegaPIDController(port="COM7", address=0x01, debug=True)    
    print "TEMP:", pid1.read_temp()