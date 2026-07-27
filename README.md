# Estimation of the internal properties of a Hohlraum in an Inertial Confinement Fusion 

By Isha Ankad and Pawel Kozlowski

Institute of Computing in Research

Objective: This project is aimed at creating a model that can estimate the internal properties of a hohlraum (or blackbody) in an inertial confinement fusion. By using data collected from an x-ray spectrometer, the model is able to separate and fit a mixed signal, consisting of blackbody and bremsstrahlung radiation (noise), and estimate its properties using MCMC algorithms.  

## How to Start:
Terminal commands for Linux OS
### 1. Clone Repo & Set-up:
```
git clone https://github.com/ishaankad/fitting-backlighter-signals.git
```

### 2. Create a venv & install packages:
Pip package manager will be used in installing python libraries. Libraries: `numpy`, `pandas`, `pymc`, `arviz`, `matplot`. Installing these libraries in a python virtual environment is recommended in preventing system-level dependency conflicts. 
```
python3 -m venv .venv
```
Acivate your virtual environment:
```
source .venv/bin/activate
```
Install the required packages:
```
pip install --upgrade pip
pip install pymc matplotlib numpy pandas arviz
```
### 3. Run the model:
```
cd fitting-backlighter-signals/
python3 main.py
```







