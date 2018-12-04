#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 17:14:47 2018

Single SSM run
takes num cores as a command line argument

@author: nxt5109
"""

import psutil
import os
import sys
from mesa_utils import *
import mesa_reader as mr
import numpy as np

args=sys.argv
num_cores=int(args[1])

print("Starting:",flush=True)

ismade=False

#give current python instance's pid as an int
pcurrent = psutil.Process()
cpid=pcurrent.pid
cwd=os.getcwd()

cploc= cwd + "/models/SSM_test"
workdir= new_work(cpid,cploc,cwd=cwd)
log_dir= cwd+"/LOGS/parallelization"

inlist_loc= workdir +"/inlist_1msun"
solar_inlist= mesa_inlist(fname=inlist_loc)
solar_inlist.read()

ismade=make_mesa(workdir,OMP_NUM_THREADS=num_cores)
model_name="test_chi2.mod"
evolve_inlist_args(solar_inlist,model_name)

hist_name= 'history_%d.data' % (cpid)
lastprofname= cwd + "/LOGS/finalProfile_"+ str(cpid) +".data"


outputs= run_mesa(solar_inlist,workdir,OMP_NUM_THREADS=num_cores,made=ismade,
                   last_profile=lastprofname, hist_name =hist_name, log_dir=log_dir,
                   use_hist=True)

histout=outputs[1]
tf=histout.elapsed_time[-1]
del_work(workdir)

print("Elapsed Time: %f" % tf, flush=True)
"""
outname= "time_%d.txt" % cpid
f_t = open(outname,'w')
f_t.write("PID: %d" % cpid )
f_t.write("\nTime: %f" % tf)

f_t.close()"""
