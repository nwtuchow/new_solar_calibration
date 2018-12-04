#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 15:50:45 2018

@author: nxt5109
"""

import psutil
import os
from mesa_utils import *
from solar_chi2 import *
import mesa_reader as mr
import numpy as np

#num_cores=16


#version with dict output
#keys are keys for chi2 dict
#need to modify to specify which stage of evolution
#ind_range should be depreciated
def serial_run_mesa_dict(inlist_vec,workdir,sound_data, ind_range=[],labels='',
                    model_name="initial_sun.mod", OMP_NUM_THREADS=16,made=False,
                    keys=["Teff", "log_L","surface_He","Rcz","cs_rms"],initialize=False,
                    log_dir='',keepcs=False):
    if ind_range ==[]:
        n_in=len(inlist_vec)
        ind_range = range(0,n_in)
    else:
        n_in = len(ind_range)
    
    out_keys=['Teff','log_R', 'log_g', 'log_L', 'FeH', 'age', 'surface_Z_div_X',
               'surface_He','Rcz', 'cs_rms']
    
    data_dict={}
    #allocate chisq component arrays
    for s1 in keys:
        s1_chi2="chi2_" +s1
        data_dict[s1_chi2]=np.empty(n_in)
    #allocate output array in dict
    for s2 in out_keys:
        data_dict[s2]=np.empty(n_in)
    
    data_dict["chi2_tot"]=np.empty(n_in)
    if keepcs:
        data_dict["cs"]= []
        data_dict["r"]=[]
        data_dict["dq"]=[]
    
    if log_dir=='':
        log_dir= workdir+"/LOGS"
    
    j=0
    for i in ind_range:
        if type(labels)==list:
            label=labels[i]
        else:
            label=labels
            
        prof_name=log_dir + "/"+label+"Profile_%d.data" % i
        hist_name=label+"history_%d.data" % i
        
        #initialize model
        if initialize:
            PMS_inlist_args(inlist_vec[i],model_name)
            outputs= run_mesa(inlist_vec[i],workdir,OMP_NUM_THREADS=OMP_NUM_THREADS,made=made,
                   last_profile=prof_name, hist_name =hist_name, log_dir=log_dir,
                   use_hist=True)
            #will using the same variable "outputs" cause problems?
        
        #evolve model
        evolve_inlist_args(inlist_vec[i],model_name)
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
            
        for k2 in out_keys:
            data_dict[k2][j]=out_dict[k2]
            
        data_dict["chi2_tot"][j]=chi2_dict["tot"]
        if keepcs:
            data_dict["cs"].append(profile.csound)
            data_dict["r"].append(profile.radius)
            data_dict["dq"].append(profile.dq)
        
        print("Index:",i, "\nChi2:",chi2_dict["tot"])
        j+=1
    return data_dict

#needs to be tested
def mesa_wrapper(in_dict,num_cores=16, cploc='',log_dir='', labels='',
                 initialize= False, model_name="initial_sun.mod",keepcs=False,
                 keys=["Teff", "log_L","surface_He","Rcz","cs_rms"]):
    ismade=False
    pcurrent = psutil.Process()
    cpid=pcurrent.pid
    cwd=os.getcwd()
    if cploc=='':
        cploc=cwd + "/models/SSM_test"
        
    workdir=new_work(cpid,cploc,cwd=cwd)
    if log_dir=='':
        log_dir= workdir+"/LOGS"
    
    count=0
    #ensure all keys in indict correspond to arrays of same length
    for st in in_dict:
        ntests=len(in_dict[st])
        oldn=ntests
        if count > 0:
            if oldn!= ntests:
                print("Dictionary dimension mismatch")
                exit()
        count+=1
        
    inlist_vec=[]
    inlist_loc= workdir +"/inlist_1msun"
    
    #inlists here need to be specified whether they are for initialization or evolution
    for i in range(0,ntests):
        solar_inlist=mesa_inlist(fname=inlist_loc)
        solar_inlist.read()
        inlist_convert(solar_inlist, in_dict["init_FeH"][i], in_dict["init_Y"][i], 
                       in_dict["alpha"][i], in_dict["f_ov"][i])
        inlist_vec.append(solar_inlist)
    
    ismade=make_mesa(workdir,OMP_NUM_THREADS=num_cores)
    sound_data = load_solar_cs_data()
    #call serial mesa
    data_dict=serial_run_mesa_dict(inlist_vec,workdir,sound_data,model_name=model_name,
                         OMP_NUM_THREADS=num_cores,made=ismade,log_dir=log_dir, 
                         initialize=initialize,keepcs=keepcs,labels=labels,keys=keys)
    
    #make sure none of in_dict keys are same as data_dict
    #if calling mesa_wrapper multiple times should deepcopy, not use update
    data_dict.update(in_dict)
    del_work(workdir)
    return data_dict


'''
in_dict={} #all fields must be same dimensions
in_dict["f_ov"]=[0.016, 0.030]
in_dict["init_Y"]=[0.27910526985061124e0,0.27910526985061124e0]
in_dict["init_FeH"]=[0.099883042891420248e0,0.099883042891420248e0]
in_dict["alpha"]=[1.9033976646700377e0,1.9033976646700377e0]

out_data=mesa_wrapper(in_dict,num_cores=16,initialize=False,model_name="test_chi2.mod")
'''