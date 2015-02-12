import h5py
import numpy as np

class ChannelInfo(object):
    def __init__(self,
                 name='channel0',
                 dimension=(1024,1024),
                 dtype=np.float,
                 unit=''):
        self.name=name
        self.dimension=dimension
        self.dtype=dtype
        self.unit=unit

class Collection(object):
    '''
    Collection object handle the data storage of a scan
    it store all the attributes in a 
    '''

    def __init__(self,
                 name='collection0',
                 create=True,
                 initial_size=1000,
                 expansion_size=1000, 
                 channel_info=[ChannelInfo()]):
        if create:
            self.name=name
            self.initial_size=initial_size
            self.expansion_size=expansion_size
            self.size=self.initial_size
            self.channel_info=channel_info
        else:
            pass
        
    def create(self):
        try:
            self.file=h5py.File(self.name+'.hdf5','w')
        except:
            raise IOError('The file name already exist, please choose a new name')
            
    def close(self):
        self.file.close()
        
    def setup_main_group(self):
        self.measurement=self.file.create_group('measurement')
        self.hardware=self.file.create_group('hardware')
        self.data_group=self.file.create_group('data_group')
        
    
    def setup_channel(self,cannel_info=ChannelInfo()):
        '''
        create a new channel in the data_group
        '''
    
    def create_channel(self,channel_info=ChannelInfo()): 
        '''
        DummyHolder for class Channel
        '''
        parent=self
        
        class Channel(object):
        
            def __init__(self,channel_info=ChannelInfo()):
                self.name=channel_info.name
                self.dimension=channel_info.dimension
                self.dtype=channel_info.dtype
                self.unit=channel_info.unit
                self.parent=parent
                
        
            def setup(self):
                pass
             
          
    def link(self,group,counter,data):
        self.group=group
        self.counter=counter
        self.data=data
        
    def data_unlinked(self):
        if self.data==None:
            return True
        else:
            return False
        
    def counter_unlinked(self):
        if self.counter==None:
            return True
        else:
            return False
    
    def group_unlinked(self):
        if self.counter==None:
            return True
        else:
            return False
    
    def add_frame(self,frame,count=None):
        if count==None:
            count=len
