# This file is intended for implementation trials of Euclid VIS characteristcs

import numpy as np
import pylab as plt
from astropy.table import Table
from scipy import stats
import skypropreties as sky

gems = Table.read('../thrid_party_data/gems_20090807.fits')

print gems.colnames

gems = gems[gems["GEMS_FLAG"] == 4]
#gems = gems[gems["ST_REERR_GALFIT"] / gems["ST_RE_GALFIT"] < 0.5]
gems = gems[gems["ST_FLUX_RADIUS"] >= 0.11/0.05*np.sqrt(2.)]

mags = gems["ST_MAG_GALFIT"]
gems["halflight_radius"] = gems["ST_FLUX_RADIUS"] * 0.05 / np.sqrt(2.)#35
sersicn = gems["ST_N_GALFIT"]

surface = 796. # http://www.mpia.de/homes/GEMS/gems.pdf, Rix+2004

bins = np.arange(19.75, 28., 0.5)

#######################################################################################################
# Magnitudes

N2025 = np.size(gems[np.logical_and(mags > 19.75, mags < 25.25)])
print N2025 

counts, bins = np.histogram(mags, bins=bins)


density = np.asarray(counts, np.float) / surface 
midbins = (bins[:-1] + bins[1:])/2

slope, intercept, r_value, p_value, std_err = stats.linregress(midbins[midbins <= 25],np.log10(density[midbins <= 25]))

nb = N2025
print slope
print intercept
magsim = sky.draw_magnitudes(nb * 10, 19.75, 25.25, slope, intercept)

binsim = np.arange(19.75, 25.5, 0.5)
midbinsim = (binsim[:-1] + binsim[1:])/2
counts, bins = np.histogram(magsim, bins=binsim)
density_sim = np.asarray(counts, np.float) / surface / 10.

yy = 10.**(midbins * slope + intercept)

plt.figure()
plt.plot(midbinsim, density_sim, alpha=0.5, c='r')
plt.plot(midbins, density)
plt.plot(midbins, yy, c='k', ls='--')
plt.yscale('log', nonposy='clip')
plt.xlim([20, 29.5])
plt.ylim([0.1, 310])
plt.xlabel("AB magnitude")
plt.ylabel(r"$N_\mathrm{gal}$ [per arcmin$^2$ per 0.5 mag]")

#######################################################################################################
# Size

mean_rh = []
width_rh = []
midbins = []
step_bin = 0.5
for binmin in np.arange(20.25, 25.25+step_bin, step_bin):
    cgal = gems[np.logical_and(gems["ST_MAG_GALFIT"] > binmin, gems["ST_MAG_GALFIT"] < binmin + step_bin)]
    log10rh = np.log10(cgal["halflight_radius"])
    #print cgal["halflight_radius"]
    midbins.append(binmin+step_bin/2.)
    mean_rh.append(np.mean(log10rh))
    width_rh.append(np.std(log10rh))

midbins = np.array(midbins)
mean_rh = np.array(mean_rh)
width_rh = np.array(width_rh)

ids_select_1 = np.logical_and(midbins >= 22.5, midbins <= 26)
ids_select_2 = np.logical_and(midbins >= 23, midbins <= 26)

slope_mean, intercept_mean, _, _, _ = stats.linregress(midbins[ids_select_1], mean_rh[ids_select_1])
slope_width, intercept_width, _, _, _ = stats.linregress(midbins[ids_select_2], width_rh[ids_select_2])

mm, ww = sky.get_size_params(midbins)

print 'mean', slope_mean, intercept_mean
print 'width', slope_width, intercept_width

plt.figure()
plt.scatter(midbins, mean_rh)
plt.plot(midbins, slope_mean * midbins + intercept_mean , c='k', ls='--')
plt.plot(midbins, mm, c='r', alpha=0.5)
plt.xlabel("AB magnitude")
plt.ylabel(r"$\langle\log_{10}(r_h/\mathrm{arcsec}) \rangle$")

plt.figure()
plt.scatter(midbins, width_rh)
plt.plot(midbins, slope_width * midbins + intercept_width , c='k', ls='--')
plt.plot(midbins, ww, c='r', alpha=0.5)
plt.xlabel("AB magnitude")
plt.ylabel(r"$\sigma_{\log_{10}(r_h)}$")
plt.ylim(0.05, 0.3)

rsim = sky.draw_sizes(magsim)

plt.figure()
plt.scatter(magsim, rsim, edgecolor="None", alpha=0.5)
plt.scatter(mags, gems["halflight_radius"], edgecolor="None", alpha=0.5, c='k')
plt.xlim([20, 25])

xmin = 20
xmax = 25
ymin = 0 
ymax = 2.

fig, axs = plt.subplots(ncols=2, sharey=True, figsize=(7, 4))
fig.subplots_adjust(hspace=0.5, left=0.07, right=0.93)
ax = axs[0]
hb = ax.hexbin(magsim, rsim, gridsize=50, bins='log', cmap='inferno')
ax.axis([xmin, xmax, ymin, ymax])
ax.set_title("Sims")
ax.set_ylabel("Half light radius in arcsec")

ax = axs[1]
hb = ax.hexbin(mags, gems["halflight_radius"], gridsize=50, bins='log', cmap='inferno')
ax.axis([xmin, xmax, ymin, ymax])
ax.set_title("GEMS")

#######################################################################################################
# Ellipticies

plt.figure()
plt.hist(sky.draw_ellipticities(10000), bins=200)
plt.xlabel("Ellipticies")

#######################################################################################################
# Sersic
step_bin=0.5
plt.figure()
"""
for binmin in np.arange(20.25, 25.25+step_bin, step_bin):
    cgal = gems[np.logical_and(gems["ST_MAG_GALFIT"] > binmin, gems["ST_MAG_GALFIT"] < binmin + step_bin)]
    plt.hist(cgal["ST_N_GALFIT"], bins=50, alpha=0.8, normed=True, histtype='step')
"""
plt.hist(gems["ST_N_GALFIT"], bins=50, alpha=0.8, normed=True, histtype='step')
plt.xlabel("Sersic n")

shape, loc, scale = stats.lognorm.fit(gems["ST_N_GALFIT"], floc=0)

print "SERSIC N"
print "shape:", shape
print "loc:", loc
print "scale", scale

sersicn, sbins = sky.draw_sersicn(100000) 
plt.hist(sersicn, bins=sbins, alpha=0.8, normed=True, histtype='stepfilled')
plt.figure()
plt.hist(sersicn, bins=np.size(sbins))

#######################################################################################################

plt.show()

