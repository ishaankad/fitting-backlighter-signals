#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 11:49:44 2026

@author: isha
"""

"""Goal: """

import numpy as np
import matplotlib.pyplot as plt
import pymc as pm
#import pandas as pd
import arviz as az

T_true = 5000 #some true temperature units [K]

'''creating planckian synthetic data'''

given_PE = np.linspace(.1,5,num=1000) #units [eV]

#variables
#B = intensity units [W * sr^-1 * m^-2 * Hz^-1]
h = 6.63e-34 #units [J * s]
c = 3.00e8 #units [m * s^-1]
k_b = 1.38e-23 #units [J * K^-1]

def synthetic_planckian(photon_energy_ev, T):
    #converting photon energy to frequency
    photon_energy_j = photon_energy_ev * 1.602e-19
    freq = photon_energy_j / h
    num = (2 * h * (freq**3)) / (c**2)
    frac = (h * freq)/(k_b * T)
    den = np.exp(frac)-1
    return num/den
 
Data_true = synthetic_planckian(given_PE, T_true)


'''creating prediction model'''
if __name__ == '__main__':
    fig, ax = plt.subplots(figsize=(12, 5))
    with pm.Model() as Model:
        x = given_PE
        y = Data_true
        T_guess = 3268 #K
        T = pm.Normal('T', mu=T_guess, sigma=1000)
        model = synthetic_planckian(x,T)
        noise = pm.HalfNormal('noise', sigma=1e-5)
        y_pred = pm.Normal('y_pred', mu=model, sigma=noise, observed=y)
        step_T = pm.Metropolis(vars=[T])
        step_noise = pm.Metropolis(vars=[noise])
        trace = pm.sample(draws=2000, tune=1000, chains=4, step=[step_T,step_noise])
        
        
        data_mc = pm.to_inference_data(trace)
        print(az.summary(data_mc, round_to=4))
        az.plot_trace(data_mc)
        
    
    
    plt.plot(given_PE, Data_true,color='pink') #true
    plt.show()

