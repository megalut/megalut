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
	
	In future, this class can in principle hold more complex WCS-like coordinate systems.
	"""

	def __init__(self, filepath, xname="x", yname="y", stampsize=None, imgname=None, workdir=None):
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
		:param imgname: a name for the image. By default (None) the filename will be used, but sometimes
			it might be helpful to specify different names.
		:type imgname: string
		:param workdir: path to a working directory for this image
		:type imgname: string	
		"""
		
		self.filepath = filepath
		self.xname = xname
		self.yname = yname
		self.stampsize = stampsize

		
		if imgname is None:
			self.imgname = os.path.splitext(os.path.basename(filepath))[0]
		else:
			self.imgname = imgname
		
		self.workdir = workdir # To be developed...
				

	def __str__(self):
		return self.imgname

	def load(self):
		return image.loadimage(self.filepath)
