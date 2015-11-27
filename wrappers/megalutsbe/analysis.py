"""
Analysis of the SBE results.
Parts of this are copy-pasted from the xample analysis scripts by Bryan.

That's why all this is so ugly, but let's keep it this way so that fixing parts of it
can be easier.

"""
import multiprocessing as mtp
import numpy as np

import scipy.stats
import scipy.optimize

from .. import tools

import logging
logger = logging.getLogger(__name__)


def analyse(cat,
	colname_PSF_ellipticity_angles_degrees="PSF_shape_angle_degrees",
	colname_e1_guesses="e1_guess",
	colname_e2_guesses="e2_guess",
	colname_gal_g1s="gal_g1",
	colname_gal_g2s="gal_g2",
	outputpath = None
	):
	"""
	Ugly coding as I try to reuse as much of the SBE code as possible...
	"""
	
	# As a quick comparision, our own way of measureing m and c:
	e1m = tools.metrics.metrics(cat, labelfeature=tools.feature.Feature(colname_gal_g1s), predlabelfeature=tools.feature.Feature(colname_e1_guesses, rea="Full"))
	e2m = tools.metrics.metrics(cat, labelfeature=tools.feature.Feature(colname_gal_g2s), predlabelfeature=tools.feature.Feature(colname_e2_guesses, rea="Full"))
	
	print "MegaLUT metrics in pixel frame:"
	print "e1: m/100 = %.4f +/- %.4f, c/100 = %.4f +/- %.4f, predfrac = %.2f %%" % (e1m["m"]*100.0, e1m["merr"]*100.0, e1m["c"]*100.0, e1m["cerr"]*100.0, e1m["predfrac"]*100.0)
	print "e2: m/100 = %.4f +/- %.4f, c/100 = %.4f +/- %.4f, predfrac = %.2f %%" % (e2m["m"]*100.0, e2m["merr"]*100.0, e2m["c"]*100.0, e2m["cerr"]*100.0, e2m["predfrac"]*100.0)
	
	
	# And now the SBE way:
	PSF_ellipticity_angles_radians = cat[colname_PSF_ellipticity_angles_degrees]*np.pi/180
	e1_guesses = cat[colname_e1_guesses]
	e2_guesses = cat[colname_e2_guesses]
	gal_g1s = cat[colname_gal_g1s]
	gal_g2s = cat[colname_gal_g2s]
	weights = np.logical_not(cat[colname_e1_guesses].mask).astype("float")
	
		
	e1_pix_regression, e2_pix_regression, e1_PSF_regression, e2_PSF_regression, \
		e1_max_regression, e2_max_regression, max_f = \
		regress_results(PSF_ellipticity_angles_radians, e1_guesses, e2_guesses,
		gal_g1s, gal_g2s, weights, outputpath)
	
	
	failure_rate = float(len(weights[weights == 0]))/len(weights)
	N_eff = np.square(np.sum(weights))/np.sum(np.square(weights))
	N_eff_over_N = N_eff/len(weights)
	
	# Writing or displaying output file
	
	output_regression_results(outputpath,
		e1_pix_regression, e2_pix_regression,
		e1_PSF_regression, e2_PSF_regression,
		e1_max_regression, e2_max_regression,
		max_f, failure_rate, N_eff_over_N)
	

	



def get_most_effective_PSF_rotation_factor(PSF_ellipticity_angles_radians, e1_guesses, e2_guesses,
										   gal_g1s, gal_g2s, weights):
	
	get_neg_abs_e1 = lambda f : -np.abs( get_rot_regression(e1_guesses,e2_guesses,gal_g1s,gal_g2s,weights,
												   f*PSF_ellipticity_angles_radians)[4][0]-1. )
	
	fminres = scipy.optimize.fmin(get_neg_abs_e1,x0=-1.,disp=False)[0]
	#logger.info("fmin output: \n%s" % str(fminres))
	
	return fminres
	
	

def get_regression(e1_guesses, e2_guesses, gal_g1s, gal_g2s, weights):
	
	# To calculate m and c, we'll do a linear regression
	good = weights > 0
	e1_pix_regression = scipy.stats.linregress(gal_g1s[good], e1_guesses[good])
	e2_pix_regression = scipy.stats.linregress(gal_g2s[good], e2_guesses[good])
	
	#logger.info("linregress output e1: %s" % str(e1_pix_regression))
	#logger.info("linregress output e2: %s" % str(e2_pix_regression))
	
	return e1_pix_regression, e2_pix_regression

