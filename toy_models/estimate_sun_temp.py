import numpy as np

#Loading data
data = np.loadtxt('whi_ref_spectra.txt',delimiter = ',')

mean = np.mean(data[:,1])

x_index = np.abs(data[:,1]-mean).argmin()

#define variables:
h = 6.63e-34
c = 3.00e8
k = 1.38e-23

x = data[x_index,0]
x = (h*c)/x # wavelength -> photon energy (joules)
x = x / 1.602e-19 #joules -> eV
y = data[x_index,1]

def est_temp(e,i):

    #convert eV -> joules
    e = e * 1.602e-19
    log_in = (2 * np.pi * (e**3)) / ((h**3) * i * (c**2))
    temp = (e) / (k*np.log(log_in+1))
    return temp

print("temperature of the sun:", est_temp(x,y))

#output: 
#temperature of the sun: 1.0560338515721844e-05




