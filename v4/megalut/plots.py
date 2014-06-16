import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import galaxy
import os

def scatterg1(axes, galaxies):
	
	pre_g1 = np.array([g.pre_g1 for g in galaxies])
	tru_g1 = np.array([g.tru_g1 for g in galaxies])
	tru_flux = np.array([g.tru_flux for g in galaxies])

	axes.plot([-1, 1], [0, 0], "k-")
	axes.scatter(tru_g1, pre_g1 - tru_g1, s=5, lw=0, c=tru_flux)
	#axes.set_aspect('equal')
	#cbar = axes.colorbar(orientation='vertical')
	#cbar.set_label("tru_flux") 
	axes.set_xlim(-0.75, 0.75)
	axes.set_ylim(-0.15, 0.15)
	axes.set_xlabel("tru_g1")
	axes.set_ylabel("pre_g1 - tru_g1")


def scatterg2(axes, galaxies):
	
	pre_g2 = np.array([g.pre_g2 for g in galaxies])
	tru_g2 = np.array([g.tru_g2 for g in galaxies])
	tru_flux = np.array([g.tru_flux for g in galaxies])
	

	axes.plot([-1, 1], [0, 0], "k-")
	axes.scatter(tru_g2, pre_g2 - tru_g2, s=5, lw=0, c=tru_flux)
	#axes.set_aspect('equal')
	#cbar = axes.colorbar(orientation='vertical')
	#cbar.set_label("tru_flux") 
	axes.set_xlim(-0.75, 0.75)
	axes.set_ylim(-0.15, 0.15)
	axes.set_xlabel("tru_g2")
	axes.set_ylabel("pre_g2 - tru_g2")



def scatterflux(axes, galaxies):
	
	pre_flux = np.array([np.mean(g.pre_flux) for g in galaxies])
	tru_flux = np.array([g.tru_flux for g in galaxies])
	mes_flux = np.array([g.mes_flux for g in galaxies])
	
	maxflux = np.max(tru_flux) + 5.0
	minflux = np.min(tru_flux) - 5.0
	
	axes.plot([minflux, maxflux], [0, 0], "k-")
	#axes.scatter(tru_flux, mes_flux - tru_flux, s=1, lw=0, c="black")
	axes.scatter(tru_flux, pre_flux - tru_flux, s=5, lw=0, c=tru_flux)
	
	#axes.set_aspect('equal')
	axes.set_xlim(minflux, maxflux)
	axes.set_ylim(-20, 20)
	axes.set_xlabel("tru_flux")
	axes.set_ylabel("pre_flux - tru_flux")
	


def scatterrad(axes, galaxies):
	
	pre_rad = np.array([g.pre_rad for g in galaxies])
	tru_rad = np.array([g.tru_rad for g in galaxies])
	tru_flux = np.array([g.tru_flux for g in galaxies])

	maxrad = np.max(tru_rad) + 0.1
	minrad = np.min(tru_rad) - 0.1
	axes.plot([minrad, maxrad], [0, 0], "k-")
	axes.scatter(tru_rad, pre_rad - tru_rad, s=5, lw=0, c=tru_flux)
	#axes.set_aspect('equal')
	#cbar = plt.colorbar(orientation='vertical')
	#cbar.set_label("tru_flux") 
	axes.set_xlim(minrad, maxrad)
	axes.set_ylim(-0.5, 0.5)
	axes.set_xlabel("tru_rad")
	axes.set_ylabel("pre_rad - tru_rad")
	

def scattersersic(axes, galaxies):
	
	pre_sersicn = np.array([g.pre_sersicn for g in galaxies])
	tru_sersicn = np.array([g.tru_sersicn for g in galaxies])
	tru_flux = np.array([g.tru_flux for g in galaxies])
	
	maxsersicn = np.max(tru_sersicn) + 0.1
	minsersicn = np.min(tru_sersicn) - 0.1
	
	axes.plot([0, 10], [0, 0], "k-")
	axes.scatter(tru_sersicn, pre_sersicn - tru_sersicn, s=5, lw=0, c=tru_flux)
	#axes.set_aspect('equal')
	#cbar = plt.colorbar(orientation='vertical')
	#cbar.set_label("tru_flux") 
	axes.set_xlim(minsersicn, maxsersicn)
	axes.set_ylim(-1.0, 1.0)
	axes.set_xlabel("tru_sersicn")
	axes.set_ylabel("pre_sersicn - tru_sersicn")


