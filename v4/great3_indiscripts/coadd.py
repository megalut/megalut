import numpy as np
import math
import random
import utils
import os
import asciidata
from datetime import datetime
import math
import utils
import sys

###############################################################
min_snr=200
factor=64
simsubfields=range(0,200,20)
skipdone=True
branch=['variable_psf','ground','variable']
great3_dir = '/scratch/kuntzer/GREAT3_DATA'
workdir = '/scratch/kuntzer/current_ML/PSF_coadd'
version='snr%d' % min_snr
################################################################

def run(imgfilepath, sexcatfilepath, assocfilepath):
	"""
	Runs sextractor on the image
	"""

	starttime = datetime.now()	

	sexparamsdir = os.path.join(os.path.dirname(__file__), "sexparams")
	settings_sex = os.path.join(sexparamsdir, "stars.sex")
	settings_param = os.path.join(sexparamsdir, "stars.param")
	settings_conv = os.path.join(sexparamsdir, "default.conv")

	cmd = "nice -n 10 sex %s -c %s -PARAMETERS_NAME %s -FILTER_NAME %s -CATALOG_NAME %s -ASSOC_NAME %s" % ( imgfilepath, 
		settings_sex, settings_param, settings_conv, sexcatfilepath, assocfilepath)
	print "Running SExtractor on image %s ..." % imgfilepath
	os.system(cmd)
	
	endtime = datetime.now()
	print "This SExtractor run took %s" % (str(endtime - starttime))

def load_catalog(sexcatfilepath):
	return asciidata.open(sexcatfilepath)

def upsample(a, newshape):
	'''
	Rebin an array to a new shape.
	'''
	assert len(a.shape) == len(newshape)
	fact = float(a.shape[0]) / float(newshape[0])
	slices = [ slice(0,old, float(old)/new) for old,new in zip(a.shape,newshape) ]
	coordinates = np.mgrid[slices]
	indices = coordinates.astype('i')   #choose the biggest smaller integer index
	return a[tuple(indices)] * fact**2.

def downsample(a, newshape):
	'''
	rebin ndarray data into a smaller ndarray of the same rank whose dimensions
	are factors of the original dimensions. eg. An array with 6 columns and 4 rows
	can be reduced to have 6,3,2 or 1 columns and 4,2 or 1 rows.
	example usages:
	>>> a=rand(6,4); b=rebin(a,(3,2))
	>>> a=rand(6); b=rebin(a,2)
	'''
	shape = a.shape
	lenShape = len(shape)
	factor = np.asarray(shape)/np.asarray(newshape)
	evList = ['a.reshape('] + \
		 ['newshape[%d],factor[%d],'%(i,i) for i in xrange(lenShape)] + \
		 [')'] + ['.sum(%d)'%(i+1) for i in xrange(lenShape)]
	return eval(''.join(evList))

def writeassoc(star_catalog,assocfile):
	"""
	Function to write an "assoc-list" for sextractor, from a list of stars objects.
	It adds the "index" of a star in the stars list as a third column.
	"""
	
	# We cannot use the galaxy ID here as it is too long.
	# At some point sextractor will write the ID as an rounded float and thus loose it !
	
	stars=np.loadtxt(star_catalog)
	lines = []
	lines.append("# X\n# Y\n# ID\n# x_tile_index\n# y_tile_index\n")
	for (sindex, s) in enumerate(stars):
		lines.append("%.3f\t%.3f\t%i\t%i\t%i\n" % (s[0], s[1], sindex,s[2],s[3]))

	lines = "".join(lines)
	f = open(assocfile, "w")
	f.writelines(lines)
	f.close()
	print "Wrote %s" % assocfile

def extract(img, center,size,factor,upsampled=False):
	size = np.asarray(size)*factor
	center=np.asarray(center)*factor
	if not upsampled: img=upsample(img,np.asarray(np.shape(img))*factor)
	x0,xf,y0,yf = int(center[0])-size[0]/2,int(center[0])+size[0]/2,int(center[1])-size[1]/2,int(center[1])+size[1]/2
	return img[x0:xf,y0:yf]

#################################################################
if branch[1]=='ground': 
	ntiles=5
	s=48
elif branch[1]=='space':
	ntiles=20
	s=96

if branch[2]=='variable': nsubfield=2
elif branch[2]=='constant': nsubfield=1

