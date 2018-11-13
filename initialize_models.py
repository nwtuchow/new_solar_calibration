#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 20:16:00 2018

initialize models from premain sequence

@author: nxt5109
"""
import psutil
import os
from mesa_utils import *
import mesa_reader as mr
import numpy as np
from solar_chi2 import tot_chi_squared, load_solar_cs_data

ismade=False
num_cores=16

#give current python instance's pid as an int
pcurrent = psutil.Process()
cpid=pcurrent.pid
cwd=os.getcwd()

workdir= cwd + "/models/SSM_test"

top_inlist_loc= workdir + "/inlist"
top_inlist=mesa_inlist(fname=top_inlist_loc)
top_inlist.read()

solar_inlist_loc= workdir +"/inlist_1msun"
solar_inlist= mesa_inlist(fname=solar_inlist_loc)
solar_inlist.read()

init_inlist_loc= workdir +"/inlist_init"
init_inlist = mesa_inlist(fname=init_inlist_loc)
init_inlist.read()

old_model=mr.MesaData(workdir+"/solar_calibration_input.mod")
model_age= old_model.star_age #1439174.0950849247

solar_inlist.dict['log_directory']= "'"+cwd+"/LOGS"+"'"


#do premain sequence with different arguments
solar_inlist.dict['create_pre_main_sequence_model']='.true.'
solar_inlist.dict['load_saved_model']='.false.'
solar_inlist.dict['save_model_when_terminate']='.true.'
save_name="init_1Msun.mod"
solar_inlist.dict['save_model_filename'] = "'" +save_name +"'"
solar_inlist.dict['max_age']=e_to_d(str(model_age))
solar_inlist.dict['which_atm_option']="'simple_photosphere'"


solar_inlist.dict['star_history_name']= "'history_init.data'"

lastprofname= cwd + "/LOGS/Profile_init.data"
solar_inlist.dict['filename_for_profile_when_terminate']= "'" + lastprofname + "'"

ismade=make_mesa(workdir,OMP_NUM_THREADS=num_cores)
p_init=run_mesa(solar_inlist,workdir,OMP_NUM_THREADS=num_cores,made=ismade)
h_init= mr.MesaData('LOGS/history_init.data')
new_model=mr.MesaData(workdir + '/'+ save_name)
#do normal evolution
solar_age = 4.61e9 

solar_inlist.dict['create_pre_main_sequence_model']='.false.'
solar_inlist.dict['load_saved_model']='.true.'
solar_inlist.dict['saved_model_name']= "'" +save_name +"'"
solar_inlist.dict['save_model_when_terminate']='.false.'
solar_inlist.dict['max_age']=e_to_d(str(solar_age))
solar_inlist.dict['which_atm_option']="'photosphere_tables'"

solar_inlist.dict['star_history_name']= "'historySSM2.data'"
lastprofname= cwd + "/LOGS/ProfileSSM2.data"
solar_inlist.dict['filename_for_profile_when_terminate']= "'" + lastprofname + "'"

p_out=run_mesa(solar_inlist,workdir,OMP_NUM_THREADS=num_cores,made=ismade)
hist_out= mr.MesaData("LOGS/historySSM2.data")

#previous profiles and histories loading from old model file
p_prev= mr.MesaData("LOGS/finalProfile_SSM.data")
hist_prev = mr.MesaData("LOGS/historySSM.data")

sound_data= load_solar_cs_data()

import matplotlib.pyplot as plt
fig, ax =plt.subplots(1)
ax.plot(hist_prev.star_age,hist_prev.log_L, label ='loading old model file')
ax.plot(hist_out.star_age, hist_out.log_L, label = 'loading new model file')
ax.set_xlabel("Age")
ax.set_ylabel("log(L)")
ax.legend()
fig.savefig("modelfile_logL_compare.png")

fig2, ax2= plt.subplots(1)
ax2.plot(hist_prev.star_age, hist_prev.Teff, label ='loading old model file')
ax2.plot(hist_out.star_age, hist_out.Teff, label ='loading new model file')
ax2.set_xlabel("Age")
ax2.set_ylabel("T_eff")
ax2.legend()
fig2.savefig("modelfile_Teff_compare.png")