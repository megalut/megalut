import megalut
import astropy
import config
import glob
import os

import logging
logger = logging.getLogger(__name__)


fitsfiles = sorted(glob.glob(os.path.join(config.truedistdir, "files/*.fits")))

logger.info("Found {} files".format(len(fitsfiles)))

tables = []
for fitsfile in fitsfiles:
	print fitsfile
	table = astropy.table.Table.read(fitsfile)
	
	# Now we attribute the disk height ratios:
	filename = os.path.split(fitsfile)[-1] # sensitivity_testing_deep_ep2_1_8_dither_0_details.fits
	ecode = filename[25:28] # em1
	dhrs = {"em2":0.02, "em1":0.06, "ep0":0.1, "ep1":0.2, "ep2":0.3} 
	assert ecode in dhrs.keys()
	table["disk_height_ratio"] = dhrs[ecode]
	table["ecode"] = ecode
	
	#print table.colnames
	tables.append(table)


table = astropy.table.vstack(tables, join_type='exact', metadata_conflicts='error')

print megalut.tools.table.info(table)

megalut.tools.io.writepickle(table, config.truedistpath)
