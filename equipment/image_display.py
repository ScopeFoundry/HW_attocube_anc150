'''
Created on Apr 7, 2015

@author: Hao Wu
'''
import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph import functions as fn
from PySide import QtCore, QtGui, QtUiTools
    
class CallBackBuffer(object):
    def __init__(self,image,parent,name='',xpix=512,ypix=512,xview=512,yview=512,sample_per_point=10,is_counter=True,unit='count',sample_rate=2000000,mode='line',collection=''):
        self.counter=0
        self.name=name
        self.xpix=xpix
        self.ypix=ypix
        self.xview=xview
        self.yview=yview
        self.xdelta=self.xpix-self.xview
        self.ydelta=self.ypix-self.yview
        self.sample_per_point=sample_per_point
        self.parent=parent
        self.is_counter=is_counter
        self.unit=unit
        self.finished=False
        self.sample_rate=sample_rate
        self.last_count=0 #for storing input array's last count to calculate difference
        self.image=image
        self.mode=mode
        self.collection=collection
    def load(self,input_array):
        if self.is_counter:
                input_array=np.insert(input_array,0,self.last_count)
                self.last_count=input_array[input_array.size-1]
                input_array=np.diff(input_array)
                if self.counter==0:
                    input_array[0]=0
        
                     
        
                
        if self.mode=="block":
            input_array=input_array.reshape(self.xpix*self.ypix,self.sample_per_point)
            input_array=input_array.mean(axis=1)
            if self.is_counter:
                if self.unit=='count':
                    input_array=np.multiply(input_array,self.sample_per_point)
                elif self.unit=='Hz':
                    input_array=np.multiply(input_array,self.sample_rate)  
            input_array=input_array.reshape(self.xpix,self.ypix)
            self.image[:,:]=input_array[0:self.yview,self.xdelta:self.xpix]
            self.collection.update_independent_frame(self.name,self.image)
        else:
            input_array=input_array.reshape(self.xpix,self.sample_per_point)
            input_array=input_array.mean(axis=1)
            if self.is_counter:
                if self.unit=='count':
                    input_array=np.multiply(input_array,self.sample_per_point)
                elif self.unit=='Hz':
                    input_array=np.multiply(input_array,self.sample_rate)          
            if self.counter<0:
                self.counter+=1
            elif self.counter>=0 and self.counter<self.yview:
                self.image[:][self.counter]=input_array[self.xdelta:]
                self.counter+=1
                self.parent.progress=1.0*self.counter/self.yview
            else:
                self.counter+=1
                self.finished=True
                self.parent.finished=True
                
            
    def display(self):
        return self.image
    
class AICallBackSpliter(object):
    
    def __init__(self,chan_num=1,buff_list=[]):
        self.chan_num=chan_num
        self.buff_list=buff_list
        
    def load(self,input_array):
        if self.chan_num>1:
            for i in xrange(self.chan_num):
                self.buff_list[i].load(input_array[i::self.chan_num])
        else:
                self.buff_list[0].load(input_array)
        
    def display(self):
        return self.image
         
class SetWindowROI(pg.ROI):
    
    def __init__(self,*args, **kwargs):
        super(SetWindowROI,self).__init__(*args, **kwargs)
    

class hao_scale(pg.ScaleBar):
    parent2=None
    def __init__(self, *args, **kwargs):
        super(hao_scale, self).__init__(*args, **kwargs)


    def setParentItem(self, parent):
        self.parent2=parent
        self.pcene=parent.scene()
        self.pcene.addItem(self)

    def parentItem(self):
        return self.parent2

    def remove(self):
        self.pcene.removeItem(self)
        
