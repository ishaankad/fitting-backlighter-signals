# Estimation of the internal properties of a Hohlraum in an Inertial Confinement Fusion 

By Isha Ankad and Pawel Kozlowski
Institute of Computing in Research

Objective: This project is aimed at creating a model that can estimate the internal properties of a hohlraum (or blackbody) in an inertial confinement fusion. By using data collected from an x-ray spectrometer, the model is able to separate and fit a mixed signal, consisting of blackbody and bremsstrahlung radiation (noise), and estimate its properties using MCMC algorithms.  

## How to Start:
Terminal commands for Linux OS
### 1. Clone Repo & Set-up:
```
git clone https://github.com/ishaankad/fitting-backlighter-signals.git
cd fitting-backlighter-signals
```

### 2. Package Installation via Miniconda:
Conda package manager will be used in installing python libraries via Miniconda bootstrap installer. Libraries: `numpy`, `pandas`, `pymc`, `arviz`, `matplot`. Installing these libraries in a python virtual environment is recommended in preventing system-level dependency conflicts. 
```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
rm miniconda.sh
```

```
$HOME/miniconda/bin/conda init bash
source ~/.bashrc
```

```
# creating virtual env and installing packages
conda create -c conda-forge -n planck-env pymc matplotlib numpy pandas arviz -y
```

Instructions to activate Conda env:
```
conda activate fitting-planckian-env
```
### 3. Run the model:
```
python fitting_planckian.py
```







