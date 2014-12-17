"""

"""

import sys
import os

import image

class ImageInfo():
	"""
	Class to structure meta-data related to an image (stored in a FITS file) inside the meta dict of a catalog (astropy.table) object.
	Putting objects of this class in a catalogs's meta dict "links" an image file to that catalog.
	This way a catalog can have links to many images (galaxy stamps, PSF stamps, multiple exposures, filters...)
	
	When working with simple single-exposure images, the convention that shape measurement functions are asked to understand is that
	the galaxy stamp image is described in catalog.meta["img"], and (optionally) the PSF stamp image is in catalog.meta["psf"].
	We can derive a more sophisticated hierarchical structure when needed.
	"""

	def __init__(self, filepath, xname="x", yname="y", stampsize=None, name=None, workdir=None):
		"""
		:param filepath: absolute path to the FITS image
		:type filepath: string
		:param xname: catalog column name containing the x coordinate of the center of the stamp
		:type xname: int
		:param yname: idem for y
		:type yname: int
		:param stampsize: width and height of a stamp, in pixels, if the image consists of gridded stamps.
			Leave it to None if the image does not hold stamps.
		:type stampsize: int
		:param name: a name for the image. By default (None) the filename will be used, but sometimes
			it might be helpful to specify different names. Functions use these names to refer to the image in logs etc.
		:type name: string
		:param workdir: path to a working directory for this image
		:type imgname: string	
		"""
		
		self.filepath = filepath
		self.xname = xname
		self.yname = yname
		self.stampsize = stampsize

		
		if name is None:
			self.name = os.path.splitext(os.path.basename(filepath))[0]
		else:
			self.name = name
		
		self.workdir = workdir # To be developed...
				

	def __str__(self):
		"""
		Retruns a short description of this object
		"""
		return "ImageInfo(%s, %s, %s, %s)" % (self.name, self.xname, self.yname, self.stampsize)

	def __repr__(self):
		"""
		Returns str(self) -- convenient when printing catalog.meta.
		"""
		return self.__str__()

	def load(self):
		"""
		Returns the image as GalSim Image object.
		"""
		return image.loadimg(self.filepath)


	def checkcolumns(self, catalog):
		"""
		Verifies that the attributes xname and yname are available as columns in the given catalog.
		If not, raises a nicely descriptive RuntimeError.
		As this is such a common check, a dedicated method seems appropriate.
		"""
		if not (self.xname in catalog.colnames and self.yname in catalog.colnames):
			raise RuntimeError("The columns (%s, %s) are not among the ones available in the catalog: %s"\
				% (self.xname, self.yname, catalog.colnames))

		
		
		