class ImageData(object):
    
    def __init__(self,sync_object, ai_chans,ai_names,ctr_chans,ctr_names,
                 num_pixels,image_shape,sample_per_point=1,xpix=512,ypix=512,xview=512,yview=512,
                 timeout=10,mode='regular',counter_unit='count',sample_rate=2000000,collection=''):
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
        self._xpix=xpix
        self._ypix=ypix
        self._xview=xview
        self._yview=yview
        self._xdelta=self._xpix-self._xview
        self._ydelta=self._ypix-self._yview
        self._timeout=timeout
        self._counter_unit=counter_unit
        self._sample_rate=sample_rate
        self.collection=collection
        #add check length maybe
        
        self._images=dict()
        self._buffers=dict()
        self._lookup_table=dict()
        self.finished=False
        self.progress=0.0
        self.setup()
        
        if mode=='callback':
            self.setup_ai_callback()
            self.setup_ctr_callback()
        elif mode=="block_callback":
            self.setup_ai_callback(mode='block')
            self.setup_ctr_callback(mode='block')
                
    def setup(self):
        for i in xrange(self._ai_nums):
            self._lookup_table[self._ai_names[i]]=self._ai_chans[i]
        for i in xrange(self._ctr_nums):
            self._lookup_table[self._ctr_names[i]]=self._ctr_chans[i]
            
    def read_all(self):
        self.read_ai()
        self.read_ctr()
        self.crunch_all()
        self.crop_all()
        
    def crunch_all(self):
        for name in self._images:
            self._images[name]=self.crunch(self._images[name])
    
    def crunch(self,data):
        if self._sample_per_point>1:
            data=data.reshape(self._num_pixels,self._sample_per_point)
            data=data.mean(axis=1)
        data=data.reshape(self._image_shape)
        return data
    
    def crop_all(self):
        for name in self._images:
            self._images[name]=self.crop(self._images[name])
    
    def crop(self,data):
        new_data=data[0:self._yview,self._xdelta:self._xpix]
        return new_data
    
    def read_ai(self):
        self._adc_data=self._sync_object.read_adc_buffer(timeout=self._timeout)
        for i in xrange(self._ai_nums):
            self._images[self._ai_names[i]]=self._adc_data[i::self._ai_nums]
            
                
    def read_ctr(self):
        for i in xrange(self._ctr_nums):
            data=self._sync_object.read_ctr_buffer_diff(i,timeout=self._timeout)
            if self._counter_unit=='count':
                    data=np.multiply(data,self._sample_per_point)
            elif self._counter_unit=='Hz':
                    data=np.multiply(data,self._sample_rate)
            self._images[self._ctr_names[i]]=data
            
    def setup_ctr_callback(self,mode='line'):
        for i in xrange(self._ctr_nums):
            self._images[self._ctr_names[i]]=np.zeros([self._xview,self._yview])
            self._buffers[self._ctr_names[i]]=CallBackBuffer(self._images[self._ctr_names[i]],
                                                             parent=self,
                                                             name=self._ctr_names[i],
                                                             xpix=self._xpix,
                                                             ypix=self._ypix,
                                                             xview=self._xview,
                                                             yview=self._yview,
                                                             sample_per_point=self._sample_per_point,
                                                             is_counter=True,
                                                             unit=self._counter_unit,
                                                             sample_rate=self._sample_rate,
                                                             mode=mode,collection=self.collection)
            self._sync_object.ctr[i].set_callback(self._buffers[self._ctr_names[i]])
    
    def setup_ai_callback(self,mode='line'):
        self.buff_list=[]
        for i in xrange(self._ai_nums):
            self._images[self._ai_names[i]]=np.zeros([self._xview,self._yview])
            self._buffers[self._ai_names[i]]=CallBackBuffer(self._images[self._ai_names[i]],
                                                             parent=self,
                                                             name=self._ai_names[i],
                                                             xpix=self._xpix,
                                                             ypix=self._ypix,
                                                             xview=self._xview,
                                                             yview=self._yview,
                                                             sample_per_point=self._sample_per_point,
                                                             is_counter=False,
                                                             unit=self._counter_unit,
                                                             sample_rate=self._sample_rate,
                                                             mode=mode,collection=self.collection)
            #self._buffers[self._ai_names[i]]=CallBackBuffer(self._images[self._ai_names[i]],self,self._xpix,self._ypix,self._sample_per_point)
            self.buff_list.append(self._buffers[self._ai_names[i]])
        self.ai_spliter=AICallBackSpliter(self._ai_nums,self.buff_list)
        self._sync_object.adc.set_callback(self.ai_spliter)
 
    def get_by_name(self,name):
        return self.get_by_name_regular(name)
    
    def get_by_name_regular(self,name):
        return self._images[name]
    
    def get_by_name_callback(self,name):
        return self._buffers[name].display()
    
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
        self.scale=hao_scale(size=10,length=10,suffix='m')
        self.scale.setParentItem(self.viewer.view)
        self.scale.anchor((1,1),(1,1),offset=(-40,-20))
        print 'setting up new image display'
        
    def load(self,data,scale_size=10,scale_length=10,scale_suffix='m'):
        self.viewer.setImage(np.fliplr(np.rot90(data,3)))
        self.scale.size=scale_size
        self.scale.length=scale_length
        self.scale.suffix=scale_suffix
        self.scale.text.setText(fn.siFormat(scale_length, suffix=scale_suffix))
        self.scale.updateBar()
        self.histogram=self.viewer.ui.histogram
#         if hasattr(self,'scale'):
#             self.scale.remove()
#         self.scale=hao_scale(size=scale_size,length=scale_length,suffix=scale_suffix)
#        
#        
        
    def presetup(self):
        test_np=np.random.rand(1,1)
        self.load(test_np)
        
    def create_roi(self):
        self.roi=self.viewer.roi()
        self.viewer.roiChanged=self.roiChanged()
        
