"""
2/12/2015 - Looking at this after a couple of months. Jesus what a mess! 
No documentation whatsoever. I need to go through this and shape shit up. 

This file assumes that you've already messed around with the .fits files, centering them 
and creating separate background files. This is present in the "longexp" folder. 

To do:
	- set this up so that I can simultaneously deal with single obsids 
	a list of obsids. I want to be able to group multiple obsids. 
	- could I set something up such that I automatically detect sources 
	thus automating the source/background creation process??

"""
import os
import sys
import subprocess
import time
import logging
# from tools import InOut
try:
	import sherpa.astro.ui as ui
	import pychips
except ImportError:
	print("you forgot to start ciao. Exiting")
	sys.exit()

fracexp = {'1233':0.964,'1230':0.9563,'159':0.9593,'1433':1.0}

obsids = [1233,1230,159,1433]

base_dir = os.path.abspath(os.path.dirname(__file__))
logs_dir = os.path.join(base_dir,'logs')

def reproject(obsids):
	"""
	obsids is a list/tuple containing the integer obsids. 
	"""

	filename_str = str()
	for index, obsid in enumerate(obsids):
		if index == len(obsids)-1:
			filename_str+=str(obsid)
		else:
			filename_str+=str(obsid)
			filename_str+=","
	subprocess.call("punlearn chandra_repro", shell=True)
	subprocess.call("chandra_repro indir={} mode=h clobber=yes".format(filename_str), shell=True)
	subprocess.call("punlearn reproject_obs", shell=True)
	subprocess.call("reproject_obs {} reproj{}/ clobber=yes".format(filename_str,time.strftime("%d-%m-%Y")), shell=True)
	
	# subprocess.call("punlearn chandra_repro", shell=True)
	# subprocess.call("punlearn chandra_repro", shell=True)

