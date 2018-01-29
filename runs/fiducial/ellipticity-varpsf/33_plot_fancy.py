import includes
import measfcts
import os
import numpy as np
import matplotlib.ticker as ticker

import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)

trainname = "train_g1_ada3"

if trainname == "train_ada3" or trainname == "train_g1_ada3":
	prefix = "fid-ell-varPSF-no-"
	maxy = -0.05
	miny = 0.05
elif trainname == "train_ada5" or trainname == "train_g1_ada5":
	prefix = "fid-ell-varPSF-xy-"
	maxy = -0.005
	miny = 0.005

traindir = os.path.join(includes.workdir, trainname)
outdir = os.path.join(traindir, "plots")

megalut.plot.figures.set_fancy(14)

component = "1"
component2 = "2"
main_pred = "s{}".format(component)
maincol = "tru_{}".format(main_pred)
main_feat = Feature(maincol)

nbins = 10
ncbins = 10

outdirplots = os.path.join(traindir, "plots")
if not os.path.exists(outdirplots):
	os.mkdir(outdirplots)
valprecatpath = os.path.join(traindir, "valprecat.pkl")


cat = megalut.tools.io.readpickle(valprecatpath)

cat["tru_psf_fwhm"] = cat["tru_psf_sigma"] * 2.355
#psf_field = megalut.tools.io.readpickle(os.path.join(includes.simdir, "EllipticityVarPSF", "psf", "psf_field.pkl"))
#x, y = cat["tru_gal_x_chip"], cat["tru_gal_y_chip"]
#tru_psf_g1, tru_psf_g2, tru_psf_fwhm = psf_field.eval(x, y)
#cat["tru_psf_fwhm"] = tru_psf_fwhm / 0.1


# Since I fixed, by mistake, the gain to 50 and we're playing with gain = 1, let's recompute snr:
cat = megalut.meas.snr_2hlr.measfct(cat, gain=1e9, fluxcol='adamom_flux')


print megalut.tools.table.info(cat)

print np.amin(cat["tru_psf_g1"]), np.amax(cat["tru_psf_g1"])
print np.amin(cat["tru_psf_g2"]), np.amax(cat["tru_psf_g2"])

g = np.hypot(cat["tru_psf_g2"], cat["tru_psf_g2"])
print np.amin(g), np.amax(g)
print '-----------------'
print np.amin(cat["tru_psf_fwhm"]), np.amax(cat["tru_psf_fwhm"])

param_feats = [
		#Feature("snr_mean", nicename=r"$S/N$"),
		#Feature("tru_flux", nicename=r"$F\,\mathrm{[counts]}$"),
		#Feature("tru_rad", nicename=r"$R\,\mathrm{[px]}$"),
		#Feature("tru_sersicn", nicename=r"$n$"),
		#Feature("tru_g", nicename=r"$e$"),
		Feature("tru_psf_g1", nicename=r"PSF $e_1$", low=-0.03, high=0.1),
		Feature("tru_psf_g2", nicename=r"PSF $e_2$", low=-0.07, high=0.1),
		Feature("tru_psf_fwhm", nicename=r"PSF FWHM [px]", low=cat["tru_psf_fwhm"].min()*0.95, high=cat["tru_psf_fwhm"].max()*1.05),
		]




for comp in [component,component2]:
	cat["pre_g{}".format(comp)] = cat["pre_g{}_adamom".format(comp)]
	megalut.tools.table.addstats(cat, "pre_g{}".format(comp))
	megalut.tools.table.addrmsd(cat, "pre_g{}".format(comp), "tru_s{}".format(comp))
megalut.tools.table.addstats(cat, "snr")


cat["adamom_frac"] = np.sum(cat["adamom_g1"].mask, axis=1)/float(cat["adamom_g1"].shape[1])

s = megalut.tools.table.Selector("ok", [
	("in", "snr_mean", 0.85, 150),
	#("in", "tru_rad", 0, 11),
	("max", "adamom_frac", 0.01)
	]
	)

cat = s.select(cat)

#--------------------------------------------------------------------------------------------------
fig = plt.figure(figsize=(8.5, 3))
plt.subplots_adjust(wspace=0.0)
plt.subplots_adjust(bottom=0.2)
plt.subplots_adjust(right=0.92)
plt.subplots_adjust(left=0.11)

#------------------------------------------------------------

