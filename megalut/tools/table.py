"""
Helpers for astropy.table arrays
"""

import astropy.table

import logging
logger = logging.getLogger(__name__)


def hjoin(table1, table2, idcol):
	"""
	This is a safe way to "hstack" two astropy tables containing different columns
	for the same sources, using a specified "ID" column.
	
	These kind of things are easy to do with astropy tables.
	The present function is just a wrapper for one type of operation that is very
	frequently required when running MegaLUT.

	Instead of a simple hstack (which would rely on the order of rows), here we use 
	join to identify the rows, using the idcol (i.e., "ID") column.
	We garantee that the ouput table will have the same number of 
	rows as the input tables.
	
	This function could be made more general/powerful (as join is much more general),
	but it is kept simple on purpose.
	
	:param table1: an astropy table
	:param table2: an astropy table
	:param idcol: a column name, to be used as key for the identification
	
	Columns that have the same name in table1 and table2 will be taken from table1.
	
	"""

	logger.debug("Starting some security checks (%i rows)..." % len(table1))
	
	if len(table1) != len(table2):
		raise RuntimeError("Your tables do not have the same lenghts!")
	
	
	if idcol not in table1.colnames:
		raise RuntimeError("There is no column '%s' in table1" % (idcol))
	if idcol not in table2.colnames:
		raise RuntimeError("There is no column '%s' in table2" % (idcol))
		
	set1 = set(table1[idcol])
	set2 = set(table2[idcol])
	if len(set1) != len(table1):
		raise RuntimeError("The IDs in table1 are not unique!")
	if len(set2) != len(table2):
		raise RuntimeError("The IDs in table2 are not unique!")
	if set1 != set2:
		raise RuntimeError("The IDs of your tables are not identical!")
		
	commoncols = [col for col in table1.colnames if (col in table2.colnames)]
	logger.info("The columns %s are common, I will keep those from table1." % (str(commoncols)))
	# Indeed, join would duplicate and rename those columns (even if they contain the same values)
	# Unless keys = None, in which case it would use them to identify.
	# But then, if those cols are different, the identification fails and join would silently keep
	# the "left" data, with masked values for the columns of table2.
	# What we want is to raise an Error if the idcol values are fishy.
	
	table2colstokeep = [col for col in table2.colnames if col not in commoncols]
	table2colstokeep.append(idcol)
	
	logger.debug("Done with security checks")
	
	output = astropy.table.join(table1, table2[table2colstokeep], keys=idcol, join_type='left', metadata_conflicts="error")

	assert len(output) == len(table1)
	assert len(output.colnames) == len(table1.colnames) + len(table2colstokeep) - 1
	
	return output
	

	
