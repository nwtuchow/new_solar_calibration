#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 16:59:11 2018

@author: nxt5109
"""

from mesa_wrapper import mesa_wrapper
import numpy as np
import sys
import pickle
import os


args=sys.argv #arg1: starting index, arg2: ending index
s_ind=int(args[1])
e_ind=int(args[2])

if(s_ind >= e_ind):
    print("Error: Starting index greater than or equal to ending index")
    exit()

ind_range=range(s_ind,e_ind)

cwd=os.getcwd()
logdir=cwd +"/LOGS/f_ov_min1"

num_cores=3

ntest=50
ni=len(ind_range)
f_ov_arr= np.linspace(0.016, 0.021,ntest)
in_dict={} #all fields must be same dimensions

dict_keys=["f_ov","init_Y","init_FeH","alpha",]
for key in dict_keys:
    in_dict[key]=np.empty(ni)

for i in range(0,ni):
    in_dict["f_ov"][i]= f_ov_arr[ind_range[i]]
    in_dict["init_Y"][i]=0.27910526985061124e0
    in_dict["init_FeH"][i]=0.099883042891420248e0
    in_dict["alpha"][i]=1.9033976646700377e0
    
out_data=mesa_wrapper(in_dict,num_cores=num_cores,log_dir=logdir,
                      model_name="test_chi2.mod")

savename="outputs/f_ov_min1_%d_%d.pkl" % (s_ind, e_ind)

with open(savename, 'wb') as out_file:
    pickle.dump(out_data,out_file)
    