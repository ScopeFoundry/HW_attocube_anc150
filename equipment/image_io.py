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
                 initial_size=100,create=True):
        
        self.name=channel_info.name
        self.dimension=channel_info.dimension
        self.dtype=channel_info.dtype
        self.unit=channel_info.unit
        self.data_group=data_group
        self.size=initial_size
        self.new=create
        self.setup()
         
    def setup(self):
        if self.new:
            self.data=self.data_group.create_dataset(self.name,
                                                     (self.size,)+self.dimension,
                                                     maxshape=(None,)+self.dimension,
                                                     dtype=self.dtype)
        else:
            self.data=self.data_group[self.name]
             
    def resize(self,size):
        self.size=size
        self.data.resize(self.size,0)
     
    def add_frame(self,counter,frame):
        self.data[counter]=frame        
 
    def get_frame(self,count):
        return self.data[count]
 
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
        self.name=name
        if create:
            self.new=True
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
            self.new=False
            self.open(self.name)
            self.link_main_group()
            self.channel_infos=list()
            
            '''
            read in channel infos
            '''
            for item in self.data_group.items():
                name,dimension,dtype=self.read_channel_info(item)
                self.channel_infos.append(ChannelInfo(name,dimension,dtype))
            
            '''
            link to channels
            '''
            self.link_channels(self.channel_infos)
            self.end_count=self.read_count()
                
    def create(self):
        try:
            self.file=h5py.File(self.name+'.hdf5','w-')
        except:
            raise IOError('The file name already exist, please choose a new name')
             
    def close(self):
        if self.new:
            self.measurement.attrs['end_count']=self.counter
        self.file.close()
    
    def open(self,name):
        try:
            self.file=h5py.File(self.name+'.hdf5','r')
        except:
            raise IOError('The file cannot be opened!')
        
    def link_main_group(self):
        self.measurement=self.file['measurement']
        self.hardware=self.file['hardware']
        self.data_group=self.file['data_group']
        
    def read_channel_info(self,data_group_item):
        name=data_group_item[0]
        dset=data_group_item[1]
        dimension=dset.shape[1:]
        dtype=dset.dtype
        return name,dimension,dtype
        
    def read_count(self):
        '''
        read the total number of frames
        '''
        return self.measurement.attrs['end_count']
    def setup_main_group(self):
        '''
        There are three groups:
        measurement is for store metadata in the measurement
        component, such as scan rate, pixel sizes, voltage etc.
        
        hardware components is for storing hardware configurations,
        such as EHT, magnification, focus etc.
        
        data_group contains channels and datasets that has the actual
        images or traces of a scan 
        '''
        self.measurement=self.file.create_group('measurement')
        self.hardware=self.file.create_group('hardware')
        self.data_group=self.file.create_group('data_group')
         
    def save_logged_quantities(self,group,logged_quantities):
        for name in logged_quantities:
            group.attrs[name]=logged_quantities[name]
            
    def save_measurement_component(self,vals,units):
        vals_group=self.measurement.create_group('vals')
        units_group=self.measurement.create_group('units')
        self.save_logged_quantities(vals_group,vals)
        self.save_logged_quantities(units_group,units)
        
    def save_hardware_component(self,hardware_name,vals,units):
        hardware_group=self.hardware.create_group(hardware_name)
        vals_group=hardware_group.create_group('vals')
        units_group=hardware_group.create_group('units')
        self.save_logged_quantities(vals_group,vals)
        self.save_logged_quantities(units_group,units)
     
    def setup_channels(self,channel_infos=[ChannelInfo()]):
        '''
        create a list of channels and set them up
        '''
        self.channels=dict()
         
        '''
        for all channel listed in channel_infos,
        create a channel object and add it to the channel list
        '''
        for channel_info in channel_infos:
            self.channels[channel_info.name]=Channel(channel_info,
                                                     data_group=self.data_group,
                                                     initial_size=self.initial_size)
    
    def link_channels(self,channel_infos):
        '''
        create a list of channels and set them up
        '''
        self.channels=dict()
         
        '''
        for all channel listed in channel_infos,
        create a channel object and add it to the channel list
        '''
        for channel_info in channel_infos:
            self.channels[channel_info.name]=Channel(channel_info,
                                                     data_group=self.data_group,
                                                     create=False)
   
    def add_frames(self,counter,frames):
        '''
        read frames from input and write them
        into the dataset of each channel
        frame is a dictionary
        '''
        #check to see if counter have reached the size of arrays
        if self.counter>=self.size:
            self.expand()
             
        for channel_name in self.channels:
            self.channels[channel_name].add_frame(self.counter,frames[channel_name])
             
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
        for channel_name in self.channels:
            self.channels[channel_name].resize(self.size)
 
if __name__=='__main__':
    print('Start testing:')