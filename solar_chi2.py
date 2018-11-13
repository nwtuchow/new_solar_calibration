#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 16:13:28 2018

Solar Chi squared

@author: nxt5109
"""
import numpy as np
import mesa_reader as mr
from scipy.interpolate import interp1d


def load_solar_cs_data(SOLAR_SOUND_DATA_LOC="/data/nxt5109/mesa-r10398/data/star_data/solar_csound.data"):
    sound_array= np.loadtxt(SOLAR_SOUND_DATA_LOC,skiprows=11)
    return sound_array
#function to calculate rms of sound speed data 
    # takes location of profile file and array from load_solar_cs_data
def calc_sound_rms(profile, sound_array):
    min_R = 0.094
    max_R = 0.94

    data_r = sound_array[:,0]
    data_cs = sound_array[:,2]
    #data_width = sound_array[:,6]

    npts= len(data_cs)
    
    model_cs = profile.csound
    model_r = profile.radius #appears ordered outmost to inmost
    dq = profile.dq

    nz=len(model_cs)
    calc_rms_f= np.empty(nz)

    for k in range(0,nz):
        if k==0:
            calc_rms_f[k]= model_cs[k]
        else:
            calc_rms_f[k]= (model_cs[k]*dq[k-1] + model_cs[k-1]*dq[k])/(dq[k-1]+dq[k])
        
    f_cs =interp1d(model_r,calc_rms_f,kind='cubic')

    new_cs = f_cs(data_r) #model cs value corresponding to data

    sumy2 = 0
    sumdr = 0

    for i in range(0,npts):
        if data_r[i]<min_R or data_r[i]>max_R:
            continue    
    
        #outdated left in fortran code?
        if i==0:
            dr = data_r[1] - data_r[0]
        else:
            dr = data_r[i] - data_r[i-1]
        
        if dr < 0:
            dr = -dr
            
        #change to weigh by point rather than by dr
        dr = 1
    
        sumdr+= dr
        y2= dr *((new_cs[i]-data_cs[i])/data_cs[i])**2
        sumy2+= y2
        
    calc_current_rms = np.sqrt(sumy2/sumdr)
    return calc_current_rms

def chi_squared(model,target,sigma):
    chi2= ((model - target)/sigma)**2
    return chi2

#sets global variables for solar target values used in chi squared
def set_targets():
    global Teff_target, Teff_sigma
    Teff_target = 5777e0
    Teff_sigma = 65e0
    
    global logR_target, logR_sigma
    logR_target = -1
    logR_sigma = -1
    
    global logg_target, logg_sigma
    logg_target = -1
    logg_sigma = -1
    
    global logL_target, logL_sigma
    logL_target = 0.00e0
    logL_sigma = 0.05e0
    
    global FeH_target, FeH_sigma
    FeH_target = 0.00
    FeH_sigma = 0.05
    
    global age_target, age_sigma
    age_target = 4.61e9
    age_sigma = 1e7
    
    global surface_Z_div_X_target, surface_Z_div_X_sigma
    surface_Z_div_X_target = 2.292e-2 # GS98 value
    #surface_Z_div_X_target = 1.81e-2 # Asplund 09 value
    surface_Z_div_X_sigma = 1e-3
    
    global surface_He_target, surface_He_sigma
    surface_He_target = 0.2485e0 # Basu & Antia 2004
    surface_He_sigma = 0.0035
    
    global Rcz_target, Rcz_sigma
    Rcz_target = 0.713e0 # Basu & Antia 1997
    Rcz_sigma = 1e-3
    
    global solar_cs_rms_target, solar_cs_rms_sigma
    solar_cs_rms_target = 0
    solar_cs_rms_sigma = 2e-4
    
    targets_set=True
    return targets_set

#convert profile and history objects to outputs for use in chi2
def output_convert(last_profile,history,sound_arr):
    out_dict=dict()
    surfaceX= max(history.surface_h1[-1],1e-10)
    surfaceHe = history.surface_he3[-1] + history.surface_he4[-1]
    surfaceZ =max(1e-99, min(1e0, 1 - (surfaceX + surfaceHe)))
    surface_Z_div_X = surfaceZ/surfaceX
    Z_div_X_solar = 0.02293e0
    
    log_Teff =history.log_Teff[-1]
    Teff =10**log_Teff
    out_dict["Teff"]=Teff
    
    log_R =history.log_R[-1]
    out_dict["log_R"]=log_R
    
    log_g =history.log_g[-1]
    out_dict["log_g"]=log_g
    
    log_L =history.log_L[-1]
    out_dict["log_L"]=log_L
    
    FeH=np.log10(surface_Z_div_X/Z_div_X_solar)
    out_dict["FeH"]=FeH
    
    age =history.star_age[-1]
    out_dict["age"]=age
    
    out_dict["surface_Z_div_X"]=surface_Z_div_X
    
    out_dict["surface_He"]=surfaceHe
    
    Rcz = history.cz_bot_radius[-1]
    out_dict["Rcz"]=Rcz
    
    cs_rms= calc_sound_rms(last_profile, sound_arr)
    out_dict["cs_rms"]=cs_rms
    
    return out_dict   


#like other chi2, but takes input as a dict from 
#output_convert(last_profile,history,sound_arr)
#outputs dict for chi2
def tot_chi_squared_dict(output_dict, targets_set=False, include_Teff_in_chi2=True,
                    include_logR_in_chi2 = False, include_logg_in_chi2 = False,
                    include_logL_in_chi2 = True, include_FeH_in_chi2 = False, 
                    include_age_in_chi2 = False, include_surface_Z_div_X_in_chi2 = False, 
                    include_surface_He_in_chi2 = True, include_Rcz_in_chi2 = True,
                    include_solar_cs_rms_in_chi2= True, keys=[]):
    if targets_set==False:
        targets_set=set_targets()
    
    #can set which terms to use with an array of keys
    #maybe eventually get rid of boolian key words
    if keys!=[]:
        if "Teff" in keys:
            include_Teff_in_chi2=True
        else:
            include_Teff_in_chi2=False
        if "log_R" in keys:
            include_logR_in_chi2 = True
        else:
            include_logR_in_chi2 = False
        if "log_g" in keys:
            include_logg_in_chi2 = True
        else:
            include_logg_in_chi2 = False
        if "log_L" in keys:
            include_logL_in_chi2 = True
        else:
            include_logL_in_chi2 = False
        if "FeH" in keys:
            include_FeH_in_chi2 = True
        else:
            include_FeH_in_chi2 = False
        if "age" in keys:
            include_age_in_chi2 = True
        else:
            include_age_in_chi2 = False
        if "surface_Z_div_X" in keys:
            include_surface_Z_div_X_in_chi2 = True
        else:
            include_surface_Z_div_X_in_chi2 = False
        if "surface_He" in keys:
            include_surface_He_in_chi2 = True
        else:
            include_surface_He_in_chi2 = False
        if "Rcz" in keys:
            include_Rcz_in_chi2 = True
        else:
            include_Rcz_in_chi2 = False
        if "cs_rms" in keys:
            include_solar_cs_rms_in_chi2 = True
        else:
            include_solar_cs_rms_in_chi2 = False
            
    
    chi2_dict={}
    
    chi2sum = 0
    chi2N = 0
    
    if include_Teff_in_chi2 and Teff_sigma>0:
        chi2term= chi_squared(output_dict["Teff"],Teff_target,Teff_sigma)
        chi2_dict["Teff"]=chi2term
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_logR_in_chi2 and logR_sigma>0:
        chi2term= chi_squared(output_dict["log_R"],logR_target,logR_sigma)
        chi2_dict["log_R"]=chi2term
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_logg_in_chi2 and logg_sigma>0:
        chi2term= chi_squared(output_dict["log_g"],logg_target,logg_sigma)
        chi2_dict["log_g"]=chi2term
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_logL_in_chi2 and logL_sigma>0:
        chi2term= chi_squared(output_dict["log_L"],logL_target,logL_sigma)
        chi2_dict["log_L"]=chi2term
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
        
    if include_FeH_in_chi2 and FeH_sigma>0:
        chi2term= chi_squared(output_dict["FeH"],FeH_target,FeH_sigma)
        chi2_dict["FeH"]=chi2term
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_age_in_chi2 and age_sigma>0:
        chi2term= chi_squared(output_dict["age"],age_target,age_sigma)
        chi2_dict["age"]=chi2term
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_surface_Z_div_X_in_chi2 and surface_Z_div_X_sigma>0:
        chi2term= chi_squared(output_dict["surface_Z_div_X"],surface_Z_div_X_target,
                              surface_Z_div_X_sigma)
        chi2_dict["surface_Z_div_X"]=chi2term
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_surface_He_in_chi2 and surface_He_sigma>0:
        chi2term= chi_squared(output_dict["surface_He"],surface_He_target,
                              surface_He_sigma)
        chi2_dict["surface_He"]=chi2term
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_Rcz_in_chi2 and Rcz_sigma>0:
        chi2term= chi_squared(output_dict["Rcz"],Rcz_target,Rcz_sigma)
        chi2_dict["Rcz"]=chi2term
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_solar_cs_rms_in_chi2 and solar_cs_rms_sigma>0:
        chi2term= chi_squared(output_dict["cs_rms"],solar_cs_rms_target,solar_cs_rms_sigma)
        chi2_dict["cs_rms"]=chi2term
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    chi2= chi2sum/max(1,chi2N)
    chi2_dict["tot"]=chi2
    chi2_dict["N"]=chi2N
    return chi2_dict


#calculate chi^2 following Brandao et al, 2011, eqn 11
def tot_chi_squared(last_profile,history,sound_arr, targets_set=False, include_Teff_in_chi2=True,
                    include_logR_in_chi2 = False, include_logg_in_chi2 = False,
                    include_logL_in_chi2 = True, include_FeH_in_chi2 = False, 
                    include_age_in_chi2 = False, include_surface_Z_div_X_in_chi2 = False, 
                    include_surface_He_in_chi2 = True, include_Rcz_in_chi2 = True,
                    include_solar_cs_rms_in_chi2= True):
    if targets_set==False:
        targets_set=set_targets()
    
    output_dict = output_convert(last_profile,history,sound_arr)
    
    chi2sum = 0
    chi2N = 0
    
    if include_Teff_in_chi2 and Teff_sigma>0:
        chi2term= chi_squared(output_dict["Teff"],Teff_target,Teff_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_logR_in_chi2 and logR_sigma>0:
        chi2term= chi_squared(output_dict["log_R"],logR_target,logR_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_logg_in_chi2 and logg_sigma>0:
        chi2term= chi_squared(output_dict["log_g"],logg_target,logg_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_logL_in_chi2 and logL_sigma>0:
        chi2term= chi_squared(output_dict["log_L"],logL_target,logL_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
        
    if include_FeH_in_chi2 and FeH_sigma>0:
        chi2term= chi_squared(output_dict["FeH"],FeH_target,FeH_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_age_in_chi2 and age_sigma>0:
        chi2term= chi_squared(output_dict["age"],age_target,age_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_surface_Z_div_X_in_chi2 and surface_Z_div_X_sigma>0:
        chi2term= chi_squared(output_dict["surface_Z_div_X"],surface_Z_div_X_target,
                              surface_Z_div_X_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_surface_He_in_chi2 and surface_He_sigma>0:
        chi2term= chi_squared(output_dict["surface_He"],surface_He_target,
                              surface_He_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_Rcz_in_chi2 and Rcz_sigma>0:
        chi2term= chi_squared(output_dict["Rcz"],Rcz_target,Rcz_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_solar_cs_rms_in_chi2 and solar_cs_rms_sigma>0:
        chi2term= chi_squared(output_dict["cs_rms"],solar_cs_rms_target,solar_cs_rms_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    chi2= chi2sum/max(1,chi2N)
    return chi2

#old version, less modular, probably uses a bit less memory and computation time
#calculate chi^2 following Brandao et al, 2011, eqn 11
def tot_chi_squared_old(last_profile,history,sound_arr, targets_set=False, include_Teff_in_chi2=True,
                    include_logR_in_chi2 = False, include_logg_in_chi2 = False,
                    include_logL_in_chi2 = True, include_FeH_in_chi2 = False, 
                    include_age_in_chi2 = False, include_surface_Z_div_X_in_chi2 = False, 
                    include_surface_He_in_chi2 = True, include_Rcz_in_chi2 = True,
                    include_solar_cs_rms_in_chi2= True):
    if targets_set==False:
        targets_set=set_targets()
    
    surfaceX= max(history.surface_h1[-1],1e-10)
    surfaceHe = history.surface_he3[-1] + history.surface_he4[-1]
    surfaceZ =max(1e-99, min(1e0, 1 - (surfaceX + surfaceHe)))
    surface_Z_div_X = surfaceZ/surfaceX
    Z_div_X_solar = 0.02293e0
    
    
    chi2sum = 0
    chi2N = 0
    
    if include_Teff_in_chi2 and Teff_sigma>0:
        log_Teff =history.log_Teff[-1]
        Teff =10**log_Teff
        chi2term= chi_squared(Teff,Teff_target,Teff_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_logR_in_chi2 and logR_sigma>0:
        log_R =history.log_R[-1]
        chi2term= chi_squared(log_R,logR_target,logR_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_logg_in_chi2 and logg_sigma>0:
        log_g =history.log_g[-1]
        chi2term= chi_squared(log_g,logg_target,logg_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_logL_in_chi2 and logL_sigma>0:
        log_L =history.log_L[-1]
        chi2term= chi_squared(log_L,logL_target,logL_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
        
    if include_FeH_in_chi2 and FeH_sigma>0:
        FeH=np.log10(surface_Z_div_X/Z_div_X_solar)
        chi2term= chi_squared(FeH,FeH_target,FeH_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_age_in_chi2 and age_sigma>0:
        age =history.star_age[-1]
        chi2term= chi_squared(age,age_target,age_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_surface_Z_div_X_in_chi2 and surface_Z_div_X_sigma>0:
        chi2term= chi_squared(surface_Z_div_X,surface_Z_div_X_target,surface_Z_div_X_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_surface_He_in_chi2 and surface_He_sigma>0:
        chi2term= chi_squared(surfaceHe,surface_He_target,surface_He_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_Rcz_in_chi2 and Rcz_sigma>0:
        Rcz = history.cz_bot_radius[-1]
        chi2term= chi_squared(Rcz,Rcz_target,Rcz_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    if include_solar_cs_rms_in_chi2 and solar_cs_rms_sigma>0:
        cs_rms= calc_sound_rms(last_profile, sound_arr)
        chi2term= chi_squared(cs_rms,solar_cs_rms_target,solar_cs_rms_sigma)
        chi2sum= chi2sum + chi2term
        chi2N = chi2N + 1
    
    chi2= chi2sum/max(1,chi2N)
    return chi2
'''
model_output_loc ="LOGS/finalProfile_SSM.data"
last_prof=mr.MesaData(model_output_loc)
model_hist_loc="LOGS/historySSM.data"
hist= mr.MesaData(model_hist_loc)

sound_array=load_solar_cs_data()
chisq1=tot_chi_squared_old(last_prof,hist,sound_array)
chisq2=tot_chi_squared(last_prof,hist,sound_array)

out_dict= output_convert(last_prof,hist,sound_array)
chisq_dict=tot_chi_squared_dict(out_dict)
'''