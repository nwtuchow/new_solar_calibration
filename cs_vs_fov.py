#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 16:02:52 2018

@author: nxt5109
"""

from mesa_wrapper import mesa_wrapper
from solar_chi2 import *
import mesa_reader as mr
import numpy as np
import sys
import pickle
import os

cwd=os.getcwd()
logdir=cwd +"/LOGS/f_ov_vs_cs"

num_cores=15

ntest=10
f_ov_arr= np.linspace(0.0175, 0.0205,ntest)

in_dict={} #all fields must be same dimensions

dict_keys=["f_ov","init_Y","init_FeH","alpha",]
for key in dict_keys:
    in_dict[key]=np.empty(ntest)

for i in range(0,ntest):
    in_dict["f_ov"][i]= f_ov_arr[i]
    in_dict["init_Y"][i]=0.27910526985061124e0
    in_dict["init_FeH"][i]=0.099883042891420248e0
    in_dict["alpha"][i]=1.9033976646700377e0

out_data=mesa_wrapper(in_dict,num_cores=num_cores,log_dir=logdir,
                      model_name="test_chi2.mod",keepcs=True)

savename="outputs/cs_vs_f_ov_data.pkl"

with open(savename, 'wb') as out_file:
    pickle.dump(out_data,out_file)


sound_array = load_solar_cs_data()

min_R = 0.094
max_R = 0.94

data_r = sound_array[:,0]
data_cs = sound_array[:,2]
#data_width = sound_array[:,6]

npts= len(data_cs)
    
    

profiles=[]
out_data['r']=[]
out_data['new_cs']=[]
out_data['delta_cs']=[]
#hists=[]
for j in range(0,ntest):
    prof_loc= logdir +"/Profile_%d.data" % j
    profile=mr.MesaData(prof_loc)
    profiles.append(profile)
    #hist_loc=logdir +"/history_%d.data" % j
    #hist=mr.MesaData(hist_loc)
    #hists.append(hist)
    model_cs = profile.csound
    model_r = profile.radius #appears ordered outmost to inmost
    dq = profile.dq

    nz=len(model_cs)
    calc_rms_f= np.empty(nz)
    
    for k in range(0,nz):
        if k==0:
            calc_rms_f[k]= model_cs[k]
        else:
            calc_rms_f[k]= (model_cs[k]*dq[k-1] + model_cs[k-1]*dq[k])/(dq[k-1]+dq[k])
    
    f_cs =interp1d(model_r,calc_rms_f,kind='cubic')

    new_cs = f_cs(data_r) #model cs value corresponding to data
    
    out_data['r'].append(data_r)
    out_data['new_cs'].append(new_cs)
    
    delta_cs= (new_cs-data_cs)/data_cs
    out_data['delta_cs'].append(delta_cs)

prevR=0
start_ind=0
end_ind=len(data_r)-1
for q in range(0,len(data_r)):
    if data_r[q] > min_R and prevR< min_R:
        start_ind=q
    if data_r[q]> max_R and prevR< max_R:
        end_ind=q-1
    prevR=data_r[q]
        

    

import matplotlib.pyplot as plt

fig, ax =plt.subplots(1)

for l in range(0,ntest):
    ltext= "f_ov=%.4f  RMS=%.5f" % (out_data["f_ov"][l], out_data["cs_rms"][l])
    ax.plot(out_data['r'][l][start_ind:end_ind],out_data['delta_cs'][l][start_ind:end_ind], label=ltext)

ax.set_xlabel("R")
ax.set_ylabel(r"$\delta c_s$")
ax.legend()
ax.savefig("f_ov_effect_on_cs.png")
