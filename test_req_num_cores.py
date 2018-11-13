#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 16:50:09 2018

@author: nxt5109
"""

import psutil
import os
from mesa_utils import *
import mesa_reader as mr
import numpy as np


#use absolute paths to avoid confusion

ORIGINAL_SOLAR="/home/nxt5109/Dropbox/Faint_Young_Sun_Abundances/MESA_modeling/models/1msun_model"
ismade=False

#give current python instance's pid as an int
pcurrent = psutil.Process()
cpid=pcurrent.pid
cwd=os.getcwd()

workdir= new_work(cpid,ORIGINAL_SOLAR,cwd=cwd)

inlistname = workdir +"/inlist_1msun"
solar_inlist= mesa_inlist(fname=inlistname)
solar_inlist.read()
solar_inlist.dict['log_directory']= "'"+cwd+"/LOGS"+"'"
#maybe also list history and profile columns here
solar_inlist.write()

num_cores=[1,2,4,8,16] #should really be call num_threads
times= np.zeros(5)

for i in range(2,3):
    ismade=False
    print("Number of Cores: %d" % num_cores[i])

    hist_name= 'history_%d_%d.data' % (i,cpid)
    solar_inlist.dict['star_history_name']= "'"+hist_name+"'"
    solar_inlist.write()

    lastprofname= cwd + "/LOGS/finalProfile_" + str(i) +"_"+str(cpid) +".data"
    ismade=make_mesa(workdir,OMP_NUM_THREADS=num_cores[i])
    pout=run_mesa(solar_inlist,workdir,OMP_NUM_THREADS=num_cores[i],
                      last_profile=lastprofname,made=ismade)
    hist_name= cwd+ "/LOGS/"+hist_name
    histout=mr.MesaData(hist_name)
    times[i]=histout.elapsed_time[-1]
    print("Elapsed Time: %f" % times[i], flush=True)

del_work(workdir)


'''
import matplotlib.pyplot as plt

fig, ax =plt.subplots(1)
ax.plot(num_cores,times)
ax.set_xlabel("Number of Cores")
ax.set_ylabel("Elapsed Time (s)")

fig.savefig("cores_vs_time_diffusion.png")'''
