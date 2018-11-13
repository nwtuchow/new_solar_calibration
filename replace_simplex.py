#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 17:03:45 2018

Code figuring out how to supplant the arguments in the simplex_solar module

@author: nxt5109
"""

import psutil
import os
from mesa_utils import *
import mesa_reader as mr
import numpy as np

#convert quantities from simplex solar inlist to mesa star
def inlist_convert(inlist, FeH, Y, alpha, f_ov, Y_depends_on_Z=False, Y0=0.248, 
                        dYdZ=1.4, f0_ov_div_f_ov= 1, Z_div_X_solar = 0.02293e0):
    inlist.dict['mixing_length_alpha'] = e_to_d(str(alpha))
    initial_Y=Y
    Y_frac_he3 = 1e-4
    initial_Z_div_X = Z_div_X_solar * pow(10,FeH)
    if Y_depends_on_Z:
        a = initial_Z_div_X
        b = dYdZ
        c= 1e0 +a * (1e0 + b)
        X= (1e0 - Y0)/c
        Y = (Y0 + a*(b + Y0))/c
        Z = 1e0 - (X + Y)
    else:
        Y=initial_Y
        X = (1e0 - Y)/(1e0 + initial_Z_div_X)
        Z = X*initial_Z_div_X
    
    initial_he3= Y_frac_he3*Y
    initial_he4= Y - initial_he3
    
    inlist.dict['initial_z']= e_to_d(str(Z))  
    inlist.dict['initial_h1']=e_to_d(str(X))
    inlist.dict['initial_h2']="0"
    inlist.dict['initial_he3']=e_to_d(str(initial_he3))
    inlist.dict['initial_he4']=e_to_d(str(initial_he4))
    
    f0_ov=f0_ov_div_f_ov*f_ov
    
    inlist.dict['overshoot_f_above_nonburn_core']=e_to_d(str(f_ov))
    inlist.dict['overshoot_f_above_nonburn_shell']=e_to_d(str(f_ov))
    inlist.dict['overshoot_f_below_nonburn_shell']=e_to_d(str(f_ov))
    
    inlist.dict['overshoot_f_above_burn_h_core']=e_to_d(str(f_ov))
    inlist.dict['overshoot_f_above_burn_h_shell']=e_to_d(str(f_ov))
    inlist.dict['overshoot_f_below_burn_h_shell']=e_to_d(str(f_ov))

    inlist.dict['overshoot_f_above_burn_he_core']=e_to_d(str(f_ov))
    inlist.dict['overshoot_f_above_burn_he_shell']=e_to_d(str(f_ov))
    inlist.dict['overshoot_f_below_burn_he_shell']=e_to_d(str(f_ov))

    inlist.dict['overshoot_f_above_burn_z_core']=e_to_d(str(f_ov))
    inlist.dict['overshoot_f_above_burn_z_shell']=e_to_d(str(f_ov))
    inlist.dict['overshoot_f_below_burn_z_shell']=e_to_d(str(f_ov)) 
    
    inlist.dict['overshoot_f0_above_nonburn_core']=e_to_d(str(f0_ov))
    inlist.dict['overshoot_f0_above_nonburn_shell']=e_to_d(str(f0_ov))
    inlist.dict['overshoot_f0_below_nonburn_shell']=e_to_d(str(f0_ov))
    
    inlist.dict['overshoot_f0_above_burn_h_core']=e_to_d(str(f0_ov))
    inlist.dict['overshoot_f0_above_burn_h_shell']=e_to_d(str(f0_ov))
    inlist.dict['overshoot_f0_below_burn_h_shell']=e_to_d(str(f0_ov))
    
    inlist.dict['overshoot_f0_above_burn_he_core']=e_to_d(str(f0_ov))
    inlist.dict['overshoot_f0_above_burn_he_shell']=e_to_d(str(f0_ov))
    inlist.dict['overshoot_f0_below_burn_he_shell']=e_to_d(str(f0_ov))
    
    inlist.dict['overshoot_f0_above_burn_z_core']=e_to_d(str(f0_ov))
    inlist.dict['overshoot_f0_above_burn_z_shell']=e_to_d(str(f0_ov))
    inlist.dict['overshoot_f0_below_burn_z_shell']=e_to_d(str(f0_ov))
    

    
    

ORIGINAL_SOLAR="/home/nxt5109/Dropbox/Faint_Young_Sun_Abundances/MESA_modeling/models/1msun_model"
ismade=False
num_cores=16

#give current python instance's pid as an int
pcurrent = psutil.Process()
cpid=pcurrent.pid
cwd=os.getcwd()

workdir= cwd + "/models/SSM_test"

inlistname = workdir +"/inlist_1msun"
solar_inlist= mesa_inlist(fname=inlistname)
solar_inlist.read()
solar_inlist.dict['log_directory']= "'"+cwd+"/LOGS"+"'"

hist_name= 'historySSM.data'
solar_inlist.dict['star_history_name']= "'"+hist_name+"'"

solar_inlist.dict['history_interval']="10"

first_FeH = 0.099883042891420248e0
first_Y = 0.27910526985061124e0
first_alpha = 1.9033976646700377e0
first_f_ov = 0.018473664849956072       

inlist_convert(solar_inlist,first_FeH,first_Y,first_alpha,first_f_ov)

solar_inlist.write()

lastprofname= cwd + "/LOGS/finalProfile_SSM.data"
ismade=make_mesa(workdir,OMP_NUM_THREADS=num_cores)
pout=run_mesa(solar_inlist,workdir,OMP_NUM_THREADS=num_cores,
              last_profile=lastprofname,made=ismade)
hist_name= cwd+ "/LOGS/"+hist_name
histout=mr.MesaData(hist_name)
#tf=histout.elapsed_time[-1]
log_L_out=histout.log_L
age_out = histout.star_age

hist_true_name = cwd + "/LOGS/historyTrueSSM.data"
hist_true =mr.MesaData(hist_true_name)

log_L_true=hist_true.log_L
age_true= hist_true.star_age

import matplotlib.pyplot as plt

fig, ax =plt.subplots(1)
ax.plot(age_out,log_L_out, label="Without simplex module")
ax.plot(age_true, log_L_true, label = "MESA Example")
ax.set_xlabel("Age")
ax.set_ylabel("log(L)")
ax.legend()
fig.savefig("logL_compare.png")

logTeff_out=histout.log_Teff
logTeff_true=hist_true.log_Teff

fig2, ax2= plt.subplots(1)
ax2.plot(age_out,logTeff_out, label="Without simplex module")
ax2.plot(age_true, logTeff_true, label = "MESA Example")
ax2.set_xlabel("Age")
ax2.set_ylabel("log(T_eff)")
ax2.legend()
fig2.savefig("logTeff_compare.png")