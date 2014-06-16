"""
This is a tiny standalone module to plot the aperture mass variances from GREAT3 variable-shear submission files.
Use it as a module, or as a script:

	python amvplot.py submissionfile1.txt submissionfile2.txt ...

"""

import sys, os
import glob
import numpy as np
import matplotlib.pyplot as plt


class Submission:
	"""
	Tiny class to hold the content of a submission file
	"""

	def __init__(self, fielddata, score = None, name="test", color="red"):
		"""
		Constructor
		The attribute fielddata is a list of numpy arrays, and each of these arrays
		is a corresponding "section" of the table from the submission file.
		"""
		self.fielddata = fielddata
		self.name = name
		self.color = color
		self.score = score
	
	
	@classmethod
	def fromfile(cls, filepath, score = None, name=None, color="red"):
		"""
		Another constructor, that reads from a submission file.
		"""
		data = np.loadtxt(filepath)
		fielddata = np.vsplit(data, 10)
		if name == None:
			name = os.path.basename(filepath)
		return cls(fielddata=fielddata, score=score, name=name, color=color)
        
	def __str__(self):
		if self.score != None:
			return "%s (%.1f)" % (self.name, self.score)
		else:
			return self.name

def colorize(submissions):
	"""
	Attributes nice colors to a list of submission objects
	"""
	colors = ["red", "blue", "green", "purple", "orange", "brown"]
	for (color, submission) in zip(colors, submissions):
		submission.color = color
     

def plot(submissions, filepath=None):
	"""
	Builds the plot, based on a provided list of Submission objects.
	
	:param filepath: If provided, I write the plot into this file, instead of showing it.
	"""

	fields = range(0, 10)
	fig = plt.figure(figsize=(15, 10))
	fig.subplots_adjust(bottom=0.08, top=0.97, right=0.97, left=0.08, wspace=0.02, hspace=0.02)
	
	
	for field in fields:
		ax = fig.add_subplot(3, 4, field+1)
		
		ax.plot([0.01, 10.0], [0.0, 0.0], color="black", linestyle="-")
		
		for sub in submissions:
			data = sub.fielddata[field]
			assert np.allclose(data[:,0], field) # Just checking that this is the right field !
			
			rs = data[:,1]
			apmassvarEs = data[:,2]
			apmassvarBs = data[:,3]
			apmassvarsigs = data[:,4]
			
			ax.plot(rs, apmassvarEs*1.0e6, color=sub.color, linestyle="-", lw=1)
			ax.plot(rs, apmassvarBs*1.0e6, color=sub.color, linestyle="--", lw=1)
			ax.plot(rs, apmassvarsigs*1.0e6, color=sub.color, linestyle=":", lw=1)
			
			ax.set_xscale("log")
		
		ax.set_xlim(0.01, 10.0)
		ax.set_ylim(-14.0, 19.0)
		ax.grid()
		
		ax.text(0.05, 0.92,"Field %i" % (field),
			verticalalignment='center',
			transform=ax.transAxes)
			
		if field == 8:
			plt.xlabel('$\\theta$ [deg]')
			plt.ylabel("Aperture mass variance $\\times$ $10^{6}$")
		else:
			ax.xaxis.set_ticklabels([])
			ax.yaxis.set_ticklabels([])
	
	legx = 0.54
	legy = 0.3
	legystep = 0.02
	fig.text(legx, legy + legystep, "Submissions: (continuous line is E-mode, dashed is B-mode, dotted is error)", color="black")		
	for (subi, sub) in enumerate(submissions):
		fig.text(legx, legy -subi*legystep, str(sub), color=sub.color)		
		
	if filepath != None:
		plt.savefig(filepath)
		print "Wrote %s" % (filepath)
	else:
		plt.show()
		

if __name__ == "__main__":
	"""
	Then we take all arguments as filepathes to submission files and plot them
	"""
	
	submissions = [Submission.fromfile(filepath) for filepath in sys.argv[1:]]
	colorize(submissions)
	plot(submissions)
	




# Some info about the ouptut file format, from the respective manuals and scripts:

"""
In the GREAT3 submission files we have:
field
R
<Map^2>
<Mx^2>
sig_map


The output of corr2 :

#     R     .  <Map^2>  .   <Mx^2>  .  <MMx>(a) .  <MMx>(b) .  sig_map  .  <Gam^2>  .  sig_gam

m2_file_name = (str) The output filename for the aperture mass statistics.

    This file outputs the aperture mass variance and related quantities, 
    derived from the shear-shear correlation function.  The output columns are:

    R = The radius of the aperture.  (Spaced the same way as  R_nominal is 
        in the correlation function output files.

    <Map^2> = The E-mode aperture mass variance for each radius R.

    <Mx^2> = The B-mode aperture mass variance.

    <MMx>(a), <MMx>(b) = Two semi-independent estimate for the E-B cross term.
                         (Both should be consistent with zero for parity
                         invariance shear fields.)

    sig_map = The 1-sigma error bar for these values.

    <Gam^2> = The variance of the top-hat weighted mean shear in apertures of 
              the given radius R.

    sig_gam = The 1-sigma error bar for <Gam^2>.

"""

