import os
import astropy.io.fits as pyfits
import numpy as np
import pylab as plt

compare_to='/scratch/kuntzer/current_ML/out-variable_psf-ground-variable-tpt-tiny/'
indir='/scratch/kuntzer/GREAT3_DATA/truth'
datadir='/scratch/kuntzer/GREAT3_DATA'
outdir='../true_ps/'
branch=['variable_psf','ground','variable']
skipdone=True
subfields=[0]#range(20)
tile_index=[0,0]
corr2path='/scratch/kuntzer/current_ML/megalut/great3/presubmission_script/corr2'
# Parameters for the correlation function
min_sep = 0.02 # in degrees
max_sep = 10.0 # in degrees
nbins = 15
########################################################################

def find_galaxies(catalog_fname, tile_index):
	catalog=np.loadtxt(catalog_fname)
	listid0 = catalog[:,3]==tile_index[0]
	listid1 = catalog[:,4]==tile_index[1]
	listid=[idd for idd, (A, B) in enumerate(zip(listid0, listid1)) if (A & B)]
	return np.asarray(catalog[listid,2], dtype=np.int), np.asarray(catalog[listid,7:])

def presubmission(outfilepath, outdir, branch, corr2path=corr2path, use_weights=False):
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

def out_fname(i, tileindex):
	return os.path.join(filedir, '%03d-tile-%02dx%02d.cat' % (i,tile_index[0],tile_index[1]))

def print_basic_corr2_params(outfile, min_sep=min_sep, max_sep=max_sep, nbins=nbins,
			  xy_units='degrees', sep_units='degrees',fits_columns=False):
	"""
Write a bare-bones corr2.params file (used by corr2) to the file named outfile.
"""
	with open(outfile, 'wb') as fout:
		if fits_columns:
			fout.write("# Column description\n")
			fout.write("x_col = x\n")
			fout.write("y_col = y\n")
			fout.write("g1_col = g1\n")
			fout.write("g2_col = g2\n")
			fout.write("w_col = w\n")
			fout.write("\n")
			fout.write("# File info\n")
			fout.write("file_type=FITS")
		else:
			fout.write("# Column description\n")
			fout.write("x_col = 1\n")
			fout.write("y_col = 2\n")
			fout.write("g1_col = 3\n")
			fout.write("g2_col = 4\n")
			fout.write("w_col = 5\n")
		fout.write("\n")
		fout.write(
			"# Assume sign conventions for gamma were correct in the catalog passed to "+
			"presubmission.py\n")
		fout.write("flip_g1 = false\n")
		fout.write("flip_g2 = false\n")
		fout.write("\n")
		fout.write("# Describe the parameters of the requested correlation function\n")
		fout.write('min_sep=%f\n'%min_sep)
		fout.write('max_sep=%f\n'%max_sep)
		fout.write('nbins=%f\n'%nbins)
		fout.write('x_units='+str(xy_units)+'\n')
		fout.write('y_units='+str(xy_units)+'\n')
		fout.write('sep_units='+str(sep_units)+'\n')
		fout.write('\n')
		fout.write("# verbose specifies how much progress output the code should emit.\n")
		fout.write("verbose = 0\n")
		fout.write("\n")

