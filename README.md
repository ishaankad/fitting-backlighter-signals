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

### 2. Package Installation via Miniconda:
Conda package manager will be used in installing python libraries via Miniconda bootstrap installer. Libraries: `numpy`, `pandas`, `pymc`, `arviz`, `matplot`. Installing these libraries in a python virtual environment is recommended in preventing system-level dependency conflicts. 
```
mkdir -p ~/miniconda3 && cd "$_"
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
```
```
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
# Once you run the .sh file, it is no longer needed
rm -rf ~/miniconda3/miniconda.sh
```
```
source ~/miniconda3/bin/activate
~/miniconda3/bin/conda init bash
```
Accept terms of service:
```
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
```
Creating virtual env and installing packages:
```
conda create -c conda-forge -n planck-env pymc matplotlib numpy pandas arviz -y
```
Instructions to activate Conda env:
```
conda activate fitting-planckian-env
```
### 3. Run the model:
```
cd fitting-backlighter-signals/
python3 main.py
```







