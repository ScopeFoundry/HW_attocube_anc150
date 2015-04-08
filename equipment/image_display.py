'''
Created on Apr 7, 2015

@author: Hao Wu
'''
import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore,QtGui


class ImageData(object):
    
    def __init__(self,sync_object, ai_chans,ai_names,ctr_chans,ctr_names,num_pixels,image_shape,sample_per_point=1,timeout=10):
        self._sync_object=sync_object
        self._ai_chans=ai_chans.split(',')
        self._ai_names=ai_names.split(',')
        self._ctr_chans=ctr_chans.split(',')
        self._ctr_names=ctr_names.split(',')
        self._ai_nums=len(self._ai_chans)
        self._ctr_nums=len(self._ctr_chans)
        self._num_pixels=num_pixels
        self._image_shape=image_shape
        self._sample_per_point=sample_per_point
        self._timeout=timeout
        #add check length maybe
        
        self._images=dict()
        self._lookup_table=dict()
        
        self.setup()
        
    def setup(self):
        for i in xrange(self._ai_nums):
            self._lookup_table[self._ai_names[i]]=self._ai_chans[i]
        for i in xrange(self._ctr_nums):
            self._lookup_table[self._ctr_names[i]]=self._ctr_chans[i]
            
    def read_all(self):
        self.read_ai()
        self.read_ctr()
        self.crunch_all()

    def crunch_all(self):
        for name in self._images:
            self._images[name]=self.crunch(self._images[name])
    
    def crunch(self,data):
        if self._sample_per_point>1:
            print(self._sample_per_point)
            data=data.reshape(self._num_pixels,self._sample_per_point)
            data=data.mean(axis=1)
        data=data.reshape(self._image_shape)
        return data
    
    def read_ai(self):
        self._adc_data=self._sync_object.read_adc_buffer(timeout=self._timeout)
        for i in xrange(self._ai_nums):
            self._images[self._ai_chans[i]]=self._adc_data[i::self._ai_nums]
        
    def read_ctr(self):
        for i in xrange(self._ctr_nums):
            self._images[self._ctr_chans[i]]=self._sync_object.read_ctr_buffer_diff(i,timeout=self._timeout)
    
    def get_by_chan(self,chan):
        return self._images[chan]

    def get_by_name(self,name):
        return self._images[self._lookup_table[name]]
    
class ImageDisplay(object):
    
    def __init__(self,name,widget):
        self._name=name
        self._widget=widget
        '''
        Weave will significantly increase the loading time
        '''
        pg.setConfigOptions(useWeave=False)
        self.viewer=pg.ImageView(name=self._name)
        self.viewer.view.setMouseEnabled(x=False,y=False)
        widget.layout().addWidget(self.viewer)
        print 'setting up new image display'
        self.presetup()
        
    def load(self,data):
        self.viewer.setImage(data,autoRange=False)
        self.viewer.view.disableAutoRange()
        self.viewer.view.setXRange(0,128)
        self.viewer.view.setYRange(0,128)
        
    def presetup(self):
        test_np=np.random.rand(1,1)
        self.load(test_np)
        
class ImageWindow(QtGui.QWidget):
    
    def __init__(self,title):
        super(ImageWindow,self).__init__()
        self._title=title
        
        self.initWindow()
        
    def initWindow(self):
        self.setGeometry(300,300,250,150)
        self.setWindowTitle(self._title)
        self.show()