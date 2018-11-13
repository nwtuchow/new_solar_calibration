#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 15:37:21 2018
parallel chi2

use in script chi2_fov_parallel
@author: nxt5109
"""
#arg1: starting index, arg2: ending index
import sys
import psutil
import os
import pickle
from mesa_utils import *
from solar_chi2 import *
#import mesa_reader as mr
import numpy as np

def serial_run_mesa(inlist_vec,workdir,sound_data, ind_range=[],label='',
                    OMP_NUM_THREADS=16,made=False):
    if ind_range ==[]:
        n_in=len(inlist_vec)
        ind_range = range(0,n_in)
    else:
        n_in = len(ind_range)
        
    chi2_arr = np.empty(n_in)
    
    log_dir= workdir+"/LOGS"
    j=0
    for i in ind_range:
        prof_name=log_dir + "/"+label+"Profile_%d.data" % i
        hist_name=label+"history_%d.data" % i
        outputs= run_mesa(inlist_vec[i],workdir,OMP_NUM_THREADS=OMP_NUM_THREADS,made=made,
                   last_profile=prof_name, hist_name =hist_name, log_dir=log_dir,
                   use_hist=True)
        profile=outputs[0]
        hist=outputs[1]
        chi2= tot_chi_squared_old(profile,hist,sound_data)
        print("Index:",i, "\nChi2:",chi2)
        chi2_arr[j]=chi2
        j+=1
    return chi2_arr

#version with dict output
#keys are keys for chi2 dict
#need to modify to specify model file, which stage of evolution
def serial_run_mesa_dict(inlist_vec,workdir,sound_data, ind_range=[],label='',
                    OMP_NUM_THREADS=16,made=False,
                    keys=["Teff", "log_L","surface_He","Rcz","cs_rms"]):
    if ind_range ==[]:
        n_in=len(inlist_vec)
        ind_range = range(0,n_in)
    else:
        n_in = len(ind_range)
    
    out_keys=['Teff','log_R', 'log_g', 'log_L', 'FeH', 'age', 'surface_Z_div_X',
               'surface_He','Rcz', 'cs_rms']
    
    data_dict={}
    for s1 in keys:
        s1_chi2="chi2_" +s1
        data_dict[s1_chi2]=np.empty(n_in)
    
    data_dict["chi2_tot"]=np.empty(n_in)
    
    for s2 in out_keys:
        data_dict[s2]=np.empty(n_in)
    
    log_dir= workdir+"/LOGS"
    j=0
    for i in ind_range:
        prof_name=log_dir + "/"+label+"Profile_%d.data" % i
        hist_name=label+"history_%d.data" % i
        outputs= run_mesa(inlist_vec[i],workdir,OMP_NUM_THREADS=OMP_NUM_THREADS,made=made,
                   last_profile=prof_name, hist_name =hist_name, log_dir=log_dir,
                   use_hist=True)
        profile=outputs[0]
        hist=outputs[1]
        out_dict=output_convert(profile,hist,sound_data)
        chi2_dict= tot_chi_squared_dict(out_dict)
        for k1 in keys:
            chi2_k1="chi2_"+k1
            data_dict[chi2_k1][j]= chi2_dict[k1]
            
        data_dict["chi2_tot"][j]=chi2_dict["tot"]
        
        for k2 in out_keys:
            data_dict[k2][j]=out_dict[k2]
        
        print("Index:",i)
        j+=1
    return data_dict

args=sys.argv #arg1: starting index, arg2: ending index
s_ind=int(args[1])
e_ind=int(args[2])

if(s_ind >= e_ind):
    print("Error: Starting index greater than or equal to ending index")
    exit()

ind_range=range(s_ind,e_ind)

ismade=False
targets_set =False #doesn't work as intended
num_cores=3

pcurrent = psutil.Process()
cpid=pcurrent.pid
cwd=os.getcwd()

cploc=cwd + "/models/SSM_test"
workdir=new_work(cpid,cploc,cwd=cwd)


first_FeH = 0.099883042891420248e0
first_Y = 0.27910526985061124e0
first_alpha = 1.9033976646700377e0
first_f_ov = 0.018473664849956072

ntest=40
f_ov_arr= np.linspace(0.016,0.021,ntest-10)
log_part=np.logspace(np.log10(0.021),np.log10(0.045),10)
f_ov_arr= np.append(f_ov_arr,log_part)
#f_ov_arr= np.linspace(0.016,0.031,ntest)
inlist_vec=[]
inlist_loc= workdir +"/inlist_1msun"
model_name="test_chi2.mod"
for q in range(0,ntest):
    solar_inlist=mesa_inlist(fname=inlist_loc)
    solar_inlist.read()
    evolve_inlist_args(solar_inlist,model_name)
    inlist_convert(solar_inlist, first_FeH, first_Y, first_alpha, f_ov_arr[q])
    inlist_vec.append(solar_inlist)

ismade=make_mesa(workdir,OMP_NUM_THREADS=num_cores)
sound_data= load_solar_cs_data()

data_dict=serial_run_mesa_dict(inlist_vec,workdir,sound_data, ind_range=ind_range,
                         OMP_NUM_THREADS=num_cores,made=ismade)
data_dict["f_ov"]=f_ov_arr
savename="outputs/data_dict_%d_%d.pkl" % (s_ind, e_ind)

with open(savename, 'wb') as out_file:
    pickle.dump(data_dict,out_file)

'''chi2_arr=serial_run_mesa(inlist_vec,workdir,sound_data, ind_range=ind_range,
                         OMP_NUM_THREADS=num_cores,made=ismade)
n_in=len(ind_range)
small_f_ov=np.empty(n_in)
for j in range(0,n_in):
    small_f_ov[j]=f_ov_arr[ind_range[j]]

small_f_ov=np.expand_dims(small_f_ov,axis=1)
chi2_arr=np.expand_dims(chi2_arr,axis=1)

data_arr=np.concatenate((small_f_ov,chi2_arr),axis=1)
'''
del_work(workdir)
#savename = "outputs/chi2_%d_%d.txt" % (s_ind, e_ind)
#np.savetxt(savename, data_arr, delimiter=',')
#still need to figure out a good way to save output    
    