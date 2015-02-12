from Spectral import Spectral
from Spectral import reproject

obsids = [1233,1230,159,1433]
obsids1 = [1233,159]
def main():
	# reproject(obsids1)
	objectoid = Spectral(obsids1,reproj_dir="reproj12-02-2015")
	objectoid.create_spectra()
	# objectoid.graph_spectra(groupcounts=25)
	# objectoid.normal_fit(plot=True)

main()