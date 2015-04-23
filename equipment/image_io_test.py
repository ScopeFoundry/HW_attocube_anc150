'''
Created on Feb 12, 2015

@author: NIuser
'''
from image_io import ChannelInfo
from image_io import Collection
import numpy as np
 
 
# channel_info1=ChannelInfo('random',(3,3))
# channel_info2=ChannelInfo('zeros',(5,5))
# ch_infos=[channel_info1,channel_info2]
# print(ch_infos)
     
test_collection=Collection(name='test_collection',
                           create=False,
                           initial_size=100,
                           expansion_size=100, 
                           channel_infos=ch_infos)
# print(test_collection)
#       
# for i in range(950):
#     ch1=np.random.rand(3,3)
#     ch2=np.zeros((5,5))
#     frames={'random':ch1,'zeros':ch2}
#     test_collection.update(frames)