def scattersnr(axes, galaxies):
	
	mes_fluxerr = np.array([g.mes_fluxerr for g in galaxies])
	pre_flux = np.array([g.pre_flux for g in galaxies])
	tru_flux = np.array([g.tru_flux for g in galaxies])
	tru_rad = np.array([g.tru_rad for g in galaxies])

	
#	maxsersicn = np.max(tru_sersicn) + 0.1
#	minsersicn = np.min(tru_sersicn) - 0.1
	
	#axes.plot([0, 10], [0, 0], "k-")
	axes.scatter(tru_rad, pre_flux/mes_fluxerr, s=5, lw=0,c=tru_flux)
	#axes.set_aspect('equal')
	#cbar = plt.colorbar(orientation='vertical')
	#cbar.set_label("tru_flux") 
#	axes.set_xlim(minsersicn, maxsersicn)
	#axes.set_ylim(-1.0, 1.0)
	axes.set_ylabel("pre_flux/mes_fluxerr")
	axes.set_xlabel("tru_rad")
	axes.grid()


def presummary(galaxies, filepath = None, title=""):
		
	
	fig = plt.figure(figsize=(15, 10))
	fig.subplots_adjust(left=0.07, bottom=0.08, right=0.98, top=0.92, wspace=0.25, hspace=0.2)


	fig.text(0.5, 0.95, title, ha="center", va="center")
	
	metrics = galaxy.mymetrics(galaxies)
	g1txt = "rms %8.5f, mad %8.5f" % (metrics["rms_g1"], metrics["mad_g1"])
	g2txt = "rms %8.5f, mad %8.5f" % (metrics["rms_g2"], metrics["mad_g2"])

	ax1 = fig.add_subplot(2,3,1)
	scatterg1(ax1, galaxies)
	ax1.text(0.1, 0.9, g1txt, transform = ax1.transAxes)

	ax2 = fig.add_subplot(2,3,2)
	scatterg2(ax2, galaxies)
	ax2.text(0.1, 0.9, g2txt, transform = ax2.transAxes)

	ax3bis = fig.add_subplot(2,3,3)
	scattersnr(ax3bis, galaxies)

	ax3 = fig.add_subplot(2,3,4)
	scatterflux(ax3, galaxies)
	fluxtxt = "rms %8.5f, mad %8.5f" % (metrics["rms_flux"], metrics["mad_flux"])
	ax3.text(0.1, 0.9, fluxtxt, transform = ax3.transAxes)

	
	ax4 = fig.add_subplot(2,3,5)
	scatterrad(ax4, galaxies)
	radtxt = "rms %8.5f, mad %8.5f" % (metrics["rms_rad"], metrics["mad_rad"])
	ax4.text(0.1, 0.9, radtxt, transform = ax4.transAxes)


	ax5 = fig.add_subplot(2,3,6)
	scattersersic(ax5, galaxies)
	sersicntxt = "rms %8.5f, mad %8.5f" % (metrics["rms_sersicn"], metrics["mad_sersicn"])
	ax5.text(0.1, 0.9, sersicntxt, transform = ax5.transAxes)

	if filepath:
		plt.savefig(filepath)
		print "Wrote %s" % (filepath)
	else:
		plt.show()



def ellipticity(gs):
	return np.sqrt(gs[:,1]**2+gs[:,0]**2)

	