def get_rot_regression(e1_guesses, e2_guesses, gal_g1s, gal_g2s, weights, thetas):
	
	cos_thetas = np.cos(thetas)
	sin_thetas = np.sin(thetas)
	rot_e1_guesses = e1_guesses * cos_thetas - e2_guesses * sin_thetas
	rot_e2_guesses = e1_guesses * sin_thetas + e2_guesses * cos_thetas
	rot_gal_g1s = gal_g1s * cos_thetas - gal_g2s * sin_thetas
	rot_gal_g2s = gal_g1s * sin_thetas + gal_g2s * cos_thetas
	
	# To calculate m and c, we'll do a linear regression
	good = weights > 0
	e1_PSF_regression = scipy.stats.linregress(rot_gal_g1s[good], rot_e1_guesses[good])
	e2_PSF_regression = scipy.stats.linregress(rot_gal_g2s[good], rot_e2_guesses[good])
	
	return rot_gal_g1s, rot_gal_g2s, rot_e1_guesses, rot_e2_guesses, \
		e1_PSF_regression, e2_PSF_regression

def regress_results(PSF_ellipticity_angles_radians, e1_guesses, e2_guesses, gal_g1s, gal_g2s, weights, store_path=None):
	""" Performs a linear regression in the pixel and PSF coordinate frames to our result data.
	
		Requires: PSF_ellipticity_angles_radians <array of floats>
				  e1_guesses <array of floats>
				  e2_guesses <array of floats>
				  gal_g1s <array of floats>
				  gal_g2s <array of floats>
				  weights <array of floats>
				  
		Returns: e1_pix_regression <tuple of floats> (see documentation of scipy.stats.linregress)
				 e2_pix_regression <tuple of floats>
				 e1_PSF_regression <tuple of floats>
				 e2_PSF_regression <tuple of floats>
				 e1_max_regression <tuple of floats>
				 e2_max_regression <tuple of floats>
				 max_f <float> (Factor of PSF angle to rotate by to maximize abs(m_e1)) 
	"""
	
	logger.info("Performing pixel frame regression...")
	
	e1_pix_regression, e2_pix_regression = get_regression(e1_guesses, e2_guesses, gal_g1s, gal_g2s, weights)
	
	
	logger.info("Performing PSF frame regression...")
	
	# Now, let's do a rotation to the PSF frame
	thetas = -PSF_ellipticity_angles_radians
	
	rot_gal_g1s, rot_gal_g2s, rot_e1_guesses, rot_e2_guesses, \
		e1_PSF_regression, e2_PSF_regression = get_rot_regression(e1_guesses, e2_guesses, 
															  gal_g1s, gal_g2s, weights, thetas)
	
	logger.info("Determining what factor of the PSF angle would give the maximal abs(m) for e1...")
		
	# Determine what factor of the PSF angle would give the maximal abs(m) for e1
	max_f = get_most_effective_PSF_rotation_factor(PSF_ellipticity_angles_radians, e1_guesses,
												   e2_guesses, gal_g1s, gal_g2s, weights)
	
	logger.info("Getting the regression in this rotated frame...")
	
	# And get the regression in this rotated frame
	thetas = max_f*PSF_ellipticity_angles_radians
	
	max_rot_gal_g1s, max_rot_gal_g2s, max_rot_e1_guesses, max_rot_e2_guesses, \
		e1_max_regression, e2_max_regression = get_rot_regression(e1_guesses, e2_guesses, 
															  gal_g1s, gal_g2s, weights, thetas)
	
	
	return e1_pix_regression, e2_pix_regression, e1_PSF_regression, e2_PSF_regression, \
		e1_max_regression, e2_max_regression, max_f
	"""
	# Store the data if desired
	if(store_path is not None):
		
		stored_data_table = fits.new_table(
			fits.ColDefs([fits.Column(name=mv.result_gal_g1_colname, format='E', array=gal_g1s),
						  fits.Column(name=mv.result_gal_g2_colname, format='E', array=gal_g2s),
						  fits.Column(name=mv.result_e1_guess_colname, format='E', array=e1_guesses),
						  fits.Column(name=mv.result_e2_guess_colname, format='E', array=e2_guesses),
						  fits.Column(name=mv.result_rot_prefix+mv.result_gal_g1_colname, format='E',
									  array=rot_gal_g1s),
						  fits.Column(name=mv.result_rot_prefix+mv.result_gal_g2_colname, format='E',
									  array=rot_gal_g2s),
						  fits.Column(name=mv.result_rot_prefix+mv.result_e1_guess_colname, format='E',
									  array=rot_e1_guesses),
						  fits.Column(name=mv.result_rot_prefix+mv.result_e2_guess_colname, format='E',
									  array=rot_e2_guesses),
						  fits.Column(name=mv.result_max_rot_prefix+mv.result_gal_g1_colname, format='E',
									  array=max_rot_gal_g1s),
						  fits.Column(name=mv.result_max_rot_prefix+mv.result_gal_g2_colname, format='E',
									  array=max_rot_gal_g2s),
						  fits.Column(name=mv.result_max_rot_prefix+mv.result_e1_guess_colname, format='E',
									  array=max_rot_e1_guesses),
						  fits.Column(name=mv.result_max_rot_prefix+mv.result_e2_guess_colname, format='E',
									  array=max_rot_e2_guesses),
						  fits.Column(name=mv.result_weight_colname, format='E',
									  array=weights)]))
		comparison_type_array = ["e1_pix","e2_pix","e1_PSF","e2_PSF","e1_max","e2_max"]
		m_array = np.array([e1_pix_regression[0],e2_pix_regression[0],
							e1_PSF_regression[0],e2_PSF_regression[0],
							e1_max_regression[0],e2_max_regression[0]]) - 1.
		c_array = np.array([e1_pix_regression[1],e2_pix_regression[1],
							e1_PSF_regression[1],e2_PSF_regression[1],
							e1_max_regression[1],e2_max_regression[1]])
		r2_array = np.array([e1_pix_regression[2],e2_pix_regression[2],
							 e1_PSF_regression[2],e2_PSF_regression[2],
							 e1_max_regression[2],e2_max_regression[2]]) ** 2
							
		
		stored_data_hdu_list = fits.HDUList([fits.PrimaryHDU(), stored_data_table])
		
		regression_results_table = fits.new_table(
			fits.ColDefs([fits.Column(name=mv.result_comparison_type_colname, format='6A', array=comparison_type_array),
						  fits.Column(name=mv.result_m_colname, format='E', array=m_array),
						  fits.Column(name=mv.result_c_colname, format='E', array=c_array),
						  fits.Column(name=mv.result_r_squared_colname, format='E', array=r2_array)]))
		
		stored_data_hdu_list.append(regression_results_table)
		
		joined_stored_data_filename = os.path.join(store_path,mv.stored_data_filename)
		
		stored_data_hdu_list.writeto(joined_stored_data_filename, clobber=True, )
		
	"""

