import ctypes
from ctypes import c_int, c_byte, c_ubyte, c_short, c_double, cdll, pointer, byref
import time

import os
madlib_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__),"MADLib.dll"))
wdapilib_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__),"wdapi1010.dll"))

print "loading DLL:", repr(madlib_path)

wdapidll = cdll.LoadLibrary(wdapilib_path)
madlib = cdll.LoadLibrary(madlib_path)

madlib.MCL_SingleReadZ.restype = c_double
madlib.MCL_SingleReadN.restype = c_double
madlib.MCL_MonitorZ.restype = c_double
madlib.MCL_MonitorN.restype = c_double
madlib.MCL_ReadEncoderZ.restype = c_double

madlib.MCL_GetCalibration.restype = c_double
#more...


class MCLProductInformation(ctypes.Structure):
    _fields_ = [
        ("axis_bitmap",     c_byte),    #//bitmap of available axis
        ("ADC_resolution",  c_short), #//# of bits of resolution
        #("pad", c_byte),
        ("DAC_resolution",  c_short), #//# of bits of resolution
        ("Product_id",      c_short),   
        ("FirmwareVersion", c_short),
        ("FirmwareProfile", c_short),]
        
    _pack_ = 1 # important for field alignment
    
    def print_info(self):
        print "MCL Product Information"
        for fieldname, fieldtype in self._fields_:
            fieldval = self.__getattribute__(fieldname)
            print "\t", fieldname, "\t\t", fieldval, "\t\t", bin(fieldval)
        
        

class MCLNanoDrive(object):

    def __init__(self, debug=False):
        self.debug = debug
        
        handle = self._handle = madlib.MCL_InitHandle()

        if self.debug: print "handle:", hex(handle)

        if not handle:
            print "MCLNanoDrive failed to grab device handle ", hex(handle)

        self.prodinfo = MCLProductInformation()
        madlib.MCL_GetProductInfo(byref(self.prodinfo), handle)
        
        if self.debug: self.prodinfo.print_info()
        
        self.cal_X = None
        self.cal_Y = None
        self.cal_Z = None
        
        self.num_axes = 0
    
        self.cal = dict()
        for axname, axnum, axbitmap in [('X', 1, 0b001), ('Y', 2, 0b010), ('Z', 3, 0b100)]:
            axvalid = bool(self.prodinfo.axis_bitmap & axbitmap)
            if debug: print axname, axnum, "axbitmap:", bin(axbitmap), "axvalid", axvalid
            
            if not axvalid:
                if debug: print "No %s axis, skipping" % axname
                continue
            
            self.num_axes += 1
            
            cal = madlib.MCL_GetCalibration(axnum, handle)

            setattr(self, 'cal_%s' % axname, cal)
            self.cal[axnum] = cal
            if debug: print "cal_%s: %g" % (axname, cal)
        
        self.get_pos()
        
    def __del__(self):
        self.close()
        
    def close(self):
        madlib.MCL_ReleaseHandle(self._handle)
        
    def move_rel(self, dx, dy, dz=0):
        pass
        #TODO

    def set_pos(self, x, y, z=None):
        assert 0 <= x <= self.cal_X
        assert 0 <= y <= self.cal_Y
        #TODO z-axis is ignored        
        if z is not None:
            assert 0 <= z <= self.cal_Z

        
        self.set_pos_ax(x, 1)
        #madlib.MCL_DeviceAttached(200, self._handle)
        self.set_pos_ax(y, 2)
        if z is not None:
            self.set_pos_ax(z, 3)
        # MCL_DeviceAttached can be used as a simple wait function. In this case
        # it is being used to allow the nanopositioner to finish its motion before 
        # reading its position. (standard 200)
        #madlib.MCL_DeviceAttached(100, self._handle)
        
    def set_pos_ax(self, pos, axis):
        if self.debug: print "set_pos_ax ", pos, axis
        assert 1 <= axis <= self.num_axes
        madlib.MCL_SingleWriteN(c_double(pos), axis, self._handle)
        
    def get_pos(self):
        self.x_pos = madlib.MCL_SingleReadN(1, self._handle)
        self.y_pos = madlib.MCL_SingleReadN(2, self._handle)
        self.z_pos = madlib.MCL_SingleReadN(3, self._handle)
        
        return (self.x_pos, self.y_pos, self.z_pos)
        
if __name__ == '__main__':
    print "MCL nanodrive test"
    
    nanodrive = MCLNanoDrive(debug=True)
    
    #for x,y in [ (0,0), (10,10), (30,30), (50,50), (50,25), (50,0)]:
    for x,y in [ (30,0), (30,10), (30,30), (30,50), (30,25), (30,0)]:
        print "moving to ", x,y
        nanodrive.set_pos(x,y)
        x1,y1,z = nanodrive.get_pos()
        print "moved to ", x1, y1,z
        time.sleep(1)
    
    nanodrive.close()
    