def simmesellip(simgalaxies, filepath=None, title=None):
				
	true = np.zeros([len(simgalaxies),2])
	sex_ab = np.zeros([len(simgalaxies),2])
	acf = np.zeros([len(simgalaxies),2])
	
	np.any(np.isnan(acf))
	
	for idg, g in enumerate(simgalaxies):
		g.calcmes()
		true[idg,:] = [g.tru_g1, g.tru_g2]
		sex_ab[idg,:] = [g.mes_g1, g.mes_g2]
		acf[idg,:] = [g.mes_acf_g1, g.mes_acf_g2]
		
	fig=plt.figure(figsize=[16,8])
	if not title == None: plt.suptitle(title)
	for i in range(2):        
		plt.subplot(1,2,i+1)
		plt.plot(true[:,i], acf[:,i]-true[:,i], '+g', label='ACF');
		plt.plot(true[:,i], sex_ab[:,i]-true[:,i], '*k', label='Sex');
		plt.plot([np.amin(true[:,i]), np.amax(true[:,i])], [0,0], 'r', lw=2, label='True')
		plt.grid()
		plt.xlabel('g%d_tru' % (i+1))
		plt.ylabel('g%d_mes - g%d_tru' % (i+1,i+1))
		legend=plt.legend(loc='best')
	'''
	nbins = 10
	plt.figure()
	plt.title('Not corrected')
	n, bins, patches = plt.hist(ellipticity(true),bins=nbins,normed=1, histtype= 'step', label='true')
	plt.setp(patches, 'color', 'r', 'alpha', 0.75,linewidth=2)
	n, bins, patches = plt.hist(ellipticity(acf),bins=nbins,normed=1, histtype= 'step', label='ACF')
	plt.setp(patches, 'color', 'g', 'alpha', 0.75, linewidth=2)
	n, bins, patches = plt.hist(ellipticity(sex_ab),bins=nbins,normed=1, histtype= 'step', label='SEx')
	plt.setp(patches, 'color', 'k', 'alpha', 0.75, linewidth=2)
	plt.legend(loc='best')
	plt.xlabel('g')
	plt.grid()
	'''
	if filepath:
		plt.savefig(filepath)
		print "Wrote %s" % (filepath)
	else:
		plt.show()
		

def mesdistribs(obsgalaxies, simgalaxies, paramx, paramy, filepath=None, title=""):
	"""
	A scatter plot that compares the measured shape parameters of simulated and observed galaxies
	
	Example :
	
	paramx = ("mes_flux", "Flux", 0, 200.0)
	paramy = ("mes_fwhm", "FWHM", 0.0, 35.0)
	
	Other common params :
	("mes_eps", "eps", 0.0, 1.0),
	("mes_size", "size", 0.0, 35.0),
	("mes_sig", "sig", 0.0, 0.2),
	("mes_theta", "theta", -90.0, 90.0)
	
	"""
	for g in simgalaxies:
		g.calcmes()
	for g in obsgalaxies:
		g.calcmes()

	fig = plt.figure(figsize=(10, 10))
	fig.subplots_adjust(left=0.08, bottom=0.08, right=0.97, top=0.90, wspace=0.2, hspace=0.2)

	fig.text(0.5, 0.95, title, ha="center", va="center")

	itema = paramx
	itemb = paramy

	sima = np.array([getattr(galaxy, itema[0]) for galaxy in simgalaxies])
	simb = np.array([getattr(galaxy, itemb[0]) for galaxy in simgalaxies])

	obsa = np.array([getattr(galaxy, itema[0]) for galaxy in obsgalaxies])
	obsb = np.array([getattr(galaxy, itemb[0]) for galaxy in obsgalaxies])

	plt.scatter(obsa, obsb, color="green", lw=0, s=3, alpha=0.5, label="Observations")
	plt.scatter(sima, simb, color="red", lw=0, s=3, label="Simulations")
	
	plt.xlabel(itema[0])
	plt.xlim(itema[2], itema[3])
	plt.ylabel(itemb[0])
	plt.ylim(itemb[2], itemb[3])
	plt.legend()
	plt.grid()

	if filepath:
		plt.savefig(filepath)
		print "Wrote %s" % (filepath)
	else:
		plt.show()

