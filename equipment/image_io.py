import h5py
import numpy as np

class ChannelInfo(object):
    
    def __init__(self,
                 name='channel0',
                 dimension=(3,3),
                 dtype=np.float,
                 unit=''):
        self.name=name
        self.dimension=dimension
        self.dtype=dtype
        self.unit=unit
        
class Channel(object):
    '''
    Channel class holds all the channel information,
    as well as link to the the channel data
    '''
    def __init__(self,
                 channel_info,
                 data_group,
                 initial_size=100):
         
        self.name=channel_info.name
        self.dimension=channel_info.dimension
        self.dtype=channel_info.dtype
        self.unit=channel_info.unit
        self.data_group=data_group
        self.size=initial_size
        self.setup()
         
    def setup(self):
        self.data=self.data_group.create_dataset(self.name,
                                                (self.size,)+self.dimension,
                                                maxshape=(None,)+self.dimension,
                                                dtype=self.dtype)
             
    def resize(self,size):
        self.size=size
        self.data.resize(self.size,0)
     
    def add_frame(self,counter,frame):
        self.data[counter]=frame        
 
     
 
class Collection(object):
    '''
    Collection object handle the data storage of a scan
    it store all the attributes in a 
    '''
 
    def __init__(self,
                 name='collection0',
                 create=True,
                 initial_size=100,
                 expansion_size=100, 
                 channel_infos=[ChannelInfo(),]):
        if create:
            self.name=name
            self.initial_size=initial_size
            self.expansion_size=expansion_size
            self.size=self.initial_size
             
            self.create()
            self.setup_main_group()
            self.counter=0
             
            '''
            create a list and setup the channels
            '''
            self.channel_infos=channel_infos
            self.setup_channels(self.channel_infos)
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
         
     
    def setup_channels(self,channel_infos=[ChannelInfo()]):
        '''
        create a list of channels and set them up
        '''
        self.channels=list()
         
        '''
        for all channel listed in channel_infos,
        create a channel object and add it to the channel list
        '''
        for channel_info in channel_infos:
            self.channels.append(Channel(channel_info,
                                         data_group=self.data_group,
                                         initial_size=self.initial_size))
   
    def add_frames(self,counter,frames):
        '''
        read frames from input and write them
        into the dataset of each channel
        frame is a dictionary
        '''
        #check to see if counter have reached the size of arrays
        if self.counter>=self.size:
            self.expand()
             
        for channel in self.channels:
            channel.add_frame(self.counter,frames[channel.name])
             
        #increase the count by 1    
        self.counter+=1
         
    def update(self,frames):
        self.add_frames(self.counter,frames)
                    
    def expand(self):
        '''
        increase the size of collection datasets by expansion_size,
        iterate through all channels
        '''
        self.size+=self.expansion_size
        for channel in self.channels:
            channel.resize(self.size)
 
if __name__=='main':
    print('Start testing:')