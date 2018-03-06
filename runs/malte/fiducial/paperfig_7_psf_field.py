import config
import os
import numpy as np
import megalut.plot

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Arrow, FancyArrowPatch
import megalut.plot.figures as figures
import matplotlib.ticker as ticker

import simparams

import logging
logger = logging.getLogger(__name__)


from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)

fig = plt.figure(figsize=(8,4.0))

w = 0.3
cbarw = 0.02
h = 0.6

ax1 = fig.add_axes([0.1, 0.2, w, h])
ax2 = fig.add_axes([0.5, 0.2, w, h])
ax3 = fig.add_axes([0.82, 0.2, cbarw, h])


extra_space = 0.1

#ax1 = plt.subplot(1, 3, 1)
X1D = np.linspace(0.0, 1.0, 9)
Y1D = np.linspace(0.0, 1.0, 9)

for x in X1D:
	for y in Y1D:
	
		psf = simparams.psf_field_1(x, y)
		x = psf["tru_psf_x"]
		y = psf["tru_psf_y"]
		
		gscale = 0.55
		g1 = gscale * psf["tru_psf_g1"]
		g2 = gscale * psf["tru_psf_g2"]
		
		arrow = FancyArrowPatch(posA=(x-g1/2.0, y-g2/2.0), posB=(x+g1/2.0, y+g2/2.0), path=None, arrowstyle='-|>', mutation_scale=6, fc="black")
		ax1.add_artist(arrow)
		
		
#ax1.set_aspect('equal')
ax1.set_xlim([0-extra_space, 1+extra_space])
ax1.set_ylim([0-extra_space, 1+extra_space])

ax1.set_xlabel(r"$x$ position in field")
ax1.set_ylabel(r"$y$ position in field")

ax1.set_title(r"PSF field in ($\varepsilon_1$, $\varepsilon_2$)-space")



#ax2 = plt.subplot(1, 3, 2)

cmap = matplotlib.cm.get_cmap("plasma")

fwhmpersigma = 2.3548
minsigma = 1.75
maxsigma = 2.25

norm = matplotlib.colors.Normalize(vmin=minsigma * fwhmpersigma, vmax=maxsigma * fwhmpersigma)

X1D = np.linspace(0.0, 1.0, 9)
Y1D = np.linspace(0.0, 1.0, 9)
	
for x in X1D:
	for y in Y1D:
	
		psf = simparams.psf_field_1(x, y)
		x = psf["tru_psf_x"]
		y = psf["tru_psf_y"]
		
		escale = 0.03
		a = escale * psf["tru_psf_a"]
		b = escale * psf["tru_psf_b"]
		ellipse = Ellipse((x, y), a, b, np.rad2deg(psf["tru_psf_theta"]))		
		#ellipse.set_clip_box(ax2.bbox)
		ellipse.set_facecolor(cmap(norm(psf["tru_psf_sigma"] * fwhmpersigma)))
		ax2.add_artist(ellipse)


#ax3 = plt.subplot(1, 3, 3)
#pos3 = ax3.get_position()
#pos2 = ax2.get_position()

#ax3.set_position((pos2.x0 + pos2.width + 0.1, pos2.y0,  pos3.width / 20.0, pos2.height))


cbar = matplotlib.colorbar.ColorbarBase(ax3, cmap=cmap, norm=norm, orientation='vertical')
cbar.set_label(r'FWHM [pix]')
			
#ax2.set_aspect('equal')
ax2.set_xlim([0-extra_space, 1+extra_space])
ax2.set_ylim([0-extra_space, 1+extra_space])
ax2.set_xlabel(r"$x$ position in field")
ax2.set_ylabel(r"$y$ position in field")
ax2.set_title(r"PSF field in real space")

#plt.tight_layout()
plt.savefig(os.path.join(config.valdir, "psf_field.pdf"))
plt.show()



