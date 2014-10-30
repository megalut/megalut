from utils import Branch
from .. import tools

import astropy.io.ascii as ascii
from astropy.table import Table, Column
import galsim

import numpy as np
import os
import logging
logger = logging.getLogger(__name__)


def generalise_catalogs(catalog):
    """
    Removes metadata to merge catalogs from different tiles without astropy complaining
    """
    catalog.meta['FILEPATH'] = catalog.meta['FILEPATH'][:-10]+"-**x**.fits"
    del catalog.meta['XT']
    del catalog.meta['YT']
    return catalog

def separate(experiment, obstype, sheartype, datadir, workdir,subfields):
    """
    Top-level function that will take the stamps of the tiles and put them into one single image
    """
    branch=Branch(experiment, obstype, sheartype, datadir, workdir)
    workdir=os.path.join(workdir,"/".join(branch.branchtuple()))
    tools.dirs.mkdir(workdir)
    
    for subfield in subfields:
        _separate("galaxy",subfield,branch,workdir)
        _separate("star",subfield,branch,workdir)

def _separate(imgtype,subfield,branch,workdir):
    """
    Does the heavy lifting for :func separate:
    """
    logger.info("Starting %s image separation on %s, subfield %03d" % (imgtype, branch.get_branchacronym(), subfield))
    if imgtype=="galaxy":
        fname=branch.galcatfilepath(subfield)
        colnames=["x","y","ID","x_tile_index","y_tile_index","tile_x_pos_deg",
                  "tile_y_pos_deg","x_field_true_deg","y_field_true_deg"]
        imgfname=branch.galimgfilepath(subfield)
    elif imgtype=="star":
        fname=branch.starcatpath(subfield)
        colnames=["x","y","x_tile_index","y_tile_index","tile_x_pos_deg",
                  "tile_y_pos_deg","x_field_true_deg","y_field_true_deg"]
        imgfname=branch.psfimgfilepath(subfield)
    
    catalog=ascii.read(fname)
        
    for ii, colname in enumerate(colnames):
        catalog["col%d" % (ii+1)].name = colname
        
    image = tools.image.loadimg(imgfname)
    
    for xt in range(branch.ntiles()):
        catalog_=catalog[catalog["x_tile_index"]==xt]
        
        for yt in range(branch.ntiles()):
            logger.debug("Starting tile %02dx%02d" % (xt,yt))
            catalog_tile=catalog_[catalog_["y_tile_index"]==yt]
            
            n = np.ceil(np.sqrt(np.size(catalog_tile)))

            # Creates a new gal_image
            new_image=np.zeros([branch.stampsize()*n,branch.stampsize()*n])
            new_image=galsim.ImageF(new_image)
            
            nx = 0
            ny = 0
            xs=[]
            ys=[]
            ids=[]
            posx=[]
            posy=[]
            for ii, (x,y) in enumerate(zip(catalog_tile["x"],catalog_tile["y"])):
                stamp = tools.image.getstamp(x+1, y+1, image, branch.stampsize())
                if stamp[0] is None:
                    logger.warning("Could not load stamp from %s, x=%d, y=%d, xt=%d, yt=%d" % 
                                   (imgfname,x,y,xt,yt))
                    continue
                stamp = stamp[0].array
                new_image.array[nx*branch.stampsize():(nx+1.)*branch.stampsize(),
                                ny*branch.stampsize():(ny+1.)*branch.stampsize()]=stamp
                # This is strange, but seems to work
                xs.append((ny+0.5)*branch.stampsize()-1)
                ys.append((nx+0.5)*branch.stampsize()-1)
                if imgtype=="galaxy": ids.append(catalog_tile["ID"][ii])
                posx.append(catalog_tile["tile_x_pos_deg"][ii])
                posy.append(catalog_tile["tile_y_pos_deg"][ii])
                
                nx+=1
                if nx >= n:
                    nx=0
                    ny+=1
            
            if imgtype=="galaxy":
                data = Table([xs, ys, ids, posx, posy], names=['x', 'y', 'ID', "tile_x_pos_deg", "tile_y_pos_deg"])
                note=""
            elif imgtype=="star":
                data = Table([xs, ys, posx, posy], names=['x', 'y', "tile_x_pos_deg", "tile_y_pos_deg"])
                note="starfield_"
                
            #TODO: add multiepoch handling 
            data.write(os.path.join(workdir, "%s_catalog-%03d-%02d-%02d.txt" % 
                                    (imgtype,subfield, xt, yt)),format="ascii.commented_header")
            
            galsim.fits.write(new_image, "%simage-%03d-0-%02d-%02d.fits" % (note,subfield, xt, yt), 
                              dir=workdir)
