#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  3 15:46:09 2018

@author: nxt5109
"""

import psutil
import os
from mesa_utils import *
import mesa_reader as mr

ORIGINAL_SOLAR="/home/nxt5109/Dropbox/Faint_Young_Sun_Abundances/MESA_modeling/models/1msun_model"
ismade=False

#give current python instance's pid as an int
pcurrent = psutil.Process()
cpid=pcurrent.pid
cwd=os.getcwd()

workdir= new_work(cpid,ORIGINAL_SOLAR,cwd=cwd)
zarr= [0.01,0.015,0.02]

inlistname = workdir +"/inlist_1msun"
solar_inlist= mesa_inlist(fname=inlistname)
solar_inlist.read()

ismade=make_mesa(workdir)
p_arr=[]
for i in range(0,len(zarr)):
    zstr=str(zarr[i])
    if 'e' in zstr:
        solar_inlist.dict['initial_z']= e_to_d(zstr)
    else:
        solar_inlist.dict['initial_z']=zstr
    
    solar_inlist.dict['star_history_name']= "'history_%d_%d.data'" % (i,cpid)
    solar_inlist.write()
    lastprofname= cwd + "/LOGS/finalProfile_" + str(i) +"_"+str(cpid) +".data"
    pout=run_mesa(solar_inlist,workdir,last_profile=lastprofname,made=ismade)
    p_arr.append(pout)
    

'''L_arr=[]

for q in range(0,len(zarr)):
    L_arr.append(p_arr[q].photosphere_L)

print(L_arr)'''



    
