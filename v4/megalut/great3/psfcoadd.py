import megalut
import numpy as np
import sys
import galsim

def psfcoadd(simparams,
	s, n, nimg,
	obspsfimgfilepath,
	simgalimgfilepath,
	simgalfilepath,
	is_psfvar,
	current_subfield,
	stars=None,
	random_psf=False,
	simtrugalimgfilepath = None,
	simpsfimgfilepath = None):

	psf_field_xy_pos = []
	psf_field_tru_pos = []

	psf_tile_xy_pos = []
	psf_tile_tru_pos = []

		
	get_fname = stars[0]
	shear_type = stars[1]
	min_snr=simparams.get_star_min_snr()

#		else:
	import time
	message = 'Preparing the PSFs. This could take a while...\nSubfields: '
	sys.stdout.write(message)
	sys.stdout.flush()
	if shear_type == "constant": nsub = 1
	else: nsub = 1
	for subfield in range(current_subfield,current_subfield+nsub):
		sys.stdout.write('%03i, ' % subfield)
		sys.stdout.flush()
		im = galsim.fits.read(obspsfimgfilepath(subfield))

		substars = megalut.utils.readpickle(get_fname(subfield))
		for iik, st in enumerate(substars):
			if st.isbrighter(min_snr): 
				psf_field_xy_pos.append([subfield,st.x,st.y])
				psf_field_tru_pos.append(st.get_xy_field_deg())

				psf_tile_xy_pos.append(st.get_xy_tile())
				psf_tile_tru_pos.append(st.get_xy_tile_deg())


		del substars, im

	im = []
	subfield=None
	message = 'Done.\n'
	sys.stdout.write(message)
	sys.stdout.flush()

	psf_field_xy_pos=np.asarray(psf_field_xy_pos)
	psf_field_tru_pos=np.asarray(psf_field_tru_pos)
	psf_tile_xy_pos=np.asarray(psf_tile_xy_pos)
	psf_tile_tru_pos=np.asarray(psf_tile_tru_pos)
#		psf_usage=np.zeros(len(psf_field_xy_pos))

	if len(psf_field_tru_pos)==0: raise ValueError("Sorry, no stars with SNR >= %i found... Try again with a lower value!" % min_snr)

	print "%i stars with a SNR >= %i were selected for the simulation" % (len(psf_field_tru_pos), min_snr)
	
	random_psf=True
