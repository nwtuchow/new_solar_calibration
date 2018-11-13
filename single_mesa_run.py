#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 17:14:47 2018

Single MESA run

@author: nxt5109
"""

import psutil
import os
from mesa_utils import *
import mesa_reader as mr
import numpy as np

print("Starting:",flush=True)

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

num_cores=3

i=1

hist_name= 'history_%d.data' % (cpid)
solar_inlist.dict['star_history_name']= "'"+hist_name+"'"
solar_inlist.write()

lastprofname= cwd + "/LOGS/finalProfile_"+ str(cpid) +".data"
ismade=make_mesa(workdir,OMP_NUM_THREADS=num_cores)
pout=run_mesa(solar_inlist,workdir,OMP_NUM_THREADS=num_cores,
              last_profile=lastprofname,made=ismade)
hist_name= cwd+ "/LOGS/"+hist_name
histout=mr.MesaData(hist_name)
tf=histout.elapsed_time[-1]
del_work(workdir)

print("Elapsed Time: %f" % tf, flush=True)
"""
outname= "time_%d.txt" % cpid
f_t = open(outname,'w')
f_t.write("PID: %d" % cpid )
f_t.write("\nTime: %f" % tf)

f_t.close()"""