maxsnr = cat["snr_mean".format(component)].max()
minsnr = cat["snr_mean".format(component)].min()

minshear = -0.12
maxshear = 0.12
#------------------------------------------------------------

ax = fig.add_subplot(1, 2, 1)
ax.fill_between([-1, 1], -2e-3, 2e-3, alpha=0.2, facecolor='darkgrey')
ax.axhline(0, ls='--', color='k')
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("pre_g{}_bias".format(component)), \
	featc=Feature("snr_mean"), marker='.', cmap="plasma", hidecbar=True, vmin=minsnr, vmax=maxsnr)
ax.set_ylabel(r"Shear\ bias")
ax.set_xlabel(r"True shear $g_{%s}$" % component)

metrics = megalut.tools.metrics.metrics(cat, main_feat,  Feature("pre_g{}_bias".format(component)), pre_is_res=True)

ax.annotate(r"$\mathrm{RMSD=%.5f}$" % metrics["rmsd"], xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -4), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3\mu=%.1f \pm %.1f;\,10^3c=%.1f \pm %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0, \
	metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -19), textcoords='offset points', ha='left', va='top')
#ax.annotate(r"$10^3c=%.1f \pm %.1f$" % (metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -35), textcoords='offset points', ha='left', va='top')
ax.set_ylim([miny, maxy])
ax.set_xlim([minshear, maxshear])

#------------------------------------------------------------

ax = fig.add_subplot(1, 2, 2)
ax.fill_between([-1, 1], -2e-3, 2e-3, alpha=0.2, facecolor='darkgrey')
ax.axhline(0, ls='--', color='k')
megalut.plot.scatter.scatter(ax, cat, main_feat,  Feature("pre_g{}_bias".format(component2)), 
	featc=Feature("snr_mean", nicename=r"S/N"), marker='.', cmap="plasma", vmin=minsnr, vmax=maxsnr)
ax.set_xlabel(r"True shear $g_{%s}$" % component2)
metrics = megalut.tools.metrics.metrics(cat, main_feat,  Feature("pre_g{}_bias".format(component2)), pre_is_res=True)

ax.annotate(r"$\mathrm{RMSD=%.5f}$" % metrics["rmsd"], xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -4), textcoords='offset points', ha='left', va='top')
ax.annotate(r"$10^3\mu=%.1f \pm %.1f;\,10^3c=%.1f \pm %.1f$" % (metrics["m"]*1000.0, metrics["merr"]*1000.0, \
	metrics["c"]*1000.0, metrics["cerr"]*1000.0), xy=(0.0, 1.0), xycoords='axes fraction', xytext=(8, -19), textcoords='offset points', ha='left', va='top')
ax.set_ylim([miny, maxy])
ax.set_xlim([minshear, maxshear])
ax.set_yticklabels([])
ax.set_ylabel("")

megalut.plot.figures.savefig(os.path.join(outdir, "%soverall_bias" % prefix), fig, fancy=True, pdf_transparence=True)
#------------------------------------------------------------
#------------------------------------------------------------
isubfig = 1
ncol = 3
nlines = int(np.ceil(len(param_feats) / (ncol*1.)))
fig = plt.figure(figsize=(12, 3 * nlines + 0.1))
plt.subplots_adjust(wspace=0.07)
plt.subplots_adjust(hspace=0.27)
plt.subplots_adjust(right=0.98)
plt.subplots_adjust(top=0.95)
plt.subplots_adjust(bottom=0.16)
import matplotlib.transforms as mtransforms
no_legend = True

assert "res" not in cat.colnames
lintresh = 2e-3

