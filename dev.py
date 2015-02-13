"""
Right now I can group the files given in the ciao tutorial using this script
I can't seem to make this work for any other observations.
"""
from Spectral import Spectral
from Spectral import reproject

obsids = [1233,1230,159,1433]
obsids1 = [1230,1433]
obsids2 = [1842,1843]

def main():
	# reproject(obsids1)
	objectoid = Spectral(obsids1,reproj_dir="reproj13-02-2015")
	objectoid.create_spectra()
	# objectoid.graph_spectra(groupcounts=25)
	# objectoid.normal_fit(plot=True)

main()