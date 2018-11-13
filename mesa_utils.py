#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Utilities for running MESA from python

"""

import subprocess
import os
import mesa_reader as mr
import copy

#locations of mesa files
MESA_DIR="/data/nxt5109/mesa-r10398"
OMP_NUM_THREADS = 16
MESASDK_ROOT="/data/nxt5109/mesasdk"
INITIALIZE="$MESASDK_ROOT/bin/mesasdk_init.sh"

#class for storing mesa inlists
class mesa_inlist:
    def __init__(self, lines=[],inlist_dict=dict(),fname=''):
        self.lines=lines
        self.dict=inlist_dict
        self.fname=fname
    
    def read(self, f_in=None):
        f_in = f_in or self.fname
        if f_in=='':
            print("No input file name given")
            return
            
        self.fname=f_in
        ll, outdict = read_inlist(f_in)
        self.lines = ll
        self.dict = outdict
    
    def write(self, f_out=None):
        f_out = f_out or self.fname
        if f_out=='':
            print("No output file name given")
            return
        self.fname =f_out
        write_inlist(self.lines, self.dict, f_out)
        
#function to read MESA inlist file
#inputs:
#   f_in_name: inlist file name
#outputs:
#   linelist: list of lists of str, lines of file broken into relevant parts
#   inlist_dict: dictionary of inlist keywords and values
def read_inlist(f_in_name):
    f_in = open(f_in_name,"r")

    linelist=[] #tuple for storing different parts of a line
    inlist_dict=dict()
    for line in f_in:
        l=line.strip() #remove '\n'
        content=''
        comment=''
    
        if l.startswith('&'):
            content,comment = l.split('&',1)
            comment= "&" + comment
        elif l.startswith('/'):
            content,comment = l.split('/',1)
            comment="/" + comment
        elif '!' in l: #do this last because can have lines like "&pgstar !plotting" and want all to be comment
            content,comment = l.split('!',1)
            comment="!" + comment
        else:
            content=l
        #end if
        keyw=""
        val=""
        if len(content)>0 and "=" in content:
            keyw,val= content.split('=',1)
            keyw=keyw.strip()
            val=val.strip()
    
        if len(keyw)>0 and len(val)>0:
            inlist_dict.update({keyw:val})
        
        linelist.append([keyw,val,comment])
    #end for
    f_in.close()
    return linelist, inlist_dict
#end fcn

#function to write MESA inlist to file
#updates content of out of date linelist
#inputs:
#   linelist: list of lists of str, lines of file broken into relevant parts
#   inlist_dict: dictionary of inlist keywords and values
#   f_out_name: name of output file
def write_inlist(linelist, inlist_dict, f_out_name):
    f_out = open(f_out_name,'w')
    llist=copy.deepcopy(linelist)

    #update tuple with current dict values
    for key in inlist_dict:
        for j in range(0,len(llist)):
            if llist[j][0]==key:
                llist[j][1]=inlist_dict[key]

    for i in range(0,len(llist)):
        if len(llist[i][0])>0:
            outstr= llist[i][0] +" = "+ llist[i][1]+" " +llist[i][2] +"\n"
        else:
            outstr= llist[i][0] + llist[i][1] + llist[i][2]+"\n"
        
        if len(llist[i][0])==0 and len(llist[i][1])!=0:
            print("This should never happen!")
    
        f_out.write(outstr)
    
    f_out.close()
    return;


#function to make MESA prior to running
#specify inlistdir, directory of inlist with mk executable
#returns boolian if make command ran
def make_mesa(inlistdir,MESA_DIR=MESA_DIR,OMP_NUM_THREADS = 16,
             MESASDK_ROOT=MESASDK_ROOT,INITIALIZE=INITIALIZE):
    mesa_make=("export MESA_DIR=" + MESA_DIR +";\n"+
                 "export OMP_NUM_THREADS="+str(OMP_NUM_THREADS) + ";\n"+
                 "export MESASDK_ROOT=" + MESASDK_ROOT+ ";\n" +
                 "source " + INITIALIZE + ";\n" +
                 "cd " + inlistdir + ";\n" +
                 "./mk")
    subprocess.call(mesa_make, shell=True, executable='/bin/bash')
    return True

#function to run mesa given a mesa_inlist object
#takes inlist object and absolute path to inlist
#specify if want to use pgstar with boolian
#give absolute path to output profiles in last_profile
#made: specify if make command has been run
#if use_hist true give hist_name as a string and log_dir as an absolute path
#returns mesa_reader profile object()
def run_mesa(inlist,inlistdir, MESA_DIR = MESA_DIR,OMP_NUM_THREADS = 16,
             MESASDK_ROOT = MESASDK_ROOT,INITIALIZE = INITIALIZE,
             pgstar = False, last_profile='',hist_name='',log_dir='',
             made=False, use_hist=False):
    mesa_start= ("export MESA_DIR=" + MESA_DIR +";\n"+
                 "export OMP_NUM_THREADS="+str(OMP_NUM_THREADS) + ";\n"+
                 "export MESASDK_ROOT=" + MESASDK_ROOT+ ";\n" +
                 "source " + INITIALIZE + ";\n" +
                 "cd " + inlistdir + ";\n" +
                 "./rn")
    #exit if makefile wasn't run
    if not made:
        print("Make Mesa before running")
        return
    #exit if important parts of inlist object are blank
    if inlist.fname=='' or inlist.lines==[] or inlist.dict=={}:
        print("Incomplete inlist.\nExiting")
        return
    
    if pgstar and ("pgstar_flag" in inlist.dict):
        inlist.dict["pgstar_flag"]=".true."
    elif "pgstar_flag" in inlist.dict:
        inlist.dict["pgstar_flag"]=".false."
    
    #need to edit based on location of inlist relative to python script    
    if ("filename_for_profile_when_terminate" in inlist.dict):
        if last_profile != '':
            inlist.dict["filename_for_profile_when_terminate"]= "'"+last_profile + "'"
        else:
            last_profile =inlist.dict["filename_for_profile_when_terminate"]
            last_profile = last_profile[1:-1]
    
    if ("star_history_name" in inlist.dict) and use_hist:
        if hist_name!='':
            inlist.dict["star_history_name"]= "'" + hist_name +"'"
        else:
            hist_name= inlist.dict["star_history_name"]
            hist_name= hist_name[1:-1]
    
    if ("log_directory" in inlist.dict) and use_hist:
        if log_dir!='':
            inlist.dict["log_directory"]= "'" + log_dir +"'"
        else:
            log_dir= inlist.dict["log_directory"]
            log_dir= log_dir[1:-1]
    
    #write inlist file and initialize and run mesa
    inlist.write()
    subprocess.call(mesa_start, shell=True, executable='/bin/bash')
    
    pf=mr.MesaData(last_profile)
    #requires log location specified
    if use_hist:
        hist_loc= log_dir + '/' +hist_name
        hf=mr.MesaData(hist_loc)
        return [pf, hf]
    else:
        return pf

#make new work directory
#pid: process id
#cploc : location of copied work directory
#cwd : current working directory    
def new_work(pid, cploc,cwd=os.getcwd(), label=''):
    dirname = cwd + "/" + "models/%d" % (pid) +label
    mkcmd= "mkdir " + dirname
    subprocess.call(mkcmd, shell=True,executable='/bin/bash')
    cpcmd ="cp -r "+ cploc + "/. "+ dirname
    subprocess.call(cpcmd, shell=True,executable='/bin/bash')
    
    return dirname

#delete working directory
#dirname: directory name
def del_work(dirname):
    rmcmd= "rm -r " + dirname
    subprocess.call(rmcmd, shell=True,executable='/bin/bash')
    return

#change exponential notation for string, s, to be fortran 90 compatible 
def e_to_d(s,verbose=False):
    eind=s.find('e')
    if eind==-1:
        if verbose:
            print("No 'e' in string")
        return s
    
    s= s[:eind]+ 'd' +s[(eind+1):]
    return s

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
    
#change inlist to run initialization    
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

#change inlist to evolve star
def evolve_inlist_args(inlist,model_name, age=4.61e9):
    inlist.dict['create_pre_main_sequence_model']='.false.'
    inlist.dict['load_saved_model']='.true.'
    inlist.dict['saved_model_name']= "'" +model_name +"'"
    inlist.dict['save_model_when_terminate']='.false.'
    inlist.dict['max_age']=e_to_d(str(age))
    inlist.dict['which_atm_option']="'photosphere_tables'"
    

    