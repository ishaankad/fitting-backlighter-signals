#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 11:49:44 2026

@author: isha
"""

"""Goal: Add noise to the model + Implement tests to see how noise changes sampling"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pymc as pm
import arviz as az
#import default_style
#from sklearn.metrics import r2_score
# from trial_noise import synthetic_planckian,synthetic_brems


#%%



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
    V = 1e3
    D = 1
    B = ((num/den) * V)/(D**2)
    return B


'''Important note: i must convert the bremsstahlung data from emittivity to irradiance prior to plotting it '''


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
 

#%%



#df = pd.read_csv('86459_time_2.0_spectrum.csv')

# df = pd.read_csv('86459_time_1.5_spectrum.csv')
    
# df = pd.read_csv('86459_time_2.0_spectrum.csv')
    
time_step = [1.0,1.5,2.0,2.5,3.0,3.5]
str(time_step)

fig,ax = plt.subplots()

for time in time_step:
    df = pd.read_csv(f'86459_time_{time}_spectrum.csv')
    print(df.columns.tolist())
    print(df.head())
    
    given_PE = df['Energy (eV)'].values
    power_GW = df['Spectrum (Gw/sr/eV)'].values
    
    power_GW = np.maximum(power_GW, 0.0)
            
    #69 degrees
    area_h = np.pi * (0.6e-3)**2
    area_h * np.cos(np.radians(69))
    power_W = power_GW * 1e9
    
    observed_data = np.pi * power_W / area_h
    print(observed_data)
    
    ax.plot(given_PE, observed_data, label=f"{time} ns")
        
    scale_coef = np.max(observed_data)
    y_scaled = observed_data / scale_coef
    if __name__ == '__main__':
    
        '''creating prediction model'''
        with pm.Model() as Model:
            # x = pos_PE
            # y = y_scaled
            mask = given_PE > 0.5   
            x = given_PE[mask]
            y = y_scaled[mask]
            T_guess = 100 #[eV]
            T_guess_brems = 170 #[eV]
            
            T_dist = pm.TruncatedNormal('T', mu=T_guess, sigma=50, lower=5)
            T_dist_brems = pm.TruncatedNormal('T_brems', mu=T_guess_brems, sigma=20, lower=5)
            
            model = synthetic_planckian(x,T_dist)
            model_brems = synthetic_brems(x,T_dist_brems) 
            
            model_both = model + model_brems
            noise = pm.HalfNormal('noise', sigma=0.1) + 1e-5
            model_both_scaled = model_both/scale_coef
    
            y_pred = pm.Normal('y_pred', mu=model_both_scaled, sigma=noise, observed=y) 
            
            
            trace = pm.sample(draws=2000, tune=1000, chains=4, cores=1,target_accept=0.95)
            
            #derives properties from metropolis
            data_mc = pm.to_inference_data(trace) #predicted probability distribution
            df = az.summary(data_mc, round_to=4) #prints out prediction of true temp
            print(df)
            az.plot_trace(data_mc, combined=True)
            plt.tight_layout()
            plt.show() 

ax.set_xlabel("Photon Energy (eV)")
ax.set_ylabel("Irradiance ()")
ax.legend(frameon=False)
plt.show()


#%%


    








