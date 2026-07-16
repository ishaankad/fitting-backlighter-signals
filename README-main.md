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

















