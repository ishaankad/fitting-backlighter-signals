#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 11:49:44 2026

@author: isha
"""

"""Goal: Derive true temperatures from bremsstrahlung and blackbody radiation recieved by an icf spectrographic device"""
'''note: all Bremsstrahlung radiation properties will be denoted with 'ss' sufix'''

#importing all the libs
import numpy as np
import matplotlib.pyplot as plt
import pymc as pm
#import pandas as pd
import arviz as az

T_true = 5000 #setting a true temperature units [K]
T_true_brems = 1000 #setting a true temperature units [K]


'''creating planckian synthetic data'''

given_PE = np.linspace(.1,5,num=1000) #units [eV]

#variables
#B = intensity units [W * sr^-1 * m^-2 * Hz^-1]
h = 6.63e-34 #units [J * s]
c = 3.00e8 #units [m * s^-1]
k_b = 1.38e-23 #units [J * K^-1]
A = 0.5

def synthetic_planckian(photon_energy_ev, T):
    #converting photon energy to frequency
    photon_energy_j = photon_energy_ev * 1.602e-19
    freq = photon_energy_j / h
    num = (2 * h * (freq**3)) / (c**2)
    frac = (h * freq)/(k_b * T)
    den = np.exp(frac)-1
    return num/den

def synthetic_brems(photon_energy_ev, T, A):
    photon_energy_j = photon_energy_ev * 1.602e-19
    freq = photon_energy_j / h
    num = (A * 2 * h * (freq**3)) / (c**2)
    frac = (h * freq)/(k_b * T)
    den = np.exp(frac)
    return num/den
 
Data_true = synthetic_planckian(given_PE, T_true)
Data_true_brems = synthetic_brems(given_PE, T_true_brems, A)

observed_data = Data_true + Data_true_brems

'''creating prediction model'''
if __name__ == '__main__': #prevents cores from reading whole file
    fig, ax = plt.subplots(figsize=(12, 5)) #
    with pm.Model() as Model:
        x = given_PE
        y = observed_data
        
        T_guess = 4000 #K
        T_guess_brems = 700 #K
        
        T_dist = pm.Normal('T', mu=T_guess, sigma=1000)
        T_dist_brems = pm.Normal('T_brems', mu=T_guess_brems, sigma=200)
        A_dist = pm.HalfNormal('A', sigma=1)
        
        model = synthetic_planckian(x,T_dist)
        model_brems = synthetic_brems(x,T_dist_brems,A_dist) 
        
        model_both = model + model_brems
        
        noise = pm.HalfNormal('noise', sigma=1e13) #accepts positive values around 0
        y_pred = pm.Normal('y_pred', mu=model_both, sigma=noise, observed=y) 
        
        step_T = pm.Metropolis(vars=[T_dist])
        step_T_brems = pm.Metropolis(vars=[T_dist_brems])        
        step_noise = pm.Metropolis(vars=[noise])
        step_A = pm.Metropolis(vars=[A_dist])
        
        trace = pm.sample(draws=2000, tune=1000, chains=4, step=[step_T,step_T_brems,step_A,step_noise])
        
        #derives properties from metropolis
        data_mc = pm.to_inference_data(trace) #predicted probability distribution
        print(az.summary(data_mc, round_to=4)) #prints out prediction of true temp
        az.plot_trace(data_mc) #plots the distribution of data_mc
        
    
    plt.plot(given_PE, Data_true,color='pink') #true
    plt.show()





 
