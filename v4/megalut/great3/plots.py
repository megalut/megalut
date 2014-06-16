import os
import numpy as np
import matplotlib.pyplot as plt
import megalut
import amvplot

def ellipticity(gs):
	return np.sqrt(gs[:,1]**2+gs[:,0]**2)




def plot_results(submissionfilepath, shear, fig_dir=None, title=None):

	if shear == 'constant' :
	
		shear_vals = np.loadtxt(submissionfilepath)
		ids = shear_vals[:,0]

	
		plt.figure()
		ellip = ellipticity(shear_vals[:,1:3])
		nbins=10
		n, bins, patches = plt.hist(ellip,bins=nbins,normed=1, histtype= 'step', label='ellip')
		plt.setp(patches, 'color', 'r', 'alpha', 0.75,linewidth=2)

		n, bins, patches = plt.hist(shear_vals[:,1],bins=nbins,normed=1, histtype= 'step', label='g1')
		plt.setp(patches, 'color', 'g', 'alpha', 0.75, linewidth=2)

		n, bins, patches = plt.hist(shear_vals[:,2],bins=nbins,normed=1, histtype= 'step', label='g2')
		plt.setp(patches, 'color', 'k', 'alpha', 0.75, linewidth=2)
		
		plt.legend(loc='best')
		plt.grid()
		if fig_dir:
			plt.savefig(os.path.join(fig_dir, 'corr2.png'))
		else:
			plt.show()
			
	elif shear == 'variable' :
		
		sub = amvplot.Submission.fromfile(submissionfilepath)
		
		if fig_dir:
			figfilepath = os.path.join(fig_dir, "amvplot.pdf")
		else:
			figfilepath = None
			
		amvplot.plot([sub], filepath=figfilepath)

		
		"""
		from matplotlib.ticker import FuncFormatter

		def format_y_axis(y, position):
			return y*1e6

		def select_field(data, n):
			which = np.where(data[:,0]==n)
			return data[which,:][0]

		for f in range(10):
			fig=plt.figure()
			fig.subplots_adjust(bottom=0.12, top=0.93, right=0.96, left=0.11)
			ax = fig.add_subplot(111)
			field = select_field(shear_vals, f)
			bins  = field[:,1]
			emode = field[:,2]
			bmode = field[:,3]
			aperture_M_error = field[:,4]

			plt.plot(bins, emode, lw=2, label='E-mode')
			plt.plot(bins, bmode, lw=2, label='B-mode')
			plt.plot(bins, aperture_M_error, lw=2, label='Apert. Mass Error')
			plt.xlabel('$\\theta$ Bin angle [degree]')
			plt.ylabel('Correlation function')
			plt.gca().set_xscale("log")

			formatter = FuncFormatter(format_y_axis)
			ax=plt.gca()

			ax.yaxis.set_major_formatter(formatter)
			plt.text(-0.02, 1.02,'$\\times 10^{-6}$', transform = ax.transAxes)

			plt.legend(loc='best')
			plt.grid()
			if not title == None: plt.title(title)

			if fig_dir:
				plt.savefig(os.path.join(fig_dir, 'corr2_field%d.png' % f ))
			else:
				plt.show()
			
			
			"""
	else:
		raise ValueError('Shear type %s not understood' % shear)