indir = os.path.join(great3_dir, "/".join(branch))
workdir = os.path.join(workdir, "psfs-" + "-".join(branch) + '-%s' % version)

if not os.path.isdir(workdir):
	os.mkdir(workdir)

#################################################################
for simsubfield in simsubfields:
	msg = 'Coadding PSF for simsubfield %03d' % simsubfield
	print msg
	print len(msg)*'-'
	subfields=range(simsubfield,simsubfield+nsubfield)

	all_psfs=[[None for i in range(ntiles)] for j in range(ntiles)]

	for subfield in subfields:
		imgfilepath=os.path.join(indir, 'starfield_image-%03d-0.fits' % (subfield))
		star_catalog=os.path.join(indir, 'star_catalog-%03d.txt' % (subfield))
		assocfile=os.path.join(workdir, 'starassoc-%03i.txt' % (subfield))
		sexcatfilepath=os.path.join(workdir, 'stars-%03d.sex' % (subfield))
	
		if skipdone and os.path.exists(sexcatfilepath): 
			msg = '\rLoading subfield %03i...' % (subfield)
			sys.stdout.write(msg)
			sys.stdout.flush()
		else: 
			writeassoc(star_catalog,assocfile)
			run(imgfilepath,sexcatfilepath,assocfile)
		data = load_catalog(sexcatfilepath)

		img=utils.fromfits(imgfilepath)

		for ix in range(ntiles):	
			for iy in range(ntiles):
				#if ix > 0 or iy > 0: continue
				msg = '\rTreating %03i -- %02ix%02i...' % (subfield, ix, iy)
				sys.stdout.write(msg)
				sys.stdout.flush()
				for d in range(np.shape(data)[1]):
					if data["FLUX_AUTO"][d]/data["FLUXERR_AUTO"][d]<min_snr: continue
					if (not data["VECTOR_ASSOC3"][d]==ix) or (not data["VECTOR_ASSOC4"][d]==iy): continue
					#print data["VECTOR_ASSOC3"][d], data["VECTOR_ASSOC4"][d], data["FLUX_AUTO"][d]/data["FLUXERR_AUTO"][d]
	

					stamp = img[data["VECTOR_ASSOC"][d]-s/2+1:data["VECTOR_ASSOC"][d]+s/2+1,data["VECTOR_ASSOC1"][d]-s/2+1:data["VECTOR_ASSOC1"][d]+s/2+1]

					#print data["VECTOR_ASSOC"][d]-s/2+1,data["VECTOR_ASSOC"][d]+s/2+1,data["VECTOR_ASSOC1"][d]-s/2+1,data["VECTOR_ASSOC1"][d]+s/2+1, np.shape(stamp), (s/2-1)
	
					#corx,cory= data["XWIN_IMAGE"][d]-data["VECTOR_ASSOC"][d],data["YWIN_IMAGE"][d]-data["VECTOR_ASSOC1"][d]
					
					#corx,cory=data["VECTOR_ASSOC"][d]-23,data["VECTOR_ASSOC1"][d]-23
					#print '\t',corx,cory

					corx = data["VECTOR_ASSOC"][d]-s/2+1
					cory = data["VECTOR_ASSOC1"][d]-s/2+1

					tmpimg=extract(stamp, [data["XWIN_IMAGE"][d]-corx,data["YWIN_IMAGE"][d]-cory],[s-4,s-4], factor, upsampled=False)
	
					if np.size(tmpimg)<2:continue
					if all_psfs[ix][iy]==None:
						all_psfs[ix][iy]=tmpimg
					else:
						all_psfs[ix][iy]+=tmpimg

				
				"""f, (ax1,ax2) = plt.subplots(1,2)
				CS=ax1.contourf(XX,YY,(all_psfs[ix][iy]),50)
				plt.colorbar(CS,orientation='horizontal')
				ax1.set_title('all_psfs')
				CS=ax2.contourf(XX,YY,(tmpimg),50)
				plt.colorbar(CS)
				plt.show()
				
		
				print '-------'"""


	sys.stdout.write('\rAll PSFs coadded, saving...\n')
	sys.stdout.flush()

	for ix in range(ntiles):
		for iy in range(ntiles):
			psffilepath=os.path.join(workdir, 'coadpsf-%03d-%02ix%02i.fits' % (simsubfield, ix, iy))
			utils.tofits(downsample(all_psfs[ix][iy],[s-4,s-4]), psffilepath)
####################################################################

