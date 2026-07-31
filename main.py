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
import pytensor.tensor as pt
from arviz_base import load_arviz_data
import arviz_plots as azp
import os

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

# test_vals = synthetic_brems(np.array([100, 500, 1000, 2000, 3000, 4000]), 300)
# print("here:",test_vals)
#%%
time_step = [1.0,2.0,3.0,4.0]
fig,ax = plt.subplots()

for time in time_step:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(script_dir, 'dante_pchip', f'86455_time_{time}_spectrum.csv'))
    # print(df.columns.tolist())
    # print(df.head())
    
    given_PE = df['Energy (eV)'].values
    power_GW = df['Spectrum (Gw/sr/eV)'].values
    
    power_GW = np.maximum(power_GW, 0.0)
            
    #69 degrees
    area_h = np.pi * (0.6e-3)**2
    # area_h * np.cos(np.radians(69))
    power_W = power_GW * 1e9
    
    observed_data = np.pi * power_W / area_h
    print(observed_data)

    ax.plot(given_PE, observed_data, label=f"{time} ns")


ax.set_xlabel("Photon Energy (eV)")
ax.set_ylabel("Irradiance (W*m^2)")
ax.legend(frameon=False)
plt.show()



#%%


#df = pd.read_csv('86459_time_2.0_spectrum.csv')

# df = pd.read_csv('86459_time_1.5_spectrum.csv')
    
# df = pd.read_csv('86459_time_2.0_spectrum.csv')
    
time_step = [1.0,2.0,3.0]
# str(time_step)


compare_bb = []
compare_br = []


