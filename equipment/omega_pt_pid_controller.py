'''
Created on Nov 22, 2015

@author: Edward Barnard
'''

import minimalmodbus

class OmegaPtPIDController(minimalmodbus.Instrument):
    '''
    M5458
    '''

    def __init__(self, port, address=0x01 ):
        minimalmodbus.Instrument.__init__(self, port, address, mode=minimalmodbus.MODE_RTU)
        
    def read_temp(self):
        return self.read_float(0x210) # CURRENT_INPUT_VALUE
    
    def read_setpoint1(self):
        return self.read_float(0x220)

    def write_setpoint1(self, value):
        return self.write_float(0x220, float(value))

    def read_setpoint2(self):
        return self.read_float(0x222)
    
    def write_setpoint2(self, value):
        return self.write_float(0x222, float(value))
    
    def read_control_setpoint(self):
        return self.read_float(0x224)

    def read_pid_output(self):
        return self.read_float(0x022A)
    
    def read_current_input_valid(self):
        return self.read_register(0x022C)
    
    ### PID Parameters
    def read_pid_P(self):
        return self.read_float(0x2A4)

    def read_pid_I(self):
        return self.read_float(0x2A6)

    def read_pid_D(self):
        return self.read_float(0x2A8)

    def write_pid_P(self, value):
        return self.read_float(0x2A4, value)

    def write_pid_I(self, value):
        return self.read_float(0x2A6, value)

    def write_pid_D(self, value):
        return self.read_float(0x2A8, value)

    def read_device_id(self):
        return self.read_long(0x0200)
    def read_version_number(self):
        return self.read_long(0x0202)
    def read_system_status(self):
        return self.read_long(0x0204)   
    def read_boot_loader_version(self):
        return self.read_long(0x0206)   
    def read_hardware_version(self):
        return self.read_long(0x0208)

    def read_run_mode(self):
        state_code = self.read_register(0x240)
        return self.system_state_table[state_code][1]
    
    def write_run_mode(self, mode):
        state_code = self.system_state_dict[mode][0]
        return self.write_register(0x240, state_code)
    
    system_state_table = (
            (0,   "LOAD",   "File transfer in progress"),
            (1,   "IDLE",   "Idle, no control"),
            (2,   "INPUT_ADJUST",   "Adjusting input value"),
            (3,   "CONTROL_ADJUST",  "Adjusting output value"),
            (4,   "MODIFY",  "Modify parameter in OPER mode"),
            (5,   "WAIT",   "Waiting for RUN condition"),
            (6,   "RUN", "System is running"),
            (7,   "STANDBY", "Standby mode"),
            (8,   "STOP",   "Stopped mode"),
            (9,   "PAUSE",   "Paused mode"),
            (10,  "FAULT",   "Fault detected"),
            (11,  "SHUTDOWN",   " Shutdown condition detected"),
            (12,  "AUTOTUNE",   " Autotune in progress"),
        )
    
    system_state_dict = { line[1]:line for line in system_state_table }
    
if __name__ == '__main__':
    pid = OmegaPtPIDController(port="COM9", address=1)
    
    print hex(pid.read_device_id())
    print hex(pid.read_version_number())
    print hex(pid.read_system_status())
    print hex(pid.read_boot_loader_version())
    print hex(pid.read_hardware_version())

    print pid.read_temp()
    print pid.read_setpoint1()
    print pid.read_setpoint2()
    print pid.read_control_setpoint()
    print pid.write_setpoint1(53.)
    print pid.read_setpoint1()
    print pid.read_setpoint2()
    print pid.read_control_setpoint()

    print pid.write_run_mode('IDLE')
    
    print pid.read_run_mode()
    print pid.write_register(0x240, 6)
    print pid.read_run_mode()
    
    print pid.read_pid_output()
    
    print pid.read_current_input_valid()
    