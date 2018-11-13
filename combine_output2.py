#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 15:13:27 2018

Combine multiple output data files into one array
@author: nxt5109
"""
import numpy as np
import matplotlib.pyplot as plt
#import os
import pickle
import copy

#append two dictionaries with the same keys
#requires all keys to correspond to arrays
def append_dict(dict1,dict2):
    dict3={}
    for key in dict1:
        part1=dict1[key]
        part2=dict2[key]
        tot_arr=np.append(part1,part2)
        dict3[key]=tot_arr
    return dict3

s_ind=0
e_ind=8

num_files=5
big_dict={}

for k in range(0,num_files):
    fname= "outputs/data_dict_%d_%d.pkl" % (s_ind, e_ind)
    with open(fname,'rb') as f1:
        file_dict = pickle.load(f1)
    
    if k==0:
        big_dict=copy.deepcopy(file_dict)
    else:
        big_dict=append_dict(big_dict,file_dict)
    
    s_ind+=8
    e_ind+=8

#f_ov_arr=big_dict["f_ov"]
ntest=40
f_ov_arr= np.linspace(0.016,0.021,ntest-10)
log_part=np.logspace(np.log10(0.021),np.log10(0.045),10)
f_ov= np.append(f_ov_arr,log_part)

fig, ax =plt.subplots(1)
ax.plot(f_ov,big_dict['chi2_tot'],'k-', label="total chi2", lw=2.5)
ax.plot(f_ov,big_dict['chi2_Teff']/5, label="Teff", ls="dashed", lw=1.5)
ax.plot(f_ov,big_dict['chi2_log_L']/5, label="log(L)",ls="dashed", lw=1.5)
ax.plot(f_ov,big_dict['chi2_surface_He']/5, label="surface He",ls="dashed", lw=1.5)
ax.plot(f_ov,big_dict['chi2_Rcz']/5, label="R_cz",ls="dashed", lw=1.5)
ax.plot(f_ov,big_dict['chi2_cs_rms']/5, label="cs rms",ls="dashed", lw=1.5)
ax.set_xlabel(r"$f_{ov}$")
ax.set_ylabel(r"$\chi ^2 _{\nu}$")
ax.set_ylim([0.0,14.0])
ax.legend()
fig.savefig("plots/f_ov_chi2_components.png")

from solar_chi2 import set_targets

targets_set=set_targets()

fig2, ax2 =plt.subplots(1)

target_T_line=Teff_target*np.ones(40)
ax2.plot(f_ov,target_T_line, 'k--',)
ax2.plot(f_ov,big_dict["Teff"])
ax2.set_xlabel(r"$f_{ov}$")
ax2.set_ylabel("T_eff (K)")
fig2.savefig("plots/f_ov_vs_T.png")

target_logL_line=logL_target*np.ones(40)
fig3, ax3 =plt.subplots(1)
ax3.plot(f_ov,target_logL_line, 'k--',)
ax3.plot(f_ov,big_dict["log_L"])
ax3.set_xlabel(r"$f_{ov}$")
ax3.set_ylabel("log(L)")
fig3.savefig("plots/f_ov_vs_logL.png")

target_cs_rms_line=solar_cs_rms_target*np.ones(40)
fig4, ax4 =plt.subplots(1)
ax4.plot(f_ov,target_cs_rms_line, 'k--',)
ax4.plot(f_ov,big_dict["cs_rms"])
ax4.set_xlabel(r"$f_{ov}$")
ax4.set_ylabel("c_s rms")
fig4.savefig("plots/f_ov_vs_cs_rms.png")


#old version
'''s_ind=0
e_ind=6

num_files=5



for k in range(0,num_files):
    fname="outputs/chi2_%d_%d.txt" % (s_ind, e_ind)
    data_arr=np.loadtxt(fname,delimiter=',')
    if k==0:
        big_arr= data_arr
    else:
        big_arr=np.vstack((big_arr,data_arr))
    s_ind+=6
    e_ind+=6
    
import matplotlib.pyplot as plt
fig, ax =plt.subplots(1)
ax.plot(big_arr[:,0],big_arr[:,1])
ax.set_xlabel("f_ov")
ax.set_ylabel(r"$\chi ^2$")
fig.savefig("f_ov_chi2_2.png")'''