'''
Created on Oct 13, 2015

@author: Zach
'''

import win32com.client

#-------------------------------------------------------------------------------
class ScopeWrapper(object):
    #---------------------------------------------------------------------------
    def __init__(self,debug=False,mode='STEM'):
        
        self.debug                  = True    
        self.Scope                  = None
        self.Acq                    = None
        self.Cam                    = None
        self.Det                    = None
        
    #---------------------------------------------------------------------------
    def Connect(self):
        self.Scope = win32com.client.gencache.EnsureDispatch('TEMScripting.Instrument')
        if self.debug: print("Connected to microscope")
        self.TIA = win32com.client.Dispatch("ESVision.Application")
        if self.debug: print("Connected to TIA")  
        self.Acq = self.Scope.Acquisition
        self.Proj = self.Scope.Projection
        self.Ill = self.Scope.Illumination      

        self.ACQIMAGECORRECTION_DEFAULT         = win32com.client.constants.AcqImageCorrection_Default
        self.ACQIMAGECORRECTION_UNPROCESSED     = win32com.client.constants.AcqImageCorrection_Unprocessed
        
        self.ACQIMAGESIZE_FULL                  = win32com.client.constants.AcqImageSize_Full
        self.ACQIMAGESIZE_HALF                  = win32com.client.constants.AcqImageSize_Half
        self.ACQIMAGESIZE_QUARTER               = win32com.client.constants.AcqImageSize_Quarter
        
        self.ACQIMAGEFILEFORMAT_TIFF            = win32com.client.constants.AcqImageFileFormat_TIFF
        self.ACQIMAGEFILEFORMAT_JPG             = win32com.client.constants.AcqImageFileFormat_JPG
        self.ACQIMAGEFILEFORMAT_PNG             = win32com.client.constants.AcqImageFileFormat_PNG


    #---------------------------------------------------------------------------
    def TEMMODE(self):
        self.Acq.RemoveAllAcqDevices()
        self.Cam = self.m_acqusition.Cameras[0]
        self.Acq.AddAcqDevice(self.Cam)
        if self.debug: print("Scope is TEM Mode")  
    
    #---------------------------------------------------------------------------
    def STEMMODE(self):
        self.Acq.RemoveAllAcqDevices()
        self.Det = self.Acq.Detectors(0)
        self.Acq.AddAcqDevice(self.Det)
        if self.debug: print("Scope is STEM Mode")  
    
    #---------------------------------------------------------------------------
    