class Spectral(object):

	def __init__(self,obsid,**kwargs):
		"""
		if obsid is a str or int it will proceed with the single observation
		if obsid is a list, then it will group the two observations.
		**kwargs:
			- reproj_dir: This is for multiple obsids. This is the name of the reproject directory. 
			if not specified, it will ask  
		"""
		logfilename = os.path.join(logs_dir,"log{}-{}.log".format(time.strftime("%d-%m-%Y"),obsid))
		logger = logging.getLogger("sherpa")
		logging.basicConfig(level=logging.INFO, filename=logfilename, filemode="a")
		logging.info('\n\nStarted: {} {}'.format(time.strftime("%H:%M:%S"), time.strftime("%d/%m/%Y")))

		if isinstance(obsid, str) or isinstance(obsid, int):
			self.obsid = obsid
			if len(str(self.obsid)) == 4:
				self.file_name = "acisf0{}_repro_evt2.fits".format(self.obsid)
			elif len(str(self.obsid)) == 3:
				self.file_name = "acisf00{}_repro_evt2.fits".format(self.obsid)
			self.directory = "/home/dean/ciao-data/longexp/{}/repro".format(self.obsid)
			self.source_file = "first.reg"
			self.bkg_file = "first_bg.reg"

		elif isinstance(obsid, list):
			"""
			Here we assume that the observations have been "reprojected."
			we also assume that the user has extracted source and background region files.
			"""
			try:
				self.reproj_dir_abs = os.path.join(base_dir, kwargs['reproj_dir'])
				self.reproj_dir_rel = kwargs['reproj_dir']
			except KeyError:
				print("No reproject directory specified.")
				self.reproj_dir_rel = raw_input("Specify reproject directory. If left blank, defaulting to \"reproj\" ")
				if self.reproj_dir_rel == "":
					self.reproj_dir_abs = os.path.join(base_dir, "reproj")
					self.reproj_dir_rel = "reproj"
				else:
					self.reproj_dir_abs = os.path.join(base_dir,self.reproj_dir_abs)
			self.obsids = list(obsid)
			self.file_names = []
			for obsid in self.obsids:
				if len(str(obsid)) == 4:
					self.file_names.append("acisf0{}_repro_evt2.fits".format(obsid))
				elif len(str(obsid)) == 3:
					self.file_names.append("acisf00{}_repro_evt2.fits".format(obsid))
			self.directories = ["/home/dean/ciao-data/longexp/{}/repro".format(obsid) for obsid in self.obsids]
			# self.source_files = ["{}_src.reg".format(obsid) for obsid in self.obsids]
			# self.bkg_files = ["{}_bg.reg".format(obsid) for obsid in self.obsids]

	def create_spectra(self):
		"""
		This just runs a series of commands to extract the spectra of the observation in question.
		"""
		try:
			dummy = self.obsid
			os.chdir(self.directory)
			subprocess.call("punlearn specextract", shell=True)
			subprocess.call("pset specextract infile=\"{}[sky=region({})]\"".format(self.file_name,self.source_file), shell=True)
			subprocess.call("pset specextract outroot=spec", shell=True)
			subprocess.call("pset specextract bkgfile=\"{}[sky=region({})]\"".format(self.file_name,self.bkg_file), shell=True)
			subprocess.call("pset specextract weight=no correctpsf=yes", shell=True)
			subprocess.call("specextract clobber=yes",shell=True)
		except AttributeError:
			src_lis = os.path.join(self.reproj_dir_abs, 'multi_src.lis')
			bg_lis = os.path.join(self.reproj_dir_abs, 'multi_bg.lis')
			asp_lis = os.path.join(self.reproj_dir_abs, 'multi_asp.lis')
			mask_lis = os.path.join(self.reproj_dir_abs, 'multi_mask.lis')
			bpix = os.path.join(self.reproj_dir_abs, 'multi_bpix.lis')
			with open(src_lis, 'w') as src, open(bg_lis, 'w') as bg, open(asp_lis, 'w') as asp,open(mask_lis, 'w') as mask,open(bpix, 'w') as bpix:
				for obsid in self.obsids:
					src.write("{}_reproj_evt.fits[sky=region({}_src.reg)]\n".format(obsid,obsid))
					bg.write("{}_reproj_evt.fits[sky=region({}_bg.reg)]\n".format(obsid,obsid))
					asp.write("{}.asol\n".format(obsid))
					mask.write("{}.mask\n".format(obsid))
					bpix.write("{}.bpix\n".format(obsid))
			os.chdir(self.reproj_dir_abs)
			if os.path.isdir("spec"):
				pass
			else:
				os.mkdir("spec")
			subprocess.call("punlearn specextract",shell=True)
			subprocess.call("pset specextract asp=@multi_asp.lis",shell=True)
			subprocess.call("pset specextract mskfile=@multi_mask.lis",shell=True)
			subprocess.call("pset specextract badpixfile=@multi_bpix.lis",shell=True)
			subprocess.call("pset specextract infile=@multi_src.lis",shell=True)
			# subprocess.call("pset specextract asp=@multi_asp.lis",shell=True)
			extract_str = "pset specextract outroot="
			for index, obsid in enumerate(self.obsids):
				if index == len(self.obsids)-1:
					extract_str+="spec/{}".format(obsid)
				else:
					extract_str += "spec/{},".format(obsid)
			subprocess.call(extract_str,shell=True)
			subprocess.call("pset specextract bkgfile=@multi_bg.lis",shell=True)
			subprocess.call("specextract mode=h",shell=True)


	def graph_spectra(self,groupcounts=20):
		"""
		Graphs the spectra, with background subtracted.
		"""
		if not os.path.isfile(os.path.join(self.directory,"spec.pi")):
			print("You haven't generated spectra files!")
		else:
			os.chdir(self.directory)
			pi = "spec.pi"
			ui.load_data(pi)
			ui.notice(0.1, 10)
			ui.group_counts(groupcounts)
			ui.plot_data()
			ui.subtract()
			ui.plot_data(overplot=True)
			pychips.log_scale()
			pychips.set_preference("foreground.display", "black")
			pychips.set_preference("background.display", "white")
			pychips.set_current_plot("plot1")
			pychips.set_plot_title("Spectra for obsid {}".format(self.obsid))
			pychips.set_curve(['*.color', 'red'])
			raw_input(">> ")

	def background_total(self):
		os.chdir(self.directory)
		pi = "spec.pi"
		ui.load_data(pi)
		return ui.calc_data_sum(bkg_id=1), ui.calc_data_sum(id=1)

	def pileupcorrect(self,groupcounts=25):
		"""
		I was worried that there would be pileup effects in my chandra data.
		It ended up not being a big deal. This method calculates pileup effect. 
		"""
		pi = "spec.pi"
		os.chdir(self.directory)
		ui.load_pha(pi)
		ui.subtract()
		ui.notice(0.1,10)
		ui.group_counts(groupcounts)
		#ui.plot_data()
		ui.set_source(ui.xsphabs.abs1*ui.xspowerlaw.power1)
		ui.set_stat("chi2datavar")
		abs1.nH = 2.2
		ui.freeze(abs1.nH)
		ui.set_pileup_model(ui.jdpileup.jdp)
		jdp.f.min = 0.85
		jdp.ftime = 3.2 # run dmkeypar acisf01233_repro_evt2.fits EXPTIME echo+
		jdp.fracexp = fracexp[str(self.obsid)] # run dmkeypar spec.arf FRACEXPO echo+
		jdp.nterms = 30
		ui.set_method("neldermead")
		ui.fit()
		ui.set_conf_opt('sigma',1.6) #this makes it so I can access the 90% confidence values
		ui.conf()
		print(ui.get_pileup_model())

	def normal_fit(self,groupcounts=25,plot=False):
		"""
		This method calculates the normal power law fit. 
		"""
		pi = "spec.pi"
		os.chdir(self.directory)
		ui.load_data(pi)
		ui.subtract()
		ui.group_counts(groupcounts)
		ui.set_source(ui.xsphabs.abs1 * ui.xspowerlaw.pl)
		ui.set_stat("chi2datavar")
		abs1.nH = 2.2
		ui.freeze(abs1.nH)
		ui.fit()
		ui.set_conf_opt('sigma',1.6) #this is so I can see 90% confidence values 
		ui.conf()
		if plot == True:
			ui.plot_fit_delchi()
			pychips.log_scale(pychips.X_AXIS)
			pychips.set_current_plot("plot1")
			pychips.set_plot_title("Power Law Fit for obsid {}".format(self.obsid))
			pychips.limits(pychips.X_AXIS,0.1,10)
			raw_input(">> ")
		else:
			pass

	def broken_fit(self,groupcounts=25,plot=False):
		"""
		This method calculates the broken power law fit. 
		"""
		pi = "spec.pi"
		os.chdir(self.directory)
		ui.load_data(pi)
		ui.subtract()
		ui.group_counts(groupcounts)
		ui.set_source(ui.xsphabs.abs1 * ui.xsbknpower.pl)
		ui.set_stat("chi2datavar")
		abs1.nH = 2.2
		ui.freeze(abs1.nH)
		ui.fit()
		ui.set_conf_opt('sigma',1.6) #this is so I can see 90% confidence values 
		ui.conf()
		if plot == True:
			ui.plot_fit_delchi()
			pychips.log_scale(pychips.X_AXIS)
			pychips.set_current_plot("plot1")
			pychips.set_plot_title("Broken Power Law Fit for obsid {}".format(self.obsid))
			pychips.limits(pychips.X_AXIS,0.1,10)
			raw_input(">> ")
		else:
			pass

# objectoid1 = Spectral(1230)
# objectoid1.normal_fit()
# bkg, source = objectoid1.background_total()
# print(source)
def main():
	# for i in obsids:
	# 	print(i)
	# 	objectoid1 = Spectral(i)
	# 	objectoid1.create_spectra()
	# 	print(objectoid1.background_total())
	# 	print("\n\n\n")
	objectoid = Spectral(1230)
	# objectoid.create_spectra()
	objectoid.graph_spectra(groupcounts=20)
	objectoid.normal_fit()

if __name__ == "__main__":
	main()
