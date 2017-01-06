# Edward Barnard 2013-06-18

import LabJack.u3 as u3

class LabJackCounter(object):

    """Works with LabJack U3 v1.30 with counters attached to EIO0 and EIO1"""

    CLOCK_PER_MS = 4000 # clock is 4MHz

    def __init__(self):
    
        lj = self.lj = u3.U3()
    
        lj.configIO(
        	EnableCounter0=True, EnableCounter1=True,
        	NumberOfTimersEnabled = 2, TimerCounterPinOffset=6, FIOAnalog=0x0F)
        #timer 0 on FIO6
        #timer 1 on FIO7
        #counter0 on EIO0
        #counter1 on EIO2
        lj.getFeedback(u3.TimerConfig(timer = 0, TimerMode = 10)) # system timer LSW
        lj.getFeedback(u3.TimerConfig(timer = 1, TimerMode = 11)) # system timer MSW

        self.lj_feedback_req = [
            u3.Timer(timer=0, UpdateReset = False, Value = 0, Mode = None),
            u3.Timer(timer=1, UpdateReset = False, Value = 0, Mode = None),
            u3.Counter(counter = 0, Reset=True),
            u3.Counter(counter = 1, Reset=False)
            ]   

        self.c0 = 0
        self.c1 = 0
        self.t  = 0 # in clock ticks
        self.t_prev = -1*LabJackCounter.CLOCK_PER_MS # in clock ticks
        self.read_rates()
        
    def read_rates(self):
        
        tLSW, tMSW, self.c0, self.c1 = self.lj.getFeedback(self.lj_feedback_req)
        
        #t = tMSW << 32 + tLSW
        self.t_prev = self.t
        self.t = tLSW
        
        dt = abs(self.t - self.t_prev) # clock ticks
        
        dt_sec = dt*1e-3/LabJackCounter.CLOCK_PER_MS

        #c0_rate = c0*1e3/REFRESH_MS
        c0_rate = self.c0 /dt_sec  # Hz
        c1_rate = self.c1 /dt_sec  # Hz
    
        return c0_rate, c1_rate, self.c0, self.c1, dt_sec
    
    def read_c0_rate(self):
    	return self.read_rates()[0]
    
    def close(self):
        self.lj.close()