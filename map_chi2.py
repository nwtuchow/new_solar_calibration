#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 15:55:58 2018

map chi2 
@author: nxt5109
"""
import psutil
import os
from mesa_utils import *
from solar_chi2 import *
import mesa_reader as mr
import numpy as np

def PMS_inlist_args(inlist, model_name ,model_age=1439174.1, save_model=True):
    inlist.dict['create_pre_main_sequence_model']='.true.'
    inlist.dict['load_saved_model']='.false.'
    
    if save_model and model_name!='':
        inlist.dict['save_model_when_terminate']='.true.'
        inlist.dict['save_model_filename'] = "'" +model_name +"'"
    else:
        inlist.dict['save_model_when_terminate']='.false.'
    
    inlist.dict['max_age']=e_to_d(str(model_age))
    inlist.dict['which_atm_option']="'simple_photosphere'"

def evolve_inlist_args(inlist,model_name, age=4.61e9):
    inlist.dict['create_pre_main_sequence_model']='.false.'
    inlist.dict['load_saved_model']='.true.'
    inlist.dict['saved_model_name']= "'" +model_name +"'"
    inlist.dict['save_model_when_terminate']='.false.'
    inlist.dict['max_age']=e_to_d(str(age))
    inlist.dict['which_atm_option']="'photosphere_tables'"
    

ismade=False
targets_set =False
num_cores=16

pcurrent = psutil.Process()
cpid=pcurrent.pid
cwd=os.getcwd()

cploc=cwd + "/models/SSM_test"
workdir=new_work(cpid,cploc,cwd=cwd)

solar_inlist_loc= workdir +"/inlist_1msun"
solar_inlist= mesa_inlist(fname=solar_inlist_loc)
solar_inlist.read()
#use same inlist for all runs



first_FeH = 0.099883042891420248e0
first_Y = 0.27910526985061124e0
first_alpha = 1.9033976646700377e0
first_f_ov = 0.018473664849956072


#first generate premain sequence model to load
model_name= "test_chi2.mod"

PMS_inlist_args(solar_inlist,model_name)
inlist_convert(solar_inlist, first_FeH, first_Y, first_alpha, first_f_ov)

log_dir= workdir+"/LOGS"
prof_name=log_dir+"/Profile_init.data"
hist_name="history_init.data"

ismade=make_mesa(workdir,OMP_NUM_THREADS=num_cores)
out_init= run_mesa(solar_inlist,workdir,OMP_NUM_THREADS=num_cores,made=ismade,
                   last_profile=prof_name, hist_name =hist_name, log_dir=log_dir,
                   use_hist=True)

#get chi2 ready
targets_set=set_targets() #doesn't appear to work
sound_data= load_solar_cs_data()

#change inlist to be for evolving star past PMS
evolve_inlist_args(solar_inlist,model_name)

ntest=20
f_ov_arr= np.linspace(0.01,0.025,ntest)
chi2_arr = np.empty(ntest)

for i in range(0,ntest):
    print("f_ov = %.3f" % f_ov_arr[i])
    prof_name=log_dir + "/Profile_%d.data" % i
    hist_name="history_%d.data" % i
    inlist_convert(solar_inlist, first_FeH, first_Y, first_alpha, f_ov_arr[i])
    
    outputs= run_mesa(solar_inlist,workdir,OMP_NUM_THREADS=num_cores,made=ismade,
                   last_profile=prof_name, hist_name =hist_name, log_dir=log_dir,
                   use_hist=True)
    profile=outputs[0]
    hist=outputs[1]
    chi2= tot_chi_squared(profile,hist,sound_data)
    print("Chi squared = %.2f" % chi2)
    chi2_arr[i]=chi2
    
import matplotlib.pyplot as plt
fig, ax =plt.subplots(1)
ax.plot(f_ov_arr,chi2_arr)
ax.set_xlabel("f_ov")
ax.set_ylabel(r"$\chi ^2$")
fig.savefig("f_ov_chi2.png")    
    