def compareradgalpsf(galaxies, stars, filepath=None):
	# Compute the average of the rad psf for the stars
	rad_psf = 0.
	fwhm_psf = 0.
	for s in stars:
		fwhm_psf += s.mes_fwhm
		rad_psf += s.mes_equivrad
	rad_psf/=float(len(stars))
	fwhm_psf/=float(len(stars))

	# Load all galaxies in an array:
	gals = []
	for g in galaxies:
		gals.append(g.mes_fwhm)
	gals=np.asarray(gals)
	#gals/=rad_psf

	plt.figure()
	
	plt.hist(gals/fwhm_psf,bins=100, histtype='step',label='FHWM',normed=True)
	plt.hist(gals/rad_psf,bins=100, histtype='step',label='rad',normed=True)
	plt.plot([1.2,1.2],[0,1],lw=2)
	plt.legend(loc='best')

	plt.xlabel("mes_fwhm/mes_psf_fwhm")
	plt.ylabel("Density (normalised)")

	print float(np.size(gals[gals/fwhm_psf<1.2]))/float(np.size(gals))*100., '% under 1.2'

	if filepath:
		plt.savefig(filepath)
		print "Wrote %s" % (filepath)
	else:
		plt.show()

##############################################################################################################
def scatterplot(axes, galaxies, predlabel, trulabel, mlparamname, mltoolname, filepath=None, title=None, rangex=None, rangey=None, color=None):

	varname = "%s_committee_%s_%s" % (predlabel, mlparamname, mltoolname)
	pre=[]
	tru=[]
	for g in galaxies:

		pre.append(getattr(g, varname))
		tru.append(getattr(g, trulabel))
	pre=np.asarray(pre)
	tru=np.asarray(tru)
	for nn_i in range(np.shape(pre)[1]):
		axes.plot(tru, pre[:,nn_i] - tru, '.')
		m = np.mean(pre[:,nn_i] - tru)
		#print 'Average is %1.4f' % m

		axes.plot([np.amin(tru), np.amax(tru)], [m,m], 'r-', lw=2)

	if np.shape(pre)[1]>1:
		# Plot the final value!
		varname = predlabel
		pre=[]
		tru=[]
		for g in galaxies:
			pre.append(getattr(g, varname))
			tru.append(getattr(g, trulabel))
		pre=np.asarray(pre)
		tru=np.asarray(tru)
		axes.plot(tru, pre - tru, 'kx')
	
	if not rangex == None: axes.set_xlim(rangex)
	if not rangey == None: axes.set_ylim(rangey)
	axes.set_xlabel(trulabel)
	axes.set_ylabel("%s - %s" % (predlabel,trulabel))
	
	axes.grid()

	if filepath:
		plt.savefig(filepath)
		print "Wrote %s" % (filepath)
	'''
	else:
		plt.show()'''

def obsscatterplot(axes, galaxies, predlabel, trulabel, mlparamname, mltoolname, color=None, filepath=None, title=None, rangex=None, rangey=None):

	varname = "%s_committee_%s_%s" % (predlabel, mlparamname, mltoolname)
	pre=[]

	for g in galaxies:
		pre.append(getattr(g, varname))

	pre=np.asarray(pre)

	mpre = np.mean(pre, axis=1)
	for nn_i in range(np.shape(pre)[1]):
		axes.plot(mpre, pre[:,nn_i]-mpre, '.')
		m = np.mean(pre[:,nn_i])
		#print 'Average is %1.4f' % m
	
	if not rangex == None: axes.set_xlim(rangex)
	if not rangey == None: axes.set_ylim(rangey)
	axes.set_xlabel("mean %s" % (predlabel))
	axes.set_ylabel("%s - mean" % (predlabel))
	
	axes.grid()

	if filepath:
		plt.savefig(filepath)
		print "Wrote %s" % (filepath)
	'''
	else:
		plt.show()'''

def stddevplot(axes, galaxies, predlabel, trulabel, mlparamname, mltoolname, filepath=None, title=None, rangex=None, rangey=None, color=None):
	varname = "%s_committee_%s_%s" % (predlabel, mlparamname, mltoolname)
	pre=[]
	tru=[]
	c=[]
	for g in galaxies:
		pre.append(getattr(g, varname))
		tru.append(getattr(g, trulabel))
		if not color == None : c.append(getattr(g, color))

	if not color==None: cm=plt.cm.get_cmap('jet')
	pre=np.asarray(pre)
	tru=np.asarray(tru)

	if not color==None:
		axes.scatter(tru, np.std(pre,axis=1), marker='o', edgecolor='none', c=c, cmap = cm)
	else:
		axes.plot(tru, np.std(pre,axis=1), '.')
	axes.set_ylabel("Standard deviation on %i realisations" % (np.shape(pre)[1]))
	axes.set_xlabel(trulabel)

	axes.grid(True)