def output_regression_results(path, e1_pix_regression, e2_pix_regression, e1_PSF_regression,
							  e2_PSF_regression, e1_max_regression,
							  e2_max_regression, max_f, failure_rate=None, N_eff_over_N=None):
	""" Outputs the results of the linear regression into the results file.
	
		Requires: path <string> (location where the results file should be made)
				  e1_pix_regression <tuple of floats> (see documentation of scipy.stats.linregress)
				  e2_pix_regression <tuple of floats>
				  e1_PSF_regression <tuple of floats>
				  e2_PSF_regression <tuple of floats>
				  e1_max_regression <tuple of floats>
				  e2_max_regression <tuple of floats>
				  max_f <float> (Factor of PSF angle to rotate by to maximize abs(m_e1)) 
				  failure_rate <float>
				  
		Returns: joined_output_filename <string> (full name, including path, of output file created)
		
		Side-effects: Output file is created and written to.
	"""
	
	# Set up labels we'll be printing in the output text file
	labels = ["e1 in pixel frame:", "e2 in pixel frame:", "e1 in PSF frame:", "e2 in PSF frame:",
			  "e1 in "+str(max_f)+"*PSF frame:", "e2 in "+str(max_f)+"*PSF frame:"]
	
	txts = []
	
	if(failure_rate is not None):
		txts.append("\nShape estimation failure rate: " + str(100*failure_rate) + " %\n")
	if(N_eff_over_N is not None):
		txts.append("N_eff/N: " + str(N_eff_over_N) + "\n")
		
	for regression_results in enumerate([e1_pix_regression, e2_pix_regression,
										 e1_PSF_regression, e2_PSF_regression,
										 e1_max_regression, e2_max_regression]):
		txts.append(labels[regression_results[0]] + "\n")
		txts.append("m   = " + str(regression_results[1][0] - 1.))
		txts.append("c   = " + str(regression_results[1][1]))
		txts.append("r^2 = " + str(regression_results[1][2] ** 2) + "\n")
	
	txt = "\n".join(txts)
	
	print txt
