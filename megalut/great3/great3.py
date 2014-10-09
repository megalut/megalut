"""
Helper class for GREAT3 that does the trivial tasks for the user.

.. todo::

 (most pressing at the top)

* make this inherit a generic run class

"""
import logging
logger = logging.getLogger(__name__)

import os
from astropy.table import Table
import numpy as np

import utils
import io
from .. import sim
from .. import utils as mutils
from .. import gsutils

class Run(utils.Branch):
    
    def __init__(self, experiment, obstype, sheartype, datadir=None, workdir=None,\
                  subfields=range(200)):
        
        utils.Branch.__init__(self,experiment, obstype, sheartype, datadir, workdir)

        self._mkdir(workdir)
        self.subfields=subfields
        logger.info("Starting new GREAT3 branch %s-%s-%s" % (experiment, obstype, sheartype))
        
    def _mkdir(self, workdir):
        """
        Creates the working directories. Outputs a warning if the directories already exist
        
         .. note:: This typically should be inherited somehow.
        """

        if workdir==None: workdir="./%s" % (self.get_branchacronym()) 
        
        mutils.mkdir(workdir)
            
        # Now must create the sub-directories:
        for subfolder in ["obs","sim","ml","pred","out"]:
            mutils.mkdir(os.path.join(workdir,subfolder))
            
        self.workdir=workdir
        
    def meas(self, imgtype, method, method_prefix="", overwrite=False):
        """
        :param imgtype: Measure on observation or sim
        :type params: `obs` or `sim`
        :param method: method to use, it must be a user-defined function. The signature of the
            function must be function(img_fname,input_cat,stampsize)
        :param overwrite: `True` all measurements and starts again, `False` (default)
            if exists, then perfect, skip it
        
        .. note:: This typically should be inherited somehow.
        """
        # Assert imgtype is known:
        assert imgtype in ["obs","sim"]

        for subfield in self.subfields:
            if imgtype=="obs":
                img_fname=self.galimgfilepath(subfield)
            elif imgtype=="sim":
                pass                                
            else: raise ValueError("Unknown image type")
            
            cat_fname=self.galfilepath(subfield,imgtype,method_prefix)
            
            # figure out if we need to overwrite (if applicable)
            if os.path.exists(cat_fname):
                if overwrite: 
                    logger.info("Analysis of %s (subfield %d) prefix %s, I'm told to overwrite..." % (imgtype,subfield,method_prefix))
                    os.remove(cat_fname)
                else: 
                    logger.info("Analysis of %s (subfield %d) prefix %s already exists, skipping..." % (imgtype,subfield,method_prefix))
                    continue
                
            input_cat = io.readgalcat(self, subfield)
            
            meas_cat=method(img_fname,input_cat,self.stampsize())
              
            # Save the meas cat
            meas_cat.write(cat_fname,format="fits") # TODO pkl or fits ? let's try it with fits
            
    def sim(self, simparams, n, overwrite=False):
        
        for subfield in self.subfields:
            
            matched_psfcat=Table.read(self.starcatpath(subfield), format="ascii")
            
            cat_fname=os.path.join(self.workdir,"sim","galaxy_catalog-%03i.fits" % subfield)
            img_fname=self.simgalimgfilepath(subfield)
            
            # figure out if we need to overwrite (if applicable)
            if os.path.exists(cat_fname) and os.path.exists(img_fname):
                if overwrite: 
                    logger.info("Sim of subfield %d, I'm told to overwrite..." % (subfield))
                    os.remove(cat_fname)
                else: 
                    logger.info("Sim of subfield %d already exists, skipping..." % (subfield))
                    continue
    
            sim_cat = sim.stampgrid.drawcat(simparams, n=n, stampsize=self.stampsize())
            
            sim_cat.write(cat_fname, format="fits") # TODO pkl or fits ? let's try it with fits
            
            ####
            psf_selection=np.random.randint(low=4, high=5, size=n*n)
            matched_psfcat = matched_psfcat[psf_selection]
            matched_psfcat.meta["stampsize"]=self.stampsize()
            
            psfimg=gsutils.loadimg(self.psfimgfilepath(subfield))
            
            sim.stampgrid.drawimg(sim_cat, psfcat=matched_psfcat, 
                    psfxname="col1", psfyname="col2",
                    psfimg=psfimg,
                    simgalimgfilepath=img_fname,
                    simtrugalimgfilepath=os.path.join(self.workdir,"sim","simtrugalimg-%03d.fits" 
                                                      % subfield),
                    simpsfimgfilepath=os.path.join(self.workdir,"sim","simtrugalimg-%03d.fits" 
                                                   % subfield)
                )
            
            
            