def obsstddevplot(axes, galaxies, predlabel, mlparamname, mltoolname, filepath=None, title=None, rangex=None, rangey=None, trulabel=None, color=None):
	varname = "%s_committee_%s_%s" % (predlabel, mlparamname, mltoolname)
	pre=[]
	c=[]
	for g in galaxies:
		pre.append(getattr(g, varname))
		if not color == None : c.append(getattr(g, color))

	if not color==None: cm=plt.cm.get_cmap('jet')
	pre=np.asarray(pre)

	mpre=np.mean(pre,axis=1)
	
#	exit()
	if not color==None:
		axes.scatter(mpre, np.std(pre,axis=1), marker='o', edgecolor='none', c=c, cmap = cm)
	else:
		axes.plot(mpre, np.std(pre,axis=1), '.')
	if not rangex == None: axes.set_xlim(rangex)
	axes.set_xlabel(predlabel)
	axes.set_ylabel("Standard deviation on %i realisations" % (np.shape(pre)[1]))

	axes.grid(True)


def committee_plot(plt_type, galaxies, mlparam, filepath = None, title=None):

	if 'color' in mlparam: color = mlparam['color']
	else: color=None
	fig = plt.figure(figsize=(15, 10))
	fig.subplots_adjust(left=0.07, bottom=0.08, right=0.98, top=0.92, wspace=0.25, hspace=0.2)


	if not title == None: fig.text(0.5, 0.95, title, ha="center", va="center")
	
	metrics = galaxy.mymetrics(galaxies)
	g1txt = "rms %8.5f, mad %8.5f" % (metrics["rms_g1"], metrics["mad_g1"])
	g2txt = "rms %8.5f, mad %8.5f" % (metrics["rms_g2"], metrics["mad_g2"])

	if 'g1' in mlparam:
		ax1 = fig.add_subplot(2,3,1)
		plt_type(ax1, galaxies, predlabel="pre_g1", trulabel="tru_g1", mlparamname=mlparam['g1'][1], mltoolname=mlparam['g1'][0], filepath=None, title="", rangex=mlparam['g1'][2], rangey=mlparam['g1'][3],color=color)
		ax1.text(0.1, 0.9, g1txt, transform = ax1.transAxes)

	if 'g2' in mlparam:
		ax2 = fig.add_subplot(2,3,2)
		plt_type(ax2, galaxies, predlabel="pre_g2", trulabel="tru_g2", mlparamname=mlparam['g2'][1], mltoolname=mlparam['g2'][0], filepath=None, title="", rangex=mlparam['g2'][2], rangey=mlparam['g2'][3],color=color)
		ax2.text(0.1, 0.9, g2txt, transform = ax2.transAxes)

	if 'flux' in mlparam:
		ax3 = fig.add_subplot(2,3,4)
		plt_type(ax3, galaxies, predlabel="pre_flux", trulabel="tru_flux", mlparamname=mlparam['flux'][1], mltoolname=mlparam['flux'][0], filepath=None, title="", rangex=mlparam['flux'][2], rangey=mlparam['flux'][3],color=color)
		fluxtxt = "rms %8.5f, mad %8.5f" % (metrics["rms_flux"], metrics["mad_flux"])
		ax3.text(0.1, 0.9, fluxtxt, transform = ax3.transAxes)

	if 'rad' in mlparam:
		ax4 = fig.add_subplot(2,3,5)
		plt_type(ax4, galaxies, predlabel="pre_rad", trulabel="tru_rad", mlparamname=mlparam['rad'][1], mltoolname=mlparam['rad'][0], filepath=None, title="", rangex=mlparam['rad'][2], rangey=mlparam['rad'][3],color=color)
		radtxt = "rms %8.5f, mad %8.5f" % (metrics["rms_rad"], metrics["mad_rad"])
		ax4.text(0.1, 0.9, radtxt, transform = ax4.transAxes)

	if 'sersicn' in mlparam:
		ax5 = fig.add_subplot(2,3,6)
		plt_type(ax5, galaxies, predlabel="pre_sersicn", trulabel="tru_sersicn", mlparamname=mlparam['sersicn'][1], mltoolname=mlparam['sersicn'][0], filepath=None, title="", rangex=mlparam['sersicn'][2], rangey=mlparam['sersicn'][3],color=color)
		sersicntxt = "rms %8.5f, mad %8.5f" % (metrics["rms_sersicn"], metrics["mad_sersicn"])
		ax5.text(0.1, 0.9, sersicntxt, transform = ax5.transAxes)
	
	if filepath:
		plt.savefig(filepath)
		print "Wrote %s" % (filepath)
	else:
		plt.show()




