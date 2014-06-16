import os
import astropy.io.fits as pyfits
import numpy as np

indir='/scratch/kuntzer/GREAT3_DATA/truth'
outdir='../true_amv/'
branch=['multiepoch','space','variable']
skipdone=False
subfields=range(200)
########################################################################

def presubmission(outfilepath, outdir, branch, corr2path=".", use_weights=False):
	"""
	Prepares the submission by computing the correlation functions.
		
	For this it uses the "presubmission_scripts", that are now part of this SVN.
	Watch for updates from GREAT3 !
	"""

	presubdir = os.path.join(os.path.dirname(__file__), "presubmission_script")
	presubscriptpath = os.path.join(presubdir, "presubmission.py")
	catpath = os.path.join(outdir, "*.cat")
	branchcode = "-".join(branch) # Not required given our filenames, but just to be sure.
	corr2path = os.path.join(corr2path, 'corr2')
		
	if use_weights:
		cmd = "python %s %s -b %s -w 3 -c2 %s -o %s" % (presubscriptpath, catpath, branchcode, corr2path, outfilepath)
	else:
		print "I am NOT using weights !"
		cmd = "python %s %s -b %s -c2 %s -o %s" % (presubscriptpath, catpath, branchcode, corr2path, outfilepath)
	os.system(cmd)

###########################################################################
outfilepath='amv_'+''.join([s[0] for s in branch])+'.txt'
outfilepath=os.path.join(outdir, outfilepath)

indir = os.path.join(indir, '/'.join(branch))

filedir = os.path.join(outdir, '/'.join(branch))

if not os.path.exists(filedir): os.makedirs(filedir)

for i in subfields:
	outfname = os.path.join(filedir, '%03d.cat' % i)
	if os.path.exists(outfname) and skipdone: 
		print 'Skipping %d...' %i
		continue

	print 'Subfield %s %03d...' % (''.join([s[0] for s in branch]),i)

	fname=os.path.join(indir,'galaxy_catalog-%03d.fits' % i)
	hdulist = pyfits.open(fname)

	table = hdulist[1].data
	IDs= np.asarray(hdulist[1].data['ID'])
	g1 = np.asarray(hdulist[1].data['g1'])+np.asarray(hdulist[1].data['g1_intrinsic'])
	g2 = np.asarray(hdulist[1].data['g2'])+np.asarray(hdulist[1].data['g2_intrinsic'])

	truths_gs = np.asarray([IDs,g1,g2]).T
	#exit()
	#thruths_gs=np.zeros([len(table),3])
	#for rid, r in enumerate(table):
	#	thruths_gs[rid] = np.asarray([r[0],r[1]+r[3],r[2]+r[4]])

	np.savetxt(outfname, truths_gs, fmt="%10i\t%+.6f\t%+.6f")
		
presubmission(outfilepath,outdir=filedir,branch=branch,corr2path="/scratch/kuntzer/current_ML/megalut/great3/presubmission_script")