class ImgWindow(QtGui.QWidget): 
    ui_filename='img_window.ui'
    
    def __init__(self,title='figure0'):
        ui_loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(self.ui_filename)
        ui_file.open(QtCore.QFile.ReadOnly); 
        self.title=title
        self.display_window=QtGui.QWidget()
        self.display_window.ui = ui_loader.load(ui_file)
        self.display_window.ui.setWindowTitle(title)
        self.image_view=ImageDisplay('display window', self.display_window.ui.plot_container)
        self.display_window.ui.show()
        self.ui=self.display_window.ui
        ui_file.close()
                       
class ImageWindow(ImgWindow):
    ui_filename='img_window.ui'
    
    def __init__(self,title='figure0',hist=False):
        super(ImageWindow, self).__init__(title)
        self.image_view.viewer.ui.roiBtn.hide()
        self.image_view.viewer.ui.normBtn.hide()

        if not hist:
            self.histogram=self.image_view.viewer.ui.histogram.item
            self.image_view.viewer.ui.histogram.setMinimumWidth(75)
            self.image_view.viewer.ui.histogram.setFixedWidth(75)
 
            #self.histogram.axis.hide()
            self.histogram.axis.setMaximumWidth(22)
            self.histogram.axis.setWidth(22)
            self.histogram.axis.mouseDragEvent=None
            self.histogram.plot.hide()
            self.histogram.region.hide()
            #self.histogram.layout.removeItem(self.histogram.axis)
            self.histogram.layout.removeItem(self.histogram.vb)
 
            self.histogram.vb.removeItem(self.histogram.plot)
            self.histogram.vb.removeItem(self.histogram.region)
            self.histogram.region.hide()

class SetWindow(ImageWindow):
    ui_filename='set_window.ui'
    
    def __init__(self,gui,title='Set Window'):
        super(SetWindow, self).__init__(title)
        self.gui=gui
        self.scanner=self.gui.sem_raster_scanner
        self.scan=self.gui.sem_raster_scan
        self.scan.progress_reporter.done.connect(self.load_full)
        self.ui.reset_pushButton.clicked.connect(self.reset_load)
        self.ui.load_pushButton.clicked.connect(self.load_current)
        self.ui.set_pushButton.clicked.connect(self.set_region)
        #self.roi=self.image_view.viewer.roi
        #self.roi.setSize(self.scanner.points.val/2)
        self.setup_roi()
        self.reload_flag=False
        
    def setup_roi(self):
        self.vb=self.image_view.viewer.view
        self.roi=pg.ROI([0,0],[self.scanner.points.val*0.5,self.scanner.lines.val*0.5])
        self.vb.addItem(self.roi)
        self.roi.addScaleHandle([1, 1], [0, 0])
        self.roi.sigRegionChanged.connect(self.square_roi)
        
    def square_roi(self): 
        size=self.roi.size()
        x=size[0]
        self.roi.setSize([x,x],update=False, finish=False)
        
    def reset(self):
        self.scanner.xoffset.update_value(0)
        self.scanner.yoffset.update_value(0)
        self.scanner.xsize.update_value(100)
        self.scanner.ysize.update_value(100)
        
    def reset_load(self):
        self.reload_flag=True
        self.reset()
        self.scan.reset_scan()
    
    @QtCore.Slot(bool)
    def load_full(self,done):
        if done and self.reload_flag:
            self.load_current()
            self.reload_flag=False
    
    def load_current(self):
        self.image_view.load(self.scan.images.get_by_name(self.gui.set_window_channel.val),
                             scale_size=self.scanner.points.val*0.2,
                             scale_length=self.scan.scale.get_pixsize_x()*self.scanner.points.val*0.2*(1e-9),
                             scale_suffix='m')
        
    def get_region(self):
        x=self.roi.pos()[0]
        y=self.roi.pos()[1]
        w=self.roi.size()[0]
        d=self.roi.size()[1]
        return x,y,w,d
    
    def set_region(self):
        xs,ys,xo,yo=self.convert_region()
        self.scanner.xsize.update_value(xs)
        self.scanner.ysize.update_value(ys)
        self.scanner.xoffset.update_value(xo)
        self.scanner.yoffset.update_value(yo)
        
    def convert_region(self):
        x,y,w,d=self.get_region()
        xpix=self.scanner.points.val
        ypix=self.scanner.lines.val
        x2=x+w/2
        y2=y+d/2
        
        xs=w/xpix*100.0
        ys=d/ypix*100.0
        xo=(x2/xpix-0.5)*100
        yo=(y2/ypix-0.5)*100
        return xs,ys,xo,yo

        
if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    imw=ImageWindow()
    sys.exit(app.exec_())