def prerrbin_plot(simgalaxies, obsgalaxies=None, filepath = None, title=None, snrmax = 50.0, sizeratiomax=3.0):
	"""
	
	careful : I assume that your obsgalaxies have the same PSF as simgalaxies !
	
	"""
	
	for g in simgalaxies:
		g.calcmes()		
		
	try:
		prerrabs_g = np.array([g.prerrabs_g for g in simgalaxies])
		prerrabs_rad = np.array([g.prerrabs_rad for g in simgalaxies])
		prerrabs_sersicn = np.array([g.prerrabs_sersicn for g in simgalaxies])
	
		mes_snr = np.array([g.mes_snr for g in simgalaxies])
		pre_rad = np.array([g.pre_rad for g in simgalaxies])
		mes_gs_sigma = np.array([g.mes_gs_sigma for g in simgalaxies])
	
		mes_gs_ratio = np.array([g.mes_gs_sigma / g.mes_gs_psf_sigma for g in simgalaxies])
	
		mes_gs_psf_sigma = np.array([g.mes_gs_psf_sigma for g in simgalaxies])
		mes_gs_psf_rho4 = np.array([g.mes_gs_psf_rho4 for g in simgalaxies])
	except:
		print "Some required fields not available for prerrbin_plot... skipping."
		return
	
	
	assert np.std(mes_gs_psf_sigma) == 0.0
	obs_psf_sigma = mes_gs_psf_sigma[0] # YES, we assume it's the same PSF !
	
	if obsgalaxies is not None:
		mes_snr_obs = np.array([g.mes_snr for g in obsgalaxies])
		mes_gs_ratio_obs = np.array([g.mes_gs_sigma / obs_psf_sigma for g in obsgalaxies])
		
		flagobsgalaxies = [g for g in obsgalaxies if getattr(g, "flag", 0) > 0]
		mes_snr_obs_flag = np.array([g.mes_snr for g in flagobsgalaxies])
		mes_gs_ratio_obs_flag = np.array([g.mes_gs_sigma / obs_psf_sigma for g in flagobsgalaxies])
		
	
	
	fig = plt.figure(figsize=(18, 10))
	fig.subplots_adjust(left=0.06, bottom=0.06, right=0.98, top=0.90, wspace=0.2, hspace=0.2)

	minorLocator = matplotlib.ticker.MultipleLocator(5)

	extent = (0.0, snrmax, 0.5, sizeratiomax) # xmin xmax    ymin ymax
	extentzoom = (5.0, snrmax/3.0, 0.5, ((sizeratiomax-1.0)/2.0)+1.0) # xmin xmax    ymin ymax
	
	gridsize = 30
	redf = np.mean	

	# g
	ax = fig.add_subplot(2,3,1)
	stuff = ax.hexbin(mes_snr, mes_gs_ratio, C=prerrabs_g, reduce_C_function = redf, gridsize=gridsize, cmap=plt.cm.jet, extent = extent, vmin=0.0, vmax=0.3)
	if obsgalaxies is not None:
		ax.plot(mes_snr_obs, mes_gs_ratio_obs, ls="None", marker=",", color="gray")
		ax.plot(mes_snr_obs_flag, mes_gs_ratio_obs_flag, ls="None", marker=".", markersize=2, color="black")
		
		ax.set_xlim(extent[0], extent[1])
		ax.set_ylim(extent[2], extent[3])

	ax.set_xlabel("SNR")
	ax.set_ylabel("Size ratio")
	cb = plt.colorbar(stuff, ax = ax)
	cb.set_label("prerrabs_g")
	ax.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(2))
	ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(0.1))




	# gzoom
	ax = fig.add_subplot(2,3,2)
	stuff = ax.hexbin(mes_snr, mes_gs_ratio, C=prerrabs_g, reduce_C_function = redf, gridsize=gridsize, cmap=plt.cm.jet, extent = extentzoom, vmin=0.0, vmax=0.3)
	if obsgalaxies is not None:
		ax.plot(mes_snr_obs, mes_gs_ratio_obs, ls="None", marker=",", color="gray")
		ax.plot(mes_snr_obs_flag, mes_gs_ratio_obs_flag, ls="None", marker=".", markersize=2, color="black")
		
		ax.set_xlim(extentzoom[0], extentzoom[1])
		ax.set_ylim(extentzoom[2], extentzoom[3])

	ax.set_xlabel("SNR")
	ax.set_ylabel("Size ratio")
	cb = plt.colorbar(stuff, ax = ax)
	cb.set_label("prerrabs_g")
	ax.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(2))
	ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(0.1))



	# counts
	ax = fig.add_subplot(2,3,3)
	stuff = ax.hexbin(mes_snr, mes_gs_ratio, bins="log", C=None, gridsize=gridsize, cmap=plt.cm.Blues, extent = extent)
	ax.set_xlabel("SNR")
	ax.set_ylabel("Size ratio")
	cb = plt.colorbar(stuff, ax = ax)
	cb.set_label("log10(learning counts)")
	ax.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(2))
	ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(0.1))
	ax.grid()
	
	"""
	if obsgalaxies is not None:
		
		
		ax = fig.add_subplot(2,3,3)
		stuff = ax.hexbin(mes_snr_obs, mes_gs_ratio_obs, bins="log", C=None, gridsize=gridsize, cmap=plt.cm.Blues, extent = extent)
		ax.set_xlabel("SNR")
		ax.set_ylabel("Size ratio")
		cb = plt.colorbar(stuff, ax = ax)
		cb.set_label("log10(observed counts)")
		ax.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(2))
		ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(0.1))
		ax.grid()
	"""
		
		
	# rad
	ax = fig.add_subplot(2,3,4)
	stuff = ax.hexbin(mes_snr, mes_gs_ratio, C=prerrabs_rad, reduce_C_function = redf, gridsize=gridsize, cmap=plt.cm.jet, extent = extent, vmin=0.0, vmax=2.0)
	ax.set_xlabel("SNR")
	ax.set_ylabel("Size ratio")
	cb = plt.colorbar(stuff, ax = ax)
	cb.set_label("prerrabs_rad")
	ax.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(2))
	ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(0.1))
	
	
	# sersicn
	ax = fig.add_subplot(2,3,5)
	stuff = ax.hexbin(mes_snr, mes_gs_ratio, C=prerrabs_sersicn, reduce_C_function = redf, gridsize=gridsize, cmap=plt.cm.jet, extent = extent, vmin=0.0, vmax=1.0)
	ax.set_xlabel("SNR")
	ax.set_ylabel("Size ratio")
	cb = plt.colorbar(stuff, ax = ax)
	cb.set_label("prerrabs_sersicn")
	ax.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(2))
	ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(0.1))
	
	
	# PSF
	ax = fig.add_subplot(2,3,6)
	stuff = ax.plot(mes_gs_psf_sigma, mes_gs_psf_rho4, "bo", lw=0)
	ax.set_xlim(-0.5, 4.0)
	ax.set_xlabel("PSF gs_sigma")
	ax.set_ylim(-0.5, 4.0)
	ax.set_ylabel("PSF gs_rho4")
	ax.grid()
	ax.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(2))
	ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(0.1))
	
	
	
	

	if not title == None: fig.text(0.5, 0.95, title, ha="center", va="center")
	
	if filepath:
		plt.savefig(filepath)
		print "Wrote %s" % (filepath)
	else:
		plt.show()