def run_corr2_ascii(x, y, e1, e2, w, min_sep=min_sep, max_sep=max_sep, nbins=nbins,
					cat_file_suffix='_temp.cat', params_file_suffix='_corr2.params',
					m2_file_suffix='_temp.m2', xy_units='degrees', sep_units='degrees',
					corr2_executable='corr2'):
	"""
Stolen from some scripts by Barney Rowe. This runs the corr2 code on a temporary
catalog generated from lists of positions, shears, and weights, and returns the contents
of the output file from corr2.
"""
	import subprocess
	import tempfile
	# Create temporary, unique files for I/O
	catfile = tempfile.mktemp(suffix=cat_file_suffix)
	paramsfile = tempfile.mktemp(suffix=params_file_suffix)
	m2file = tempfile.mktemp(suffix=m2_file_suffix)
	# Write the basic corr2.params to temp location
	print_basic_corr2_params(paramsfile, min_sep=min_sep, max_sep=max_sep, nbins=nbins,
							 xy_units=xy_units, sep_units=sep_units)

	# Write catfile and run corr2
	f = open(catfile, 'wb')
	for (xi, yi, e1i, e2i, wi) in zip(x, y, e1, e2, w):
		if e1i < 10. and e2i < 10.:
			f.write('%e %e %e %e %e\n' % (xi, yi, e1i, e2i, wi))
	f.close()
	print [corr2_executable, str(paramsfile), 'file_name='+str(catfile), 'm2_file_name='+str(m2file)]
	subprocess.Popen([
		corr2_executable, str(paramsfile), 'file_name='+str(catfile), 'm2_file_name='+str(m2file),
		]).wait() ##<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<TODO TODO TODO TODO
	os.remove(paramsfile)
	os.remove(catfile)
	if not os.path.isfile(m2file):
		raise RuntimeError('Corr2 output file does not exist--this usually indicates an error '
						   'within corr2 itself. Please check output stream for error '
						   'messages.')
	results = readfile(m2file)
	os.remove(m2file)
	return results
###########################################################################
# INITIALISATION

datadir = os.path.join(datadir, '/'.join(branch))
indir = os.path.join(indir, '/'.join(branch))

filedir = os.path.join(outdir, '/'.join(branch))

if not os.path.exists(filedir): os.makedirs(filedir)
#############################################################################
for i in subfields:
	outfname=out_fname(i, tile_index)
	
	if os.path.exists(outfname) and skipdone: 
		print 'Skipping %d...' %i
		continue

	print 'Subfield %s %03d...' % (''.join([s[0] for s in branch]),i)

	catalog_fname=os.path.join(datadir,'galaxy_catalog-%03d.txt' % i)
	listid,_=find_galaxies(catalog_fname, tile_index)

	fname=os.path.join(indir,'galaxy_catalog-%03d.fits' % i)
	hdulist = pyfits.open(fname)

	table = hdulist[1].data
	truths_gs=[]
	for rid, r in enumerate(table):
		if not r[0] in listid: continue
		truths_gs.append([r[0], r[1]+r[3], r[2]+r[4]])
	truth = np.asarray(truths_gs)

	np.savetxt(outfname, truth, fmt="%10i\t%+.6f\t%+.6f")
#############################################################################
for i in subfields:
	outfname=out_fname(i, tile_index)

	compare_to=os.path.join(compare_to, '%03d.cat' % (i))

	truth=np.loadtxt(outfname)
	predicted=np.loadtxt(compare_to)

	catalog_fname=os.path.join(datadir,'galaxy_catalog-%03d.txt' % i)
	listid,xy=find_galaxies(catalog_fname, tile_index)

	current_predicted=[]
	for g in predicted:
		if not g[0] in listid: continue
		current_predicted.append(g)
	current_predicted=np.asarray(current_predicted)

	results = run_corr2_ascii(
			xy[:,0],xy[:,1], current_predicted[:,1], current_predicted[:,2], np.zeros_like(xy[:,0]), min_sep=min_sep, max_sep=max_sep,
			nbins=nbins, xy_units='degrees', sep_units='degrees', corr2_executable=corr2path)

	print results
	exit()
	plt.figure(figsize=(14,7))
	plt.subplot(121)
	plt.plot(truth[:,1],current_predicted[:,1]-truth[:,1],'.')
	plt.plot([-0.7,0.7],[0,0],lw=2)
	plt.grid()

	#plt.axis('equal')
	plt.xlim([-0.7,0.7])
	plt.ylim([-0.4,0.4])

	plt.subplot(122)
	plt.plot(truth[:,2],current_predicted[:,2]-truth[:,2],'.')
	plt.plot([-0.7,0.7],[0,0],lw=2)
	plt.grid()

	#plt.axis('equal')
	plt.xlim([-0.7,0.7])
	plt.ylim([-0.4,0.4])
	plt.show()