coln = 0
for iplot, featc in enumerate(param_feats):
	
	ax = fig.add_subplot(nlines, ncol, isubfig + iplot)
	
	trans = mtransforms.blended_transform_factory(ax.transAxes, ax.transData)
	ax.fill_between([0, 1], -lintresh, lintresh, alpha=0.2, facecolor='darkgrey', transform=trans)
	ax.axhline(0, ls='--', color='k')
	ax.set_ylabel(r"Shear bias")
	
	for icomp, comp in enumerate([component, component2]):
		
		main_pred = "s{}".format(comp)
		maincol = "tru_{}".format(main_pred)
		main_feat = Feature(maincol)
	
		cat["res"] = cat["pre_g{}_bias".format(comp)]
		
		xbinrange = megalut.plot.utils.getrange(cat, featc)
		binsumma = megalut.plot.utils.summabin(cat[maincol], cat["res"], xbinrange=xbinrange, nbins=nbins)
		
		cbinrange = megalut.plot.utils.getrange(cat, featc)
		
		cbinlims = np.array([np.percentile(cat[featc.colname], q) for q in np.linspace(0.0, 100.0, ncbins+1)])
		
		cbinlows = cbinlims[0:-1]
		cbinhighs = cbinlims[1:]
		cbincenters = 0.5 * (cbinlows + cbinhighs)
		assert len(cbincenters) == ncbins
		
		offsetscale = 0.5*((xbinrange[1] - xbinrange[0])/float(nbins))/float(ncbins)
		
		ms = []
		merrs = []
		cs = []
		cerrs = []
		for i in range(ncbins):
			
			offset = (i - float(ncbins)/2) * offsetscale
			
			# We build the subset of data that is in this color bin:
			selcbin = megalut.tools.table.Selector(featc.colname, [("in", featc.colname, cbinlows[i], cbinhighs[i])])
			cbindata = selcbin.select(cat)
			if len(cbindata) == 0:
				continue
			cbinfrac = float(len(cbindata)) / float(len(cat))
			
			# And we perform the line regression
			md = megalut.tools.metrics.metrics(cbindata,
				main_feat, # Redefining those to get rid of any rea settings that don't apply to cbindata
				megalut.tools.feature.Feature("res"),
				pre_is_res=True)
			
			ms.append(md["m"])
			merrs.append(md["merr"])
			cs.append(md["c"])
			cerrs.append(md["cerr"])
			#ax.plot(np.array(xbinrange), md["m"]*np.array(xbinrange)+md["c"], color=color, ls="-")
			
			
			# And now bin this in x:
			cbinsumma = megalut.plot.utils.summabin(cbindata[maincol], cbindata["res"], xbinrange=xbinrange, nbins=nbins, equalcount=False)
			
		if icomp == 0:
			markm = '*'
			markc = '^'
			color = 'k'
		elif icomp == 1:
			markm = 's'
			markc = 'v'
			color = 'r'
		labelc = r"$c_{%s}$" % (comp)
		labelm = r"$m_{%s}$" % (comp)
			
		ax.errorbar(cbinsumma["xbincents"]+offset, ms, yerr=merrs, color=color, marker=markm, label=labelm)
		ax.errorbar(cbinsumma["xbincents"]+offset, cs, yerr=cerrs, color=color, marker=markc, ls=':', label=labelc)

	#if (isubfig + iplot)/2+1 == nlines:
	#	ax.set_xlabel(r"$\mathrm{True\ shear}$")
	#else:
	#	ax.set_xticklabels([])
	
	
	ax.set_yscale('symlog', linthreshy=lintresh)
	ax.set_xlabel(featc.nicename)
	if featc.colname == "tru_g" or (iplot == len(param_feats) + 1 and no_legend):
		plt.legend(loc="best", handletextpad=0.07,fontsize="small", framealpha=0.5, columnspacing=0.1, ncol=2)
		no_legend = False
	
	ax.set_ylim([-1e-1, 1e-1])
	
	ticks = np.concatenate([np.arange(-lintresh, lintresh, 1e-3)])#, np.arange(lintresh, 1e-2, 9)])
	s = ax.yaxis._scale
	ax.yaxis.set_minor_locator(ticker.SymmetricalLogLocator(s, subs=[1., 2.,3.,4.,5.,6.,7.,8.,9.,-2.,-3.,-4.,-5.,-6.,-7.,-8.,-9.]))
	ticks = np.concatenate([ticks, ax.yaxis.get_minor_locator().tick_values(-.1, .1)])
	ax.yaxis.set_minor_locator(ticker.FixedLocator(ticks))
	
	if featc.low is not None and featc.high is not None:
		ax.set_xlim([featc.low, featc.high])
		#ax.locator_params(axis='x', nticks=2)
		tick_spacing = (featc.high - featc.low) / 5.
		ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
		ax.xaxis.set_major_formatter(ticker.FormatStrFormatter(r'$%0.3f$'))
		
	if coln > 0:
		ax.set_ylabel("")
		ax.set_yticklabels([])

	coln += 1
	if coln == ncol: coln = 0
megalut.plot.figures.savefig(os.path.join(outdir, "%sconditional_bias" % prefix), fig, fancy=True, pdf_transparence=True)
plt.show()

