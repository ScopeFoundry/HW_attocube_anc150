'''
Created on 31.08.2014

@author: Benedikt
'''

import numpy as np
import timeit
import matplotlib.pyplot as plt
import __future__


from Hardware_components.keithley_sourcemeter import KeithleySourceMeterComponent 




class KeithleySourceMeter(KeithleySourceMeterComponent):#object -->KeithleySourceMeterComponent
    '''
    classdocs
    '''
    def resetA(self):
        self.ser.write('smua.reset()\n')        

    def setRanges_A(self,Vmeasure,Vsource,Imeasure,Isource):
        '''
        determines the accuracy for measuring and sourcing
        Alternatively use setAutorange_A() which might be slower
            possible V ranges: 200 mV, 2 V, 20 V, 200V 
            possible I ranges: 100 nA, 1 uA, 10uA, ... 100 mA, 1 A, 1.5, 10 A (10 A only in pulse mode)
        refer to UserManual/Specification for accuracy
        '''
        self.ser.write('smua.source.rangev = '+str(Vsource)+'\r\n')
        self.ser.write('smua.measure.rangev = '+str(Vmeasure)+'\r\n')   
        self.ser.write('smua.source.rangei = '+str(Isource)+'\r\n')
        self.ser.write('smua.measure.rangei = '+str(Imeasure)+'\r\n')
        
    def setAutoranges_A(self):
        '''
        Alternatively use setRanges_A(Vmeasure,Vsource,Imeasure,Isource) to set ranges manually, which might be faster
        '''
        self.ser.write('smua.source.autorangev = smua.AUTORANGE_ON\r\n')
        self.ser.write('smua.measure.autorangev = smua.AUTORANGE_ON\r\n')   
        self.ser.write('smua.source.autorangei = smua.AUTORANGE_ON\r\n')
        self.ser.write('smua.measure.autorangei = smua.AUTORANGE_ON\r\n')                           
        
    def setV_A(self,V):
        """
        set DC voltage on channel A and turns it on
        """
        self.ser.write('smua.source.func = smua.OUTPUT_DCVOLTS\r\n')
        self.ser.write('smua.source.levelv = '+str(V)+'\r\n')
        self.ser.write('smua.source.output = smua.OUTPUT_ON\r\n')
        #print('set Voltage in channel A to '+str(V_A))
        pass
    
    def swichV_A_off(self):
        self.ser.write('smua.source.output = smua.OUTPUT_OFF\r\n')
               
    def getI_A(self):
        """
        gets a single current measurement
        use measureI_A(self,N,KeithleyADCIntTime,delay) for multiple readouts
        """
        self.ser.write('print(smua.measure.i())\r\n')               
        return float(self.ser.readline())
        
    def sourceVmeasureI(self,N,Vmax):
        self.ser.write('smua.reset();\n')
        self.ser.write('format.data = format.ASCII\r\n')
        self.ser.write('smua.nvbuffer1.clear()\r\n')
        self.ser.write('smua.nvbuffer1.appendmode = 1\r\n')        
        self.ser.write('smua.nvbuffer1.collectsourcevalues = 1\r\n')
        self.ser.write('smua.measure.count = 1\r\n')
        self.ser.write('smua.source.func = smua.OUTPUT_DCVOLTS\r\n')
        
        # first voltages
        self.ser.write('smua.source.levelv = 0.0\r\n')
        self.ser.write('smua.source.output = smua.OUTPUT_ON\r\n')
        self.ser.write('for v = 1, '+str(N)+' do smua.source.levelv = v * '+str(float(Vmax)/float(N))+' smua.measure.i(smua.nvbuffer1) end\r\n')
        self.ser.write('smua.source.output = smua.OUTPUT_OFF\r\n')
        
        # read out measured currents
        self.ser.write('printbuffer(1, smua.nvbuffer1.n, smua.nvbuffer1.readings)\r\n')
        StrI = self.ser.readline()
        I = np.array(StrI.replace(',', '').split(),dtype = np.float32)
        
        # read out sourced voltages
        self.ser.write('printbuffer(1, smua.nvbuffer1.n, smua.nvbuffer1.sourcevalues)\r\n')
        StrV = self.ser.readline()
        V = np.array(StrV.replace(',', '').split(),dtype = np.float32)

        return I,V
    
    def measureI_A(self,N,KeithleyADCIntTime,delay):
        """
        takes N current measurements and returns the avarage of them
        KeithleyADCIntTime = 0.1 sets integration time in Keitheley ADC to 0.1/60 sec
            Note: lowering KeithleyADCIntTime increases rate of measurements and decreases accuracy (0.001 is fastest and 25 slowest)
        delay [sec]: delay between measurements
        """
        
        self.ser.write('format.data = format.ASCII\r\n')
        
        # Buffer
        self.ser.write('smua.nvbuffer1.clear()\r\n')
        self.ser.write('smua.nvbuffer1.appendmode = 1\r\n')
        self.ser.write('smua.measure.count = 1\r\n')
        #self.ser.write('smua.nvbuffer2.appendmode = 1\r\n')        
        #self.ser.write('smua.nvbuffer2.clear()\r\n')            

        # Timestamps (if needed uncomment lowest section)       
        #self.ser.write('smua.nvbuffer1.collecttimestamps = 1\r\n')
        #self.ser.write('smua.nvbuffer1.timestampresolution=0.000001\r\n')

        # Speed configurations: 
        # autozero = 0 = off no significant speed boost
        # deleay/delayfactor seem to be 0 by default
        # nplc really does boost steed: nplc = 0.1 sets integration time in Keitheley ADC to 0.1/60
        #     Note: lowering nplc increases rate of measurements and decreases accuracy (0.001 is fastest and 25 slowest)   
        self.ser.write('smua.measure.nplc = '+str(KeithleyADCIntTime)+'\r\n')
        self.ser.write('smua.measure.delay = '+str(delay)+'\r\n')
        #self.ser.write('smua.measure.delayfactor = 0\r\n')
        #self.ser.write('smua.measure.autozero = 0')
        
        # Make N measurements  
        self.ser.write('for v = 1, '+str(N)+'do smua.measure.i(smua.nvbuffer1) end\r\n')
        # read out measured currents
        self.ser.write('printbuffer(1, smua.nvbuffer1.n, smua.nvbuffer1.readings)\r\n')
        StrI = self.ser.readline()
        return np.array(StrI.replace(',', '').split(),dtype = np.float32)
    
        #self.ser.write('printbuffer(1, smua.nvbuffer1.n, smua.nvbuffer1.timestamps)\r\n')
        #Strt = self.ser.readline()
        #t = np.array(Strt.replace(',', '').split(),dtype = np.float32)  
        #return t,I       

            
    #===========================================================================
    # def sourceVmeasureI(self,V):
    #     I = np.arange(np.size(V, 0),dtype = float )
    #     for i in range(np.size(V, 0)):
    #         self.setV_A(V[i])
    #         I[i] = self.getI_A()
    #     return I
    #===========================================================================

if __name__ == '__main__':
    
    K1 = KeithleySourceMeter()
    K1.setup()
    
    K1.connect()
    K1.resetA()
    
    #K1.setRanges_A(Vmeasure=2,Vsource=2,Imeasure=0.1,Isource=0.1)
    K1.setAutoranges_A()
    K1.setV_A(V=0)
    
    
    """
    TODO
    loop over scan area
        I=K1.measureI_A()
        get average
        store it a data matrix
        
     
    """
    
    I = K1.measureI_A(N=100,KeithleyADCIntTime=1,delay=0)
    print 'average current is ',np.average(I,0) 
    print 'Integrated current is ',np.sum(I,0)
    #plt.ion() 
    plt.plot(I)
    plt.show()
    
    
    K1.swichV_A_off()         
    K1.disconnect()




    pass