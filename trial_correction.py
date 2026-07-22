#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 09:16:50 2026

@author: isha
"""

"""Goal: Correcting sampling; the equation is off?"""

#importing all the libs
import numpy as np
import matplotlib.pyplot as plt
import pymc as pm
#import pandas as pd
import arviz as az
#import default_style

T_true = 150*11604 #setting a true temperature units [K]
T_true_brems = 100*11604 #setting a true temperature units [K]


'''creating planckian synthetic data'''

given_PE = np.linspace(1,2000,num=1000) #units [eV]

#VARIABLES
#B = intensity units [W * sr^-1 * m^-2 * Hz^-1]
h = 6.63e-34 #units [J * s]
c = 3.00e8 #units [m * s^-1]
k_b = 1.38e-23 #units [J * K^-1]

#specific for Bremss
perm = 8.85e-12 #permitivity [F * J^-1]
q = 1.60e-19 #electron charge [C]
m_e = 9.11e-31 #electron mass [kg]
Z = 1 #average ionization is +1; full ionized Hydrogen ions in D-T fuel []
n_e = 3e+32 #electron density n_e = (Z*)(n_i) if Z* is +1, n_e = n_i; [m^-3] #adjusting val to see curve
n_i = n_e/Z #ion density [m^-3]
I_h = 2.18e-18 #Hydrogen ionization energy [J]
D = 1 # 0.6 - 5 meters [m]
V = 6.28e-12 #[m^3] #adjusting val to see curve


def synthetic_planckian(photon_energy_ev, T):
    #converting photon energy to frequency
    photon_energy_j = photon_energy_ev * 1.602e-19
    freq = photon_energy_j / h
    
    num = (2 * h * (freq**3)) / (c**2)
    e_power = (h * freq)/(k_b * T)
    den = np.exp(e_power)-1
    
    return num/den


'''Important note: i must convert the bremsstahlung data from emittivity to irradiance prior to plotting it '''


#%%

def synthetic_brems(photon_energy_ev, T): # change formula
    photon_energy_j = photon_energy_ev * 1.602e-19
    freq = photon_energy_j / h
    
    coulomb_factor = ((q**2) / (4 * np.pi * perm)) ** 3
    term1 = (8/3)*(((2*np.pi) / (3*m_e*k_b*T)) ** 0.5)
    term2 = (coulomb_factor) / (m_e * (c**3))
    term3 = (Z**2)*n_e*n_i
    term4 = np.exp((-h * freq) / (k_b * T))
    gaunt_factor = 1 + (0.1728) * (((h * freq)/(I_h * (Z**2))) ** (1/3)) * (1 + ((2 * k_b * T) / (h * freq)))
    j = (term1 * term2 * term3 * term4 * gaunt_factor)
    return (j*V)/(D**2)
 
Data_true = synthetic_planckian(given_PE, T_true)
Data_true_brems = synthetic_brems(given_PE, T_true_brems)


#%%


observed_data = Data_true + Data_true_brems
# #%%
plt.plot(given_PE, observed_data, label="total")
plt.plot(given_PE, Data_true, label="Blackbody")
plt.plot(given_PE, Data_true_brems, label="Brems")



plt.xlabel("Photon Energy (eV)")
plt.ylabel("Irradiance ()")
plt.legend(frameon=False)
plt.show()
#%%



if __name__ == '__main__':

    '''creating prediction model'''
    #fig, ax = plt.subplots(figsize=(12, 5)) #
    with pm.Model() as Model:
        x = given_PE
        y = observed_data
        
        T_guess = 100*11604 #K
        T_guess_brems = 80*11604 #K
        
        T_dist = pm.Normal('T', mu=T_guess, sigma=50*11604)
        T_dist_brems = pm.Normal('T_brems', mu=T_guess_brems, sigma=20*11604)
        
        model = synthetic_planckian(x,T_dist)
        model_brems = synthetic_brems(x,T_dist_brems) 
        
        model_both = model + model_brems
        
        noise = pm.HalfNormal('noise', sigma=1e13) #accepts positive values around 0
        y_pred = pm.Normal('y_pred', mu=model_both, sigma=noise, observed=y) 
        
        step_T = pm.Metropolis(vars=[T_dist])
        step_T_brems = pm.Metropolis(vars=[T_dist_brems])        
        step_noise = pm.Metropolis(vars=[noise])
        
        trace = pm.sample(draws=2000, tune=1000, chains=4, cores=1,step=[step_T,step_T_brems, step_noise])
        
        #derives properties from metropolis
        data_mc = pm.to_inference_data(trace) #predicted probability distribution
        df = az.summary(data_mc, round_to=4) #prints out prediction of true temp
        print(df)
        # fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 6))
        #az.plot_trace(data_mc)
        #plt.tight_layout()
        #plt.show() #plots the distribution of data_mc
        

    fig_custom, ax = plt.subplots(figsize=(8, 5))
 #%% Title
    estimate_bb_temp = float(df["mean"].loc["T"])
    estimate_br_temp = float(df["mean"].loc["T_brems"])
    blackbody_fit = synthetic_planckian(given_PE, estimate_bb_temp)
    brems_fit = synthetic_brems(given_PE, estimate_br_temp)
    total_fit = blackbody_fit + brems_fit
    
    ax.scatter(given_PE, observed_data,c="C0",s=1, label="total")
    ax.plot(given_PE, total_fit,c="C0",ls="--", label="fit_total")
    
    
    ax.scatter(given_PE, Data_true,c="C1" ,s=1,label=f"Blackbody T={T_true/11604:.0f} eV")
    ax.plot(given_PE, blackbody_fit,c="C1",ls="--", label=f"fit_blackbody T={estimate_bb_temp/11604:.0f} eV")
    
    
    ax.scatter(given_PE, Data_true_brems,c="C2",s=1, label=f"Brems T={T_true_brems/11604:.0f} eV")
    ax.plot(given_PE, brems_fit,c="C2",ls="--", label=f"fit_brems T={estimate_br_temp/11604:.0f} eV")
    
    
    ax.set_xlabel("Photon Energy (eV)")
    ax.set_ylabel("Irradiance ()")
    ax.legend(frameon=False)
    plt.tight_layout()
    plt.show()




#%%

'''
    resources:
        * https://github.com/DmitryRyumin/Awesome-Speech-Enhancement/blob/main/notebooks/SNR.ipynb
        * gemini
        * https://discourse.pymc.io/t/customize-proposal-distribution-in-pm-metropolis-for-multivariables/14781
        * https://scikit-learn.org/stable/modules/generated/sklearn.metrics.r2_score.html
        * Foundations of High Energy Density Physics Jon Larsen

'''