for time in time_step:
    df = pd.read_csv(f'dante_pchip/86455_time_{time}_spectrum.csv')
    # print(df.columns.tolist())
    # print(df.head())
    
    given_PE = df['Energy (eV)'].values
    power_GW = df['Spectrum (Gw/sr/eV)'].values
    
    power_GW = np.maximum(power_GW, 0.0)
            
    #69 degrees
    area_h = np.pi * (0.6e-3)**2
    # area_h * np.cos(np.radians(69))
    power_W = power_GW * 1e9
    
    observed_data = np.pi * power_W / area_h
    print(observed_data)
    
        
    scale_coef = np.max(observed_data)
    y_scaled = observed_data / scale_coef
    if __name__ == '__main__':
    
        '''creating prediction model'''
        
        with pm.Model() as Model:
            # x = pos_PE
            # y = y_scaled
            mask = given_PE > 100   
            x = given_PE[mask]
            y = y_scaled[mask]

            # test_model = synthetic_planckian(x, 100) + synthetic_brems(x, 170)
            # print("model magnitude:", np.max(test_model), np.min(test_model))
            # print("data magnitude (unscaled):", np.max(observed_data), np.min(observed_data))
                        
            T_guess = 150 #[eV]
            T_guess_brems = 300 #[eV]
            
            # T_dist = pm.TruncatedNormal('T', mu=T_guess, sigma=50, lower=5)
            # T_dist_brems = pm.TruncatedNormal('T_brems', mu=T_guess_brems, sigma=20, lower=5)
            
            log_T = pm.Normal('log_T', mu=np.log(T_guess), sigma=80)
            T_dist = pm.Deterministic('Blackbody_Temp', pm.math.exp(log_T))


            
            # log_T_brems = pm.Normal('log_T_brems', mu=np.log(T_guess_brems), sigma=200) #Uniform
            # log_T_brems = pm.Uniform('log_T_brems', lower=np.log(100), upper=np.log(600))
            # T_dist_brems = pm.Deterministic('Brems_Temp', pm.math.exp(log_T_brems))
            T_dist_brems = pm.Uniform('Brems_Temp', lower=500, upper=5000)            # log_amp = pm.Normal('log_amp', mu=0, sigma=10)
            # amp = pm.math.exp(log_amp)
            
            # log_amp_bb = pm.Uniform('log_amp_bb', lower=1, upper=10)
            # amp_bb = pm.Deterministic('amp_bb', pm.math.exp(log_amp_bb))
            
            # log_amp_br = pm.Uniform('log_amp_br', lower=1, upper=10)
            # amp_br = pm.Deterministic('amp_br', pm.math.exp(log_amp_br))
            
            model = synthetic_planckian(x,T_dist)
            model_brems = synthetic_brems(x,T_dist_brems) 
            
            model_bb_scaled = model / pt.max(model)
            model_br_scaled = model_brems / pt.max(model_brems)

                        
            # model_bb_scaled = amp_bb * model / pt.max(model)
            # model_br_scaled = amp_br * model_brems / pt.max(model_brems)
            
            model_both_scaled = model_bb_scaled + model_br_scaled
            noise = pm.HalfNormal('noise', sigma=300) #???*
            y_pred = pm.Normal('y_pred', mu=model_both_scaled, sigma=noise, observed=y)
            
            
            # model_both = model + model_brems
            # noise = pm.HalfNormal('noise', sigma=0.1) + 1e-5
            # model_both_scaled = amp * model_both / pt.max(model_both)
    
            # y_pred = pm.Normal('y_pred', mu=model_both_scaled, sigma=noise, observed=y) 
            
            
            rank = pm.sample(draws=2000, tune=1000, chains=4, cores=1,target_accept=0.95)
            
            #derives properties from metropolis
            data_mc = pm.to_inference_data(rank) #predicted probability distribution
            df = az.summary(data_mc, round_to=4) #prints out prediction of tru*e temp
            print(df)
            az.plot_rank(data_mc, var_names=['Blackbody_Temp', 'Brems_Temp', 'noise'])
            plt.tight_layout()
            plt.show() 
            estimate_bb_temp = float(df["mean"].loc["Blackbody_Temp"])
            estimate_br_temp = float(df["mean"].loc["Brems_Temp"])
            # estimate_amp_bb = float(df["mean"].loc["amp_bb"])
            # estimate_amp_br = float(df["mean"].loc["amp_br"])

            compare_bb.append(estimate_bb_temp)
            compare_br.append(estimate_br_temp)

            print(f"ESTIMATED TEMP BLACKBODY: {estimate_bb_temp}\nESTIMATED TEMP BREMS: {estimate_br_temp}")
            
            total_fit = synthetic_planckian(x, estimate_bb_temp) + synthetic_brems(x, estimate_br_temp)
            bb_fit = synthetic_planckian(x, estimate_bb_temp)
            br_fit = synthetic_brems(x, estimate_br_temp)
            
            # bb_fit_scaled = estimate_amp_bb * bb_fit / np.max(bb_fit)
            # br_fit_scaled = estimate_amp_br * br_fit / np.max(br_fit)
            bb_fit_scaled =   bb_fit / np.max(bb_fit)
            br_fit_scaled =   br_fit / np.max(br_fit)

            total_fit_scaled = bb_fit_scaled + br_fit_scaled
            
            
            hdi_vals = az.hdi(data_mc, var_names=["Blackbody_Temp", "Brems_Temp"], hdi_prob=0.94)
            print(hdi_vals)

            plt.scatter(x, y, c="C0", s=1, label="Total")

            plt.plot(x, total_fit_scaled, c="C0", ls="--", label="Total Fit")

            plt.plot(x, bb_fit_scaled, c="C1", ls="--", label="Blackbody Fit")
            
            plt.plot(x, br_fit_scaled, c="C2", ls="--", label="Brems Fit")


            plt.xlabel("Photon Energy (eV)")
            plt.ylabel("Irradiance ")
            plt.legend(frameon=False)
            plt.show()
            
            
            

            pc = azp.plot_dist(
                data_mc,
                kind="dot",
                var_names=["Blackbody_Temp", "Brems_Temp"],
                visuals={"point_estimate_text": False},
                stats={"dist": {"nquantiles": 200}},
                backend="matplotlib",
            )
            plt.show()

#%%

plt.scatter(time_step,compare_bb)
plt.xlabel("Time step (ns)")
plt.ylabel("Blackbody Temp (eV)")
plt.tight_layout()
plt.show()


plt.scatter(time_step,compare_br)
plt.xlabel("Time step (ns)")
plt.ylabel("Bremsstrahlung Temp (eV)")

plt.tight_layout()
plt.show()
    








