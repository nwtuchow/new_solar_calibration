#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 15:26:57 2018

@author: nxt5109
"""
from rw_inlists import *
import subprocess

import mesa_reader as mr


#function to run mesa given a mesa_inlist object
#returns mesa_reader profile object
def run_mesa(inlist,MESA_DIR="/data/nxt5109/mesa-r10398",OMP_NUM_THREADS = 16,
             MESASDK_ROOT="/data/nxt5109/mesasdk",INITIALIZE="$MESASDK_ROOT/bin/mesasdk_init.sh",
             pgstar=False, last_profile='LOGS/finalProfile1Msun.data'):
    mesa_start= ("export MESA_DIR=" + MESA_DIR +";\n"+
                 "export OMP_NUM_THREADS="+str(OMP_NUM_THREADS) + ";\n"+
                 "export MESASDK_ROOT=" + MESASDK_ROOT+ ";\n" +
                 "source " + INITIALIZE + ";\n" +
                 "./mk;\n" + "./rn")
    
    #exit if important parts of inlist object are blank
    if inlist.fname=='' or inlist.lines==[] or inlist.dict=={}:
        print("Incomplete inlist.\nExiting")
        return
    
    if pgstar and ("pgstar_flag" in inlist.dict):
        inlist.dict["pgstar_flag"]=".true."
    elif "pgstar_flag" in inlist.dict:
        inlist.dict["pgstar_flag"]=".false."
        
    if ("filename_for_profile_when_terminate" in inlist.dict) and  last_profile != '':
        inlist.dict["filename_for_profile_when_terminate"]= "'"+last_profile + "'"
    
    #write inlist file and initialize and run mesa
    inlist.write()
    subprocess.call(mesa_start, shell=True, executable='/bin/bash')
    
    pf=mr.MesaData(last_profile)
    return pf
    
#earlier version of run_mesa
def run_mesa2(lines,solar_dict,fname,MESA_DIR="/data/nxt5109/mesa-r10398",OMP_NUM_THREADS = 16,
             MESASDK_ROOT="/data/nxt5109/mesasdk",INITIALIZE="$MESASDK_ROOT/bin/mesasdk_init.sh",
             pgstar=False, last_profile='LOGS/finalProfile1Msun.data'):
    mesa_start= ("export MESA_DIR=" + MESA_DIR +";\n"+
                 "export OMP_NUM_THREADS="+str(OMP_NUM_THREADS) + ";\n"+
                 "export MESASDK_ROOT=" + MESASDK_ROOT+ ";\n" +
                 "source " + INITIALIZE + ";\n" +
                 "./mk;\n" + "./rn")
    
    if pgstar and ("pgstar_flag" in solar_dict):
        solar_dict["pgstar_flag"]=".true."
    elif "pgstar_flag" in solar_dict:
        solar_dict["pgstar_flag"]=".false."
    
    if ("filename_for_profile_when_terminate" in solar_dict) and  last_profile != '':
        solar_dict["filename_for_profile_when_terminate"]= "'"+last_profile + "'"
            
    write_inlist(lines,solar_dict,fname)
    subprocess.call(mesa_start, shell=True, executable='/bin/bash')
    
    pf= mr.MesaData(last_profile)
    return pf
    
'''alt_start="""export MESA_DIR=/data/nxt5109/mesa-r10398;
	export OMP_NUM_THREADS=16;
	export MESASDK_ROOT=/data/nxt5109/mesasdk;
	source $MESASDK_ROOT/bin/mesasdk_init.sh;
    ./mk;
    ./rn"""
subprocess.call(['/bin/bash', '-i', '-c', alt_start])
MESA_DIR="/data/nxt5109/mesa-r10398"
OMP_NUM_THREADS = 16
MESASDK_ROOT="/data/nxt5109/mesasdk"
INITIALIZE="$MESASDK_ROOT/bin/mesasdk_init.sh"
'''


fname= "inlist_1msun"

inlist_solar= mesa_inlist(fname=fname)

inlist_solar.read()

plast= run_mesa(inlist_solar)