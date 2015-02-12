from astropy import units as u
import numpy as np 

ra_targ = 278.389583
dec_targ = -10.568528 

coordinates= {
				'1230': [278.38678693465,-10.573081378866],
				'1433':[278.39353079353,-10.589528953519],
				'1233':[278.37551782795,-10.593500425816],
				'159':[278.38680336177, -10.573076999136]
				}

def calculate_deg_distance(obsid):
	offset = list(coordinates[str(obsid)])
	ra_dif = ra_targ - offset[0]
	dec_dif = dec_targ - offset[1]
	ra_dif *= u.deg
	dec_dif *= u.deg 
	return np.sqrt(ra_dif**2 + dec_dif**2)
	# ra_distance = ra_dif.to(u.rad).value*(5*u.kpc)
	# dec_distance = dec_dif.to(u.rad).value*(5*u.kpc)
	# sep = np.sqrt(ra_distance**2 + dec_distance**2)
	# return sep

for key in coordinates.keys():
	print("{}:".format(key))
	print(calculate_deg_distance(key))


