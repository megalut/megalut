"""
Shape measurement with AutoCorrelation Function
http://adsabs.harvard.edu/abs/1997A%26A...317..303V
"""

import numpy as np
#import math
#import random
import utils
import os
from datetime import datetime
import galaxy
#from lacf import QuadrupoleMoments
#from lacf import WindowedMoments
from lacf import QuadrupoleMoments,EllipticityGradients#,WindowedMoments
import sys

def run(imgfilepath, acfcatfilepath, assocfilepath, galaxies, **kwargs):
	"""
	Runs ACF on the image
	Depends on previous sextractor measurments !!! Must be run AFTER Sextractor run !!
	"""
	starttime = datetime.now()	
	
	if 'n_stamps' in kwargs: n_stamps = kwargs['n_stamps']
	else: n_stamps = 100
    
	print 'Running ACF measurements on %s. This could take a while...' % (imgfilepath)
	whole_image = utils.fromfits(imgfilepath)
	sx, sy = np.asarray(np.shape(whole_image))/np.array([n_stamps, n_stamps])
	init=np.zeros([sx,sy])

	# Initiate one instance of QuadrupoleMoments, we won't need more (plus it's better memory-wise).
	# I'm not sure it's the fastest way though.
	img = EllipticityGradients(init, show=False, verbose=False)

	# Save the ellipticity in the format g1, g2, ID
	gs = np.zeros([n_stamps,n_stamps,3])

	# assocfilepath is written for Sextractor, so we use it.
	assoc = np.loadtxt(assocfilepath)

	proposed_id = 0
	old_percent = -1

	for j in range(n_stamps):
        	for i in range(n_stamps):
			percent = 100.*proposed_id/n_stamps/n_stamps
			if old_percent < np.floor(percent):
				time_spent = datetime.now()-starttime
				if percent > 0:
					time_remaining = utils.timedelta_total_seconds(time_spent) /percent * (100.-percent)
				else:
					time_remaining = 0.
				message = '\r%3d%%. Approximate remaining time: %3.0f sec' % (percent, float(time_remaining))
				sys.stdout.write(message)
				sys.stdout.flush()
				old_percent=np.ceil(percent)
		
            		# Find nearest entry in catalogue using the stamp's centre
			cx = ((float(i)+0.5)*sx)
			cy = ((float(j)+0.5)*sy)
			if np.abs(assoc[proposed_id,0]-cx)<10 and np.abs(assoc[proposed_id,1]-cy)<10 :
				id_gal = proposed_id
			else:
				# Build a table with all possible candidates (x,y)
				# Alternative definitively faster way: build tree and look in there...
				# We give a tolerance of 10 pixels, this is huge ! In Great3, the centre of the galaxies are supposed to be close to the grid point.
				# The galaxy might be too faint to be measured by SExtractor!
				a = np.where(np.abs(assoc[:,0]-cx)<5)[0]
				b = np.where(np.abs(assoc[:,1]-cy)<5)[0]
				# Get which galaxy has both the right x and y coordinates
				if not np.shape(np.intersect1d(a,b))[0] == 0: 
					id_np = int(np.intersect1d(a,b)[0])
					if 'debug' in kwargs and kwargs['debug']:print 'I had to look up the galaxy\'s ID...'
					proposed_id = int(id_np)
				else:
					print 'No galaxy close to %d, %d found... Ignoring cell...' % (cx, cy)
					continue
				id_gal = int(assoc[id_np,2])
				
			# Change the data of the ACF instance to the stamp
			img.Set_data(whole_image[i*sx:(i+1)*sx,j*sy:(j+1)*sy])

			a, b, theta, radius, x_obj, y_obj, flux_g = galaxies[id_gal].getattrs(['mes_a','mes_b','mes_theta','mes_rad50','mes_x','mes_y','mes_flux'])
			x_obj -= i*sx
			y_obj -= j*sy

			if float(flux_g) < 0:
				continue

			img.ComputeACF(clip=False, weights='gaussian', a=a, b=b, theta=theta, radius=radius, x_obj=y_obj, y_obj=x_obj)
			img.ACF=img.ACF.T # Necessary here to have the correct sign convention
			img.Measure()
			mes_g1, mes_g2 = img.Get_Shear()
			gs[i,j,:]=[mes_g1, mes_g2, id_gal]
			#img.ShowACF()
			#if j > 2:exit()

			# Housekeeping things... Resetting to default values
			img.ClearMeasures()
			img.Set_ACF(None)
			img.Set_data(init)
			proposed_id+=1
			
			
	gs.resize([n_stamps*n_stamps,3])
	
	# Filter out all rows with all elements at 0.0 or any element at nan
	gs = gs[~np.all(gs==0.0, axis=1)]
	gs = gs[~np.isnan(gs).any(axis=1)]
	
	np.savetxt(acfcatfilepath, gs)	
	endtime = datetime.now()
	
	sys.stdout.write('\r')
	sys.stdout.flush()
	print "This ACF run took %s" % (str(endtime - starttime))

	

def readout(galaxies, acfcatfilepath):
	"""
	Reads in shape measurements from a ACF catalog.
	
	galaxies = a list of galaxy objects
	acfcatfilepath = path to acf catoalog
	
	I find each galaxy in the catalog, and get its measured shape.
	For this I use the "third col" assoc data of the acf catalog, which gives the ID of the galaxy.
	"""
	
	print "Reading catalog..."
	starttime = datetime.now()	

	cat = np.loadtxt(acfcatfilepath)
	print "We have %i galaxies in the acf catalog %s" % (np.shape(cat)[0], acfcatfilepath)
	
	print "Identifying galaxies..."
	
	gindexes = cat[:,2]
	notfound = 0
	cgal = 0

	for (gindex, g) in enumerate(galaxies):
		tid = gindex

		cgal+=1
		found_id = np.where(gindexes==tid)
		if np.size(found_id) == 1:
			i = found_id
		else:
#			print gindex
			notfound += 1
			g.mes_flux = -1.0
			continue
					
		g.mes_acf_g1 = cat[i,0][0][0]
		g.mes_acf_g2 = cat[i,1][0][0]
	
	endtime = datetime.now()

	print "I could identify %.2f%% of the galaxies (%i out of %i are missing)." % (100.0 * float(cgal-notfound) / float(cgal), notfound, cgal)
	print "This catalog-readout took %s" % (str(endtime - starttime))
