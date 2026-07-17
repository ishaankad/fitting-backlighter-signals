Note: all is to be updated with more code progress

## Overview

My model estimates temperature and other properties of the hohlraum/blackbody in an inertial confinement fusion. The model uses Metropolis MCMC algorithm to estimate these properties given synthetically generated 'measured data'.


## Introduction 

What is an Inertial Confinement Fusion?

Let's touch the surface of the physics aspect. An intertial confinment fusion is the fusion between deutrium gas particles. The process requires extremely high powered lasers confined into a very small container (a hohlraum) that acts as a filter to let through high intensity x-ray beams. These beams, now inside the hohlraum, make contact with a second container (a capsule) with enough pressure so that it implodes (self-explodes?) which creates enough pressure for the gas within this second container to have its electrostatic bonds broken, allowing for a fusion between atoms.

The objective of my model is to derive properties from the hohlraum, the container that filters laser beams. This is done by a backlighter-spectrometer system. Essentialy, a subset of lasers divert their path and are aimed at a backlighter instead of the hohlraum. Being made of the same blackbody properties as a hohlraum, the backlighter lets through x-rays from the lasers, which are intentionally aimed at the hohlraum. The unabsorbed radiance is recieved by a reciever (spectrometer) past the hohlraum, recording information to be used in estimating properties of the hohlraum. 

The spectrometer also recieves a significant amount of non-blackbody radiation, known as the bremsstrahlung radiation, which cannot be dismissed. The model derives the property of this noise on its own. Its produced from the extreme intensities in the hohlraum, which allow for solid to plasma transitions, producing ion-electron interactions, and thus, creating bremsstrahlung radiation. 

We segregate the two radiations to derive properties from each of them by using prior knowledge of which intensities these radiations occur at. In this model, such knowledge can be derived from Planck's law for blackbody radiation and bremsstrahlung radiation. Planck's law shows how much energy is emitted by a blackbody, given a temperature. 


## Physics Model




Planck's law for measuring Blackbody Radiation:



$$B(\nu, T) = \frac{2h\nu^3}{c^2 \left(e^{\frac{h\nu}{k_B T}} - 1\right)}$$

Thermal Bremsstrahlung Equation:



$$I(\nu) = \frac{A \cdot 2h\nu^3}{c^2} \cdot \frac{1}{e^{\frac{h\nu}{k_B T}}}$$


## Bayesian Statistics

Metropolis Markov Chain Monte Carlo:

The ratio between the probability densities between the two creates a clean acceptance value $$alpha$$. Thereby, the chance of this draw being accepted or not becomes $$alpha$$.

Burn-ins are the inital set of draws that are discarded as they are used in bringing out the algorithm to a spot where we can draw probable samples that are useful. This way our collection of samples contains less error and is more concentrated towards the true parameter.

## Methodology

Generating True Probability:

I set true parameters, such as temperature, the value my model is to guess, in their appropriate ranges. The holhraum reaches millions of Kelvin, so it will be more convenient to look at Temperature in units of electronvolts, allowing for more readable values.

After defining my variables and true parameters, I calculate irradiances of blackbody and bremsstrahlung radiations. I superpose both arrays across a range of photon energies, and pass it into py.Model()


The model takes in this irradiance as "observed data". 

Takes in a prior belief for parameter $$theta$$, whose likelihood is presented to be P($$theta$$). The model takes this prior, in this case temperture, and calculates the irradiance using the Planck's law for the guess temperture of the Blackbody and Bremsstrahlung equation for the guess temperature of the Bremsstrahlung respecitvely. The model uses Metropolis MCMC algorithm to measure how much the guess combination of irradiance deviates from the passed-in/given irradiance. The deviation between these curves is what allows the algorithm to set the degree to which it should accept the draw as a sample. MCMC's role in the process of generating samples using prior data. Thereby, the next draw will be sampled from the normalization distribution of the last accepted sample. Like so, the algorithm will draw samples for 4 independent chains, with 2000 draws, and a thousand burn-ins.



# Advancements I want to make:
- Update the bremsstrahlung equation
- Add noise to the observed data
- Create a signal to noise ratio: signal(observed)/amplitude of the noise vs. Measurement of fit accurancy
- Examples of fit accuracy: R^2 value or Difference between estimate and true value *pymc library
- Rename variables
- Play with temperature and other input parameters/come up with and test different scenarios and models
- Indtroduce the dante noise/real
- Chapters: pg. 48 9.132 (first e corresponds to electron charge), 9.134,
- Interrelated variables:
-  Z* = Average ionization (average of the ion charges)
-  n_e = electron density (# of electrons per cm^3)
-  n_i = ion density













