#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 11:49:44 2026

@author: isha
"""

"""Goal: Add noise to the model + Implement tests to see how noise changes sampling"""

#importing all the libs
import numpy as np
import matplotlib.pyplot as plt
import pymc as pm
#import pandas as pd
import arviz as az
#import default_style
from sklearn.metrics import r2_score

T_true = 150 # [eV]
T_true_brems = 100 # [eV]


'''creating planckian synthetic data'''

given_PE = np.linspace(1,2000,num=1000) # [eV]

#VARIABLES
h = 6.63e-34 # [J * s]
c = 3.00e8 # [m * s^-1]
k_b = 1.38e-23 # [J * K^-1]

def synthetic_planckian(photon_energy_ev, T):
    T_K = T*11604 #[K]
    #converting photon energy to frequency
    photon_energy_j = photon_energy_ev * 1.602e-19
    freq = photon_energy_j / h
    
    num = (2 * h * (freq**3)) / (c**2)
    e_power = (h * freq)/(k_b * T_K)
    den = np.exp(e_power)-1
    
    return num/den


'''Important note: i must convert the bremsstahlung data from emittivity to irradiance prior to plotting it '''


#%%

def synthetic_brems(photon_energy_ev, T): # change formula
    T_K = T*11604 #[K]
    k_b_erg = 1.380649e-16  # erg/K
    m_e = 9.11e-28 #[g]
    c = 2.99e10 #[cm/sec]
    e_c = 4.80e-10 #[statC or esu]
    Z = 1 #VARY THIS VAL
    n_e = 1e21 #[cm^-3] VARY THIS VAL
    n_i = n_e/Z #[cm^-3] 
    E_p = photon_energy_ev/(6.24e11) #[erg]
    E_t = k_b_erg * T_K #[erg]
    I_h = 2.18e-11 #[erg]
    V = 1e3 #[cm^3] DOUBLE CHECK
    D = 100 #[cm] DOUBLE CHECK
    
    term1 = (8/3)*(((2*np.pi) / (3*m_e*k_b*T)) ** 0.5)
    term2 = (e_c**6) / (m_e * (c**3))
    term3 = (Z**2)*n_e*n_i
    term4 = np.exp(-E_p / E_t)
    gaunt_factor = 1 + (0.1728) * (((E_p)/(I_h * (Z**2))) ** (1/3)) * (1 + ((2 * E_t) / (E_p)))
    j = (term1 * term2 * term3 * term4 * gaunt_factor)
    irr_cgs = (j*V)/(D**2)
    irr_si = irr_cgs*1e-3
    return irr_si
 
Data_true = synthetic_planckian(given_PE, T_true)
Data_true_brems = synthetic_brems(given_PE, T_true_brems)

#%%

observed_data = Data_true + Data_true_brems

#%%
# plt.plot(given_PE, observed_data, label="total")
# plt.plot(given_PE, Data_true, label="Blackbody")
# plt.plot(given_PE, Data_true_brems, label="Brems")



# plt.xlabel("Photon Energy (eV)")
# plt.ylabel("Irradiance ()")
# plt.legend(frameon=False)
# plt.show()
#%%
snr_levels = np.arange(5, 31, 5) 

signal_power = np.mean(observed_data ** 2)
r2_vals = []
mse_vals = []
if __name__ == '__main__':
    for snr in snr_levels:
    
        noise_power = signal_power / snr 
        std_dev = np.sqrt(noise_power) 
        noise = np.random.normal(0, std_dev, size=given_PE.shape) 
        noisy_data = observed_data + noise
        
        scale_coef = np.max(noisy_data)
        y_scaled = noisy_data/scale_coef


        '''creating prediction model'''
        with pm.Model() as Model:
            x = given_PE
            y = y_scaled
            
            T_guess = 100 #[eV]
            T_guess_brems = 80 #[eV]
            
            T_dist = pm.TruncatedNormal('T', mu=T_guess, sigma=50, lower=5)
            T_dist_brems = pm.TruncatedNormal('T_brems', mu=T_guess_brems, sigma=20, lower=5)
            
            model = synthetic_planckian(x,T_dist)
            model_brems = synthetic_brems(x,T_dist_brems) 
            
            model_both = model + model_brems
            noise = pm.HalfNormal('noise', sigma=0.1) + 1e-5
            model_both_scaled = model_both/scale_coef
            # noise = pm.HalfNormal('noise', sigma=1e13) #accepts positive values around 0
            y_pred = pm.Normal('y_pred', mu=model_both_scaled, sigma=noise, observed=y) 
            
            # step_T = pm.Metropolis(vars=[T_dist])
            # step_T_brems = pm.Metropolis(vars=[T_dist_brems])        
            # step_noise = pm.Metropolis(vars=[noise])
            
            trace = pm.sample(draws=2000, tune=1000, chains=4, cores=1,target_accept=0.95)
            
            #derives properties from metropolis
            data_mc = pm.to_inference_data(trace) #predicted probability distribution
            df = az.summary(data_mc, round_to=4) #prints out prediction of true temp
            print(df)
            az.plot_trace(data_mc, combined=True)
            plt.tight_layout()
            plt.show() #plots the distribution of data_mc

            
        estimate_bb_temp = float(df["mean"].loc["T"])
        estimate_br_temp = float(df["mean"].loc["T_brems"])
        blackbody_fit = synthetic_planckian(given_PE, estimate_bb_temp)
        brems_fit = synthetic_brems(given_PE, estimate_br_temp)
        total_fit = blackbody_fit + brems_fit


        post = az.extract(trace)
        r2 = r2_score(observed_data,total_fit)
        r2_vals.append(r2)
        mse_vals.append(np.mean((observed_data - total_fit) ** 2))

    
# # %% Title
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))


r2_vals = np.log(np.abs(r2_vals))
ax1.plot(snr_levels, r2_vals)
ax1.set_xlabel("Signal:Noise Ratio")
ax1.set_ylabel("R^2 Values")
ax1.set_title("R^2 values over varying noise")

ax2.plot(snr_levels, mse_vals)
ax2.set_xlabel("Signal:Noise Ratio")
ax2.set_ylabel("MSE Values")
ax2.set_title("MSE values over varying noise")
plt.tight_layout()
plt.show()
plt.scatter(given_PE, observed_data,c="C0",s=1, label="total")
plt.plot(given_PE, total_fit,c="C0",ls="--", label="fit_total")


plt.scatter(given_PE, Data_true,c="C1" ,s=1,label=f"Blackbody T={T_true:.0f} eV")
plt.plot(given_PE, blackbody_fit,c="C1",ls="--", label=f"fit_blackbody T={estimate_bb_temp:.0f} eV")


plt.scatter(given_PE, Data_true_brems,c="C2",s=1, label=f"Brems T={T_true_brems:.0f} eV")
plt.plot(given_PE, brems_fit,c="C2",ls="--", label=f"fit_brems T={estimate_br_temp:.0f} eV")


plt.xlabel("Photon Energy (eV)")
plt.ylabel("Irradiance ()")
plt.legend(frameon=False)
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

