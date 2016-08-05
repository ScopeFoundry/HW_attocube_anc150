from __future__ import division, print_function
from collections import OrderedDict
from astropy.utils.compat._funcsigs import signature

h_fname = "Original Files/NiFpga_CountertoDAC.h"

def split_on_caps(input_string):
    _list = [x for x in input_string]
    for char in _list:
        if char.isupper():
            _list[_list.index(char)] = " " + char

    return ''.join(_list).strip().split(' ')


consts_dict = OrderedDict()


with open(h_fname) as h_file:
    
    for line in h_file:
        if "=" in line and "NiFpga" and (not line.startswith(' *')):
            a, b= line.split("=")
            #print(line.startswith('*'))
            const_name = a.strip().split()[-1]
            const_val  = b.strip(', \n')
            
            consts_dict[const_name] = const_val
    
    for const_name, const_val in consts_dict:
        if 'Signature' in const_name:
            signature = 

    
            if "_" in const_name:
                x = const_name.split("_")
                print(x)
                
                assert x[0] == 'NiFpga'
                vi_name = x[1]
                ctrl_type = x[2]                
                ctrl_name = x[-1]
                
                
                'Indicator', 'Control'
                'I16', 'U16', 'I32', 'U32', 'Bool'
                
                
                #print(split_on_caps(ctrl_type))
                
                #data_type
                
                
                
            #print(const_name)
            print(const_val)
            
        
print("="*80)
print(consts_dict)
            
