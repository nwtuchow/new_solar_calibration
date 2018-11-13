#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 21:11:46 2018

Plot sound speed difference

@author: nxt5109
"""
import numpy as np
import mesa_reader as mr
from scipy.interpolate import interp1d

def load_solar_cs_data(SOLAR_SOUND_DATA_LOC="/data/nxt5109/mesa-r10398/data/star_data/solar_csound.data"):
    sound_array= np.loadtxt(SOLAR_SOUND_DATA_LOC,skiprows=11)
    return sound_array

model_output_loc ="LOGS/finalProfile_SSM.data"
sound_array=load_solar_cs_data()

data_r = sound_array[:,0]
data_cs = sound_array[:,2]
data_width = sound_array[:,6]

npts= len(data_cs)
    
last_prof= mr.MesaData(model_output_loc)
model_cs = last_prof.csound
model_r = last_prof.radius #appears ordered outmost to inmost
dq = last_prof.dq

nz=len(model_cs)
calc_rms_f= np.empty(nz)

for k in range(0,nz):
    if k==0:
        calc_rms_f[k]= model_cs[k]
    else:
        calc_rms_f[k]= (model_cs[k]*dq[k-1] + model_cs[k-1]*dq[k])/(dq[k-1]+dq[k])
        
f_cs =interp1d(model_r,model_cs,kind='cubic')

new_cs = f_cs(data_r)

deltacs= (new_cs - data_cs)/data_cs

import matplotlib.pyplot as plt

fig, ax =plt.subplots(1)
ax.plot(data_r,deltacs)
ax.set_xlabel("r/Rsun")
ax.set_ylabel(r"$\delta c_s /c_s$")
fig.savefig("cs_difference.png")

fig2, ax2 =plt.subplots(1)
ax2.plot(data_r,data_cs, label="Solar Data")
ax2.plot(model_r,model_cs,label="model")
ax2.set_xlabel("r")
ax2.set_ylabel("c_s")
ax2.legend()
fig2.savefig("cs_profile.png")
