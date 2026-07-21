#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 11:49:44 2026

@author: isha
"""

"""Goal: Derive true temperatures from bremsstrahlung and blackbody radiation recieved by an icf spectrographic device"""

#importing all the libs
import numpy as np
import matplotlib.pyplot as plt
import pymc as pm
#import pandas as pd
import arviz as az
#import default_style
from sklearn.metrics import r2_score

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
e = 1.60e-19 #electron charge [C]
m_e = 9.11e-31 #electron mass [kg]
n_e = 10e+30 #electron density n_e = (Z*)(n_i) if Z* is +1, n_e = n_i; [m^-3]
n_i = n_e #ion density [m^-3]
Z = 1 #average ionization is +1; full ionized Hydrogen ions in D-T fuel []
I_h = 2.18e-18 #Hydrogen ionization energy [J]
D = 1 # 0.6 - 5 meters [m]
V = 1e-13 #[m^3]


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
    charge_conv = ((e**2) / (4 * np.pi * perm))**3
    n1 = (32 * np.pi * (charge_conv)) / (3 * m_e * (c**3))
    n2 = ((2 * np.pi) / (3 * m_e * k_b * T))**0.5    
    e_power = (h * freq)/(k_b * T)
    n3 = ((Z**2) * n_e * n_i) / (np.exp(e_power))
    gaunt_factor = 1 + (0.1728) * (((h * freq)/(I_h * (Z**2))) ** (1/3)) * (1 + ((2 * k_b * T) / (h * freq)))
    j = (n1*n2*n3*gaunt_factor)/(4*np.pi)
    irr_brems = (j*V)/(D**2)
    return irr_brems
 
Data_true = synthetic_planckian(given_PE, T_true)
Data_true_brems = synthetic_brems(given_PE, T_true_brems)


#%%


observed_data = Data_true + Data_true_brems
#%%
plt.plot(given_PE, observed_data, label="total")
plt.plot(given_PE, Data_true, label="Blackbody")
plt.plot(given_PE, Data_true_brems, label="Brems")



plt.xlabel("Photon Energy (eV)")
plt.ylabel("Irradiance ()")
plt.legend(frameon=False)
plt.show()
#%%
snr_levels = np.arange(5, 31, 5) 
signal_power = np.mean(observed_data ** 2)
r2_vals = []


if __name__ == '__main__':
    for snr in snr_levels:
    
        noise_power = signal_power / snr 
        std_dev = np.sqrt(noise_power) 
        noise = np.random.normal(0, std_dev, size=given_PE.shape) 
        noisy_data = observed_data + noise
        
        scale_coef = np.max(noisy_data)
        y_scaled = noisy_data/scale_coef


        '''creating prediction model'''
        fig, ax = plt.subplots(figsize=(12, 5)) #
        with pm.Model() as Model:
            x = given_PE
            y = y_scaled
            
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
            #az.plot_trace(data_mc) #plots the distribution of data_mc
            
        estimate_bb_temp = float(df["mean"].loc["T"])
        estimate_br_temp = float(df["mean"].loc["T_brems"])
        blackbody_fit = synthetic_planckian(given_PE, estimate_bb_temp)
        brems_fit = synthetic_brems(given_PE, estimate_br_temp)
        total_fit = blackbody_fit + brems_fit


        post = az.extract(trace)
        r2 = r2_score(observed_data,total_fit)
        r2_vals.append(r2)
        mse_vals = np.mean((observed_data - total_fit) ** 2)

    
# # %% Title
r2_vals = np.log(np.abs(r2_vals))
plt.plot(snr_levels, r2_vals)
plt.set_title("$$R^2 values over varying noise$$")

plt.plot(snr_levels, mse_vals)
plt.set_title("MSE values over varying noise")

# plt.scatter(given_PE, observed_data,c="C0",s=1, label="total")
# plt.plot(given_PE, total_fit,c="C0",ls="--", label="fit_total")


# plt.scatter(given_PE, Data_true,c="C1" ,s=1,label=f"Blackbody T={T_true/11604:.0f} eV")
# plt.plot(given_PE, blackbody_fit,c="C1",ls="--", label=f"fit_blackbody T={estimate_bb_temp/11604:.0f} eV")


# plt.scatter(given_PE, Data_true_brems,c="C2",s=1, label=f"Brems T={T_true_brems/11604:.0f} eV")
# plt.plot(given_PE, brems_fit,c="C2",ls="--", label=f"fit_brems T={estimate_br_temp/11604:.0f} eV")


# plt.xlabel("Photon Energy (eV)")
# plt.ylabel("Irradiance ()")
# plt.legend(frameon=False)
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

