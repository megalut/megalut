import os
import numpy as np
from scipy import stats

import config
import pylab as plt

import megalut.tools as tools

import megalutgreat3 as mg3
import metrics.evaluate as evaluate

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

draw_subfields = False
show = True

# Loading the correct configuration!
great3 = mg3.great3.load_config(outdir='cgc')

fakedir = 'fake_%s' % great3.get_branchacronym()

if not os.path.exists(fakedir):
	os.makedirs(fakedir)
	os.makedirs(os.path.join(fakedir, "out"))
great3.workdir = fakedir
	
# The training used by default in training is the one defined in:
# great3.trainparams_name
trainname = great3.trainparams_name
trainparamslist = great3.trainparamslist

mean_g1 = []
mean_g2 = []

if not os.path.exists(fakedir):
	os.makedirs(fakedir)
	
fields_id, fields_true_e1, fields_true_e2 = evaluate.get_generate_const_truth(great3.experiment, great3.obstype, logger=logger)
	
config.subfields = range(200)

def make_errors(trushapecat):
	SN = np.clip(trushapecat["gal_sn"] / 100., 0., 1.)
	sersicn = trushapecat["bulge_n"] / 4.
	twocomp = np.clip(trushapecat["bulge_flux"] / 100., 0., 1.)
	g1 = np.clip((trushapecat['g1_intrinsic']+trushapecat['g1']) / 0.7, -1, 1.)
	g2 = np.clip((trushapecat['g2_intrinsic']+trushapecat['g2']) / 0.7, -1, 1.)
	gal_size =  np.clip(((trushapecat["disk_hlr"] + trushapecat["bulge_hlr"]) / 2.)/1., 0., 1.)
	nrandn = np.shape(gal_size)[0]
	
	def base_err():
		return np.sign(g1) * np.sign(g2) * np.sqrt(SN) * 9e-3 + sersicn**2 * 1e-3 + twocomp * 2e-3 +\
			 (1. - np.abs(g1)) * (1.-np.abs(g2)) * gal_size * 5e-3 +\
			 ((1. - np.abs(g1)) + (1.-np.abs(g2))) * 5e-3 + np.random.randn(nrandn) * 5e-4 
			
	err1 = (g1 * 1e-3 + base_err()) / 3.
	err2 = (g2 * 1e-3 + base_err()) / 3.
	
	return err1, err2

for subfield in config.subfields:
	print 'Subfield {:03d}'.format(subfield)
	# We load the predictions
	cat = tools.io.readpickle(great3.get_path("obs", "img_%i_meascat.pkl" % subfield))
	trushapecat = mg3.great3.load_true_shape(config.trushapedir, great3.experiment, great3.obstype, great3.sheartype, subfield)

	err1, err2 = make_errors(trushapecat)
	"""
	plt.figure()
	plt.hist(err1, 50, alpha=.5)
	plt.hist(err2, 50, alpha=.5)
	plt.show()
	"""
	# We cut out the columns we need
	preobscat = trushapecat["ID","g1_intrinsic","g2_intrinsic"]
	
	preobscat['g1_intrinsic'] = trushapecat['g1_intrinsic'] + trushapecat['g1'] + err1#(np.random.randn() * 1e-13 + 1) * (preobscat['g1_intrinsic'] + trushapecat['g1']) + np.random.randn() * 1e-12
	preobscat['g2_intrinsic'] = trushapecat['g2_intrinsic'] + trushapecat['g2'] + err2#(np.random.randn() * 1e-6 + 1) * (preobscat['g2_intrinsic'] + trushapecat['g2']) + np.random.randn() * 1e-6
	
	mg1s = np.ma.mean(preobscat['g1_intrinsic'])
	mg2s = np.ma.mean(preobscat['g2_intrinsic'])
	
	# We write the ascii file
	preobscat.write(os.path.join(fakedir, "out", "%03i.cat" % subfield), format="ascii.commented_header")
	
	if draw_subfields:
		
		print '...| meas val | true val |'
		print 'e1 |{:+0.7f}|{:+0.7f}|'.format(mg1s, fields_true_e1[subfield])
		print 'e2 |{:+0.7f}|{:+0.7f}|'.format(mg2s, fields_true_e2[subfield])
	
		fig = plt.figure(figsize=(8,4.5))
	
		ax1 = plt.subplot(121, aspect='equal')
		
		x = trushapecat['g1_intrinsic'] + trushapecat['g1']
		y = preobscat['g1_intrinsic']
		
		ax1.scatter(x, y-x, marker='.', c='Grey', edgecolor="None")
		ax1.axhline(0, ls='--', c='k', lw=2)
		ax1.axvline(fields_true_e1[subfield] * 10, c='k', lw=2, ls='--')
		ax1.axvline(mg1s * 10, c='k', lw=2)
		ax1.set_xlim([-0.7, 0.7])
		ax1.set_ylim([-0.7, 0.7])
		ax1.set_xlabel("g1 predicted")
		ax1.set_ylabel("g pred - (g intrinsic + g true)")
		
		m, c, _, _, _ = stats.linregress(x, y-x)
		ax1.annotate(r"$m_1=%0.1f\cdot 10^{-3}$" % (m * 1e3), xy=(0.2, -0.58))
		ax1.annotate(r"$c_1=%0.1f\cdot 10^{-4}$" % (c * 1e4), xy=(0.2, -0.65))
		ax1.grid()
		
		ax2 = plt.subplot(122, aspect='equal')
	
		x = trushapecat['g2_intrinsic'] + trushapecat['g2']
		y = preobscat['g2_intrinsic']
		
		ax2.scatter(x, y-x, marker='.', c='Grey', edgecolor="None")
		ax2.axhline(0, ls='--', c='k', lw=2)
		ax2.axvline(fields_true_e2[subfield] * 10, c='k', lw=2, ls='--')
		ax2.axvline(mg2s * 10, c='k', lw=2)
		ax2.set_xlim([-0.7, 0.7])
		ax2.set_ylim([-0.7, 0.7])
		
		m, c, _, _, _ = stats.linregress(x, y-x)
		ax2.annotate(r"$m_2=%0.1f\cdot 10^{-3}$" % (m * 1e3), xy=(0.2, -0.58))
		ax2.annotate(r"$c_2=%0.1f\cdot 10^{-4}$" % (c * 1e4), xy=(0.2, -0.65))
		ax2.grid()
		ax2.set_yticklabels([])
		ax2.set_xlabel("g1 predicted")
		
		plt.suptitle("Subfield {:03d}".format(subfield))
		
		plt.tight_layout()
		plt.subplots_adjust(wspace=0.)
		
		fname = os.path.join(fakedir, 'shearpred_subfield_{:03d}.png'.format(subfield))
		fig.savefig(fname,dpi=300)
		if show:
			plt.show()
		
		plt.close(fig)

logger.info("Pre-submitting the catalogs")

great3.presubmit(corr2path=config.corr2path, presubdir=config.presubdir)

logger.info("Evaluating with the Great3 code")

submission_file = os.path.join(fakedir, "out", "%s.out" % great3.branchcode())

fname = os.path.join(fakedir, 'shearpred_all_subfields.png')
results = evaluate.q_constant(submission_file, great3.experiment, great3.obstype, logger=logger, plot=fname, pretty_print=True)
Q_c, cp, mp, cx, mx, sigcp, sigcmp, sigcx, sigmx = results

np.savetxt(great3.get_path('out', 'results_%s.out' % great3.branchcode()), results,\
		 header='Q_c, cp, mp, cx, mx, sigcp, sigcmp, sigcx, sigmx')
logging.info('Q value: %1.2f' % Q_c) 
