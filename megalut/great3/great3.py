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
from .. import learn

import shutil

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
        self.workdir=workdir
        
        # Now must create the sub-directories:
        for subfolder in ["obs","sim","ml","pred","out"]:
            mutils.mkdir(self._get_path(subfolder))

        
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
                input_cat = io.readgalcat(self, subfield)
            elif imgtype=="sim":
                img_fname=self.simgalimgfilepath(subfield)
                input_cat = self._get_path("sim","galaxy_catalog-%03i.fits" % subfield)
                input_cat =  Table.read(input_cat)
            else: raise ValueError("Unknown image type")
            
            cat_fname=self.galfilepath(subfield,imgtype,method_prefix)  
            
            # figure out if we need to overwrite (if applicable)
            if os.path.exists(cat_fname):
                if overwrite: 
                    logger.info("Analysis of %s (subfield %d) prefix %s, I'm told to overwrite..."
                                 % (imgtype,subfield,method_prefix))
                    os.remove(cat_fname)
                else: 
                    logger.info("Analysis of %s (subfield %d) prefix %s already exists, skipping..."
                                 % (imgtype,subfield,method_prefix))
                    continue
            
            meas_cat=method(img_fname,input_cat,self.stampsize(),prefix=method_prefix)
              
            # Save the meas cat
            meas_cat.write(cat_fname,format="fits") 
            # TODO: pkl or fits ? let's try it with fits
            
    def sim(self, simparams, n, overwrite=False):
        
        for subfield in self.subfields:
            
            matched_psfcat=Table.read(self.starcatpath(subfield), format="ascii")
            
            cat_fname=self._get_path("sim","galaxy_catalog-%03i.fits" % subfield)
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
            
            sim_cat.write(cat_fname, format="fits") 
            # TODO: pkl or fits ? let's try it with fits
            
            ####
            psf_selection=np.random.randint(low=4, high=5, size=n*n) 
            # TODO: make this random ?
            matched_psfcat = matched_psfcat[psf_selection]
            matched_psfcat.meta["stampsize"]=self.stampsize()
            
            psfimg=gsutils.loadimg(self.psfimgfilepath(subfield))
            
            sim.stampgrid.drawimg(sim_cat, psfcat=matched_psfcat, 
                    psfxname="col1", psfyname="col2",
                    psfimg=psfimg,
                    simgalimgfilepath=img_fname,
                    simtrugalimgfilepath=self._get_path("sim","simtrugalimg-%03d.fits" 
                                                      % subfield),
                    simpsfimgfilepath=self._get_path("sim","simtrugalimg-%03d.fits" 
                                                   % subfield)
                )
            
    def learn(self, learnparams, mlparams, method_prefix="", overwrite=False):
        # TODO: how to merge different measurements together ?
        for subfield in self.subfields:            
            ml = learn.ML(learnparams, mlparams,workbasedir=os.path.join(self.workdir
                                                                         ,"ml","%03d" % subfield))
                        
            ml_files=ml.get_fnames()
            exists=True
            for fname in ml_files[1]:
                if not os.path.exists(os.path.join(ml_files[0],fname)) :
                    exists=False

            if exists and not overwrite:
                logger.info("Learn of subfield %d already exists, skipping..." % (subfield))
                continue
            elif overwrite and exists:
                logger.info("Learn of subfield %d, I'm told to overwrite..." % (subfield))
                shutil.rmtree(ml_files[0])

            input_cat=self.galfilepath(subfield,"sim",method_prefix)
            input_cat=Table.read(input_cat)
            
            # Important: we don't want to train on badly measured data!
            input_cat = input_cat[input_cat[method_prefix+"flag"] == 0] 

            ml.train(input_cat)
            
            # export the ML object:
            mutils.writepickle(ml, os.path.join(ml_files[0],"ML.pkl"))
            
    def predict(self,method_prefix,overwrite=False):
        for subfield in self.subfields:    
            for root, dirs, files in os.walk(os.path.join(self.workdir,"ml","%03d" % subfield)):
                if not "ML.pkl" in files: continue
                ml_name = root.split("/")[-1]
                cat_fname=self._get_path("pred","%s-%03d.fits" % (ml_name,subfield))
                
                if os.path.exists(cat_fname) and overwrite:
                    logger.info("Pred of subfield %d, I'm told to overwrite..." % (subfield))
                    os.remove(cat_fname)
                elif os.path.exists(cat_fname):
                    logger.info("Pred of subfield %d already exists, skipping..." % (subfield))
                    continue
                
                logger.info("Using %s to predict on subfield %03d" % (ml_name,subfield))

                ml=mutils.readpickle(os.path.join(root,"ML.pkl"))
                
                input_cat=self.galfilepath(subfield,"obs",method_prefix)
                input_cat=Table.read(input_cat)
                
                # We predict everything, we will remove flags later
                predicted=ml.predict(input_cat)
                
                failed=predicted[method_prefix+"flag"]>0
                count_failed=0
                for p in predicted[failed]:
                    # TODO: Better and faster way to do this ?
                    p["pre_g1"]=20.
                    p["pre_g2"]=20.
                    count_failed+=1
                    
                logger.info("Predicted on %d objects, %d failed" % (len(input_cat),count_failed))
                
                predicted.write(cat_fname,format="fits")
                
    def writeout(self, ml_name):
        for subfield in self.subfields:  
            input_cat = Table.read(self._get_path("pred","%s-%03d.fits" % (ml_name,subfield)))
            
            input_cat=input_cat["ID","pre_g1","pre_g2"]
            input_cat.write(self._get_path("out","%03d.dat" % subfield),format="ascii.commented_header")
            logger.info("Wrote shear cat for subfield %03d" % subfield)
            
    def _get_path(self,*args):
        return os.path.join(self.workdir,"/".join(args))
            