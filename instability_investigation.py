#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 15:13:27 2018

Combine multiple output data files into one array
for f_ov min1
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
e_ind=10

num_files=5
big_dict={}
#should look into including file names for profiles and histories in dict

for k in range(0,num_files):
    fname= "outputs/f_ov_min1_%d_%d.pkl" % (s_ind, e_ind)
    with open(fname,'rb') as f1:
        file_dict = pickle.load(f1)
    
    if k==0:
        big_dict=copy.deepcopy(file_dict)
    else:
        big_dict=append_dict(big_dict,file_dict)
    
    s_ind+=10
    e_ind+=10

f_ov=big_dict['f_ov']

fig, ax =plt.subplots(1)
ax.plot(f_ov,big_dict['chi2_tot'],'k-', label="total chi2", lw=2.5)
ax.plot(f_ov,big_dict['chi2_Teff']/5, label="Teff", ls="dashed", lw=1.5)
ax.plot(f_ov,big_dict['chi2_log_L']/5, label="log(L)",ls="dashed", lw=1.5)
ax.plot(f_ov,big_dict['chi2_surface_He']/5, label="surface He",ls="dashed", lw=1.5)
ax.plot(f_ov,big_dict['chi2_Rcz']/5, label="R_cz",ls="dashed", lw=1.5)
ax.plot(f_ov,big_dict['chi2_cs_rms']/5, label="cs rms",ls="dashed", lw=1.5)
ax.set_xlabel(r"$f_{ov}$")
ax.set_ylabel(r"$\chi ^2 _{\nu}$")
ax.legend()
#fig.savefig("plots/f_ov_min1_chi2.png")

#f_ov_arr=big_dict["f_ov"]

fig2, ax2= plt.subplots(1)
ax2.plot(big_dict['surface_Z_div_X'],big_dict['chi2_tot'])
ax2.set_xlabel("surface Z/X")
ax2.set_ylabel("reduced chi2")

fig3, ax3= plt.subplots(1)
ax3.scatter(big_dict['log_g'],big_dict['chi2_tot'])
ax3.set_xlabel("log(g)")
ax3.set_ylabel("reduced chi2")

fig4, ax4= plt.subplots(1)
ax4.scatter(big_dict['log_R'],big_dict['chi2_tot'])
ax4.set_xlabel("log(R)")
ax4.set_ylabel("reduced chi2")