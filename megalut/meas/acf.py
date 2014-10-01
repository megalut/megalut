import numpy as np
from datetime import datetime
from .. import utils
import logging
import astropy.table

logger = logging.getLogger(__name__)

###################################################################################################

def run(imgfilepath, gal_catalog, stampsize=32, method=None, acf_weight="gaussian", prefix="mes_acf", show=False):
    """
    Shape measurement with AutoCorrelation Function
    http://adsabs.harvard.edu/abs/1997A%26A...317..303V
    Runs acf on the image
    
    :param imgfilepath: The filepath of the image
    :gal_catalog: The catalog of the galaxy with an entry for : id, x, y
    :stampsize: the stamp size to use for the measurement. Default: 32
    :method: which method to use ? Choice : "AdaptiveMoments", "EllipticityGradients",
        "QuadrupoleMoments". Default: AdaptiveMoments
    :acf_weight: Weight for the convolution ie, Data*=weight before the convolution.
        default: "gaussian" or None
    :prefix: for the output catalog, what is the prefix of the variable?, Default "mes_acf"
    :show: if True, then prints an image of the data and the ACF.
    """
    if method=="None" or not method in ["AdaptiveMoments",
                                        "EllipticityGradients",
                                        "QuadrupoleMoments"]:
        method="AdaptiveMoments"
        
    
    logger.info("acf run on %s with method %s starting now" % (imgfilepath,method))
    evList = 'acf=%s()' % method
    acf=None # This line does actually nothing, it's do remove the errors in Eclipse...
    # here we create the acf instance according to the method chosen
    exec(evList)
    
    starttime = datetime.now()
    
    rows=[]  
    
    logger.info('Running acf measurements on %s. This could take a while...' % (imgfilepath))
    whole_image = utils.fromfits(imgfilepath)
    for gal in gal_catalog:
        x,y=gal["x"], gal["y"]
        # By MegaLUT's definition, a pixel is centered at 0.5,0.5
        dd=+.0#.5
        xmin=round(int(x-dd-stampsize/2))
        xmax=round(int(x-dd+stampsize/2))
        ymin=round(int(y-dd-stampsize/2))
        ymax=round(int(y-dd+stampsize/2))
        img=whole_image[xmin:xmax,ymin:ymax]
        
        acf.set_data(img.copy())
        
        acf.compute_acf(weights=acf_weight)
        acf.measure()
        if method == 'AdaptiveMoments':
            output=acf.get_measurements(prefix=prefix)
        else:
            g1,g2=acf.get_shear()
            output={prefix+"_g1":g1,prefix+"_g2":g2}
            
        output['id']=gal["id"]
        rows.append(output)
        
        if show: acf.show_acf()
        
        acf.clear()

    catalog = astropy.table.Table(rows=rows)
    
    return catalog
    

# END OF RUN METHOD
###################################################################################################
class _ACF(object):
    '''
    Class which manages the two images (the observation and its ACF). 
    For now only one method is available to compute the ACF from the data. (See compute_acf() )
    This class is not to be used directly as it is inherited by ACF measurements methods!
    '''
    
    def __init__(self, image=None, show=True):
        ''' Polymorphic constructor takes 3 arguments (one is mandatory):
            
            :param image: (mandatory) Either the path to the image or a numpy array containing the data.
            :param show: (optional) allows the system to show images.
        '''
        if not image==None:
            if type(image)==str: self.data = utils.fromfits(image)
            else: self.data = np.asarray(image)
        else: 
            self.data=None
        self.show = show
        self.acf = None
        self.g1 = None
        self.g2 = None
        self.a = None
        self.b = None
        self.phi=None
                
    def save_acf(self, fname, region=None):
        ''' Saves the ACF to a specified filename. The region argument is a list/numpy vector of [rx, ry] 
            which selects the region (rectangular) of ACF to be saved around the centre. 

            :raise RuntimeError: Raise an exception if the ACF is not computed 
        '''
        if self.acf == None: 
            raise RuntimeError('cannot save %s, acf not computed!' % fname)
        else: 
            if region == None:
                x0 = y0 = 0
                xf, yf = np.shape(self.acf)
                dx = xf
                dy=yf
            else:
                cx, cy = np.shape(self.acf)
                cx /= 2
                cy /= 2
                dx, dy = region
                x0 = cx - dx/2
                y0 = cy - dy/2
                xf = cx + dx/2
                yf = cy + dy/2
            
            acf = self.acf[x0:xf,y0:yf]
            acf[dx/2,dx/2]=0.
            acf[dx/2,dx/2]=np.amax(acf)
            utils.tofits(acf, fname)
        logger.info('Wrote acf to %s' % fname)
        
    def compute_acf(self,weights=None, clip=False, **kwargs):
        ''' Computes the acf from the data using FFT by the equation
            acf = F^-1 ( F(weights.data).(F(weights.data))* )
            where F is the Fourier transform, F^-1 its inverse and * the complex conjugate, the operator . denotes multiplication
            
            This function takes two optional arguments:
            :param weigthts: can be None (no weighting of the data), "gaussian" (2D gaussian function 
            aligned to a first guess of the shape by SExtractor) or "tophat" same as gaussian, but once
            the shape is estimated, the Gaussian is replaced by a top-hat.
            :param clip: clip the data to [0, data_max]
        '''
        from numpy.fft import fft2, ifft2, fftshift   
        
        if weights == 'gaussian' or weights == 'acfgaussian' or weights == 'tophat':
            starttime = datetime.now()    
            if ('x_obj' in kwargs and 'y_obj' in kwargs and 'radius' in kwargs and 'a' in kwargs and 'b' in kwargs and 'theta' in kwargs):
                weights_params = [kwargs['x_obj'], kwargs['y_obj'], kwargs['radius'], kwargs['a'], kwargs['b'],kwargs['theta']]
                weights_params = np.array([weights_params])
            elif 'weights_params' in kwargs:
                weights_params=kwargs['weights_params']
            else:
                weights_params = None
            logger.info('Weights params (for weight type: %s) %s' % (weights, weights_params))
            weights_map = self._BuildWeightMap(self.data, weights_type = weights, weights_params=weights_params)
            data=self.data*weights_map
            endtime = datetime.now()
            logger.info('Time needed to build weight map [s]: %s' % (str(endtime - starttime)))
        else:
            data = self.data
            weights_params = None
            
        data = data+0.j
        starttime = datetime.now()    
        dataFT = fft2(data)
        self.acf = fftshift(ifft2(dataFT * np.conjugate(dataFT))).real
        
        weights_map = self._BuildWeightMap(self.acf, weights_type = weights, weights_params=weights_params)
        self.acf=self.acf*weights_map
        if clip:
            self.acf = np.clip(self.acf, 0., np.amax(self.acf))
        
        self.acf=self.acf.transpose().copy()
        endtime = datetime.now()
        logger.info('Needed to compute acf [s]:%s', (str(endtime - starttime)))
        
    def show_acf(self, fname=None, title=None, zoom = 1):
        ''' Shows the image of the data and the ACF with the estimation of the ellipticity if already computed.
        
        :param fname: (optional) if a filename is specified, the graph is saved.
        :param title: (optional) Adds a title to the graph
        :param zoom: (optional) changes the size of the ellipse drawn on top of the ACF
        
        :raise RuntimeError: Raise an exception if the ACF is not computed 
        requires:: Pylab
        '''
        
        if self.acf == None: 
            raise RuntimeError('cannot save %s, ACF not computed!' % fname)
        
        import pylab as plt

        plt.figure(figsize=(24, 12))
        
        plt.subplot(121)
        plt.imshow(self.data, origin='lower', interpolation='nearest',cmap=plt.cm.gray, vmin = np.amin(self.data)*0.999, vmax = np.amax(self.data)*1.001)
        plt.title('Data')
        
        ax=plt.subplot(122)
        plt.imshow(self.acf,origin='lower', interpolation='nearest', vmin = np.amin(self.acf)*0.999, vmax = np.amax(self.acf)*1.001)
        if not (self.a == None and self.b == None and self.phi==None): 
            from matplotlib.patches import Ellipse
            cx, cy = np.shape(self.acf)
            cx /= 2
            cy /= 2
            e=Ellipse(xy=[cx, cy], width=self.a*zoom, height=self.b*zoom, angle=self.phi/np.pi*180., facecolor='None',lw=2)
            ax.add_artist(e)
        plt.title('acf')
        
        if not fname==None: plt.savefig(fname)
        plt.show()
        
    def clear(self):
        ''' Resets all the ellipticity parameters to None '''
        logger.info("Resetting all ellipticities measurements.")
        self.acf=None
        self.data=None
        self.g1 = None
        self.g2 = None
        self.a = None
        self.b = None
        self.phi = None

    def set_data(self, a):
        ''' SET method for the data 
        :param a: numpy array of the data
        '''
        self.data=a
    
    def set_acf(self, a):
        ''' SET method for the acf 
        :param a: numpy array of the acf
        '''
        self.acf=a
        
    def get_acf(self):
        ''' GET method for the acf '''
        return self.acf
        
    def get_shear(self):
        ''' Returns g1 and g2 estimates 
            :raise RuntimeError: if g1,g2 are not yet computed
        '''
        if self.g1 == None or self.g2== None: raise RuntimeError('g1/g2 not computed yet!')
        else: return self.g1, self.g2
        
    def find_obj_sex(self, data):
        #TODO: This is an old way of doing things... use sextractor wrapper!
        ''' Runs Sextractor on the specifed data.
        :param data: numpy array with data
        :return: Catalogue as generated by SExtractor and according the parameters below
        :requires: pysex
        :requires: SExtractor 
        '''

        import pysex
        params = ['XWIN_IMAGE', 'YWIN_IMAGE','FLUX_RADIUS','AWIN_IMAGE','BWIN_IMAGE','THETAWIN_IMAGE']
        config = {'DETECT_MINAREA':5, 'DETECT_THRESH':2., 'VERBOSE_TYPE':'QUIET'}
        cat = pysex.run(data, params=params, conf_args=config)

        return np.array(zip(cat[params[0]], cat[params[1]], cat[params[2]], cat[params[3]], cat[params[4]], cat[params[5]]))
    
    def find_obj_gs(self, data):
        import galsim

        gps=galsim.ImageD(data.copy())       
        res = galsim.hsm.FindAdaptiveMom(gps)

        return np.array([[res.moments_centroid.x + 1.0,res.moments_centroid.y + 1.0, res.moments_sigma, 1, 1, 0]])
    
    def _BuildWeightMap(self, data, weights_type,weights_params):
        ''' Creates the weights map for a given image according to a given weight type '''

        if weights_type==None:
            return np.ones_like(data)
        
        def gaussian(width_x, width_y, rotation):
            """Returns a gaussian function with the given parameters"""
            width_x = float(width_x)
            width_y = float(width_y)
 
            rotation = np.deg2rad(rotation)
 
            def rotgauss(x,y):
                xp = x * np.cos(rotation) - y * np.sin(rotation)
                yp = x * np.sin(rotation) + y * np.cos(rotation)
                g = np.exp(-((xp/width_x)**2+(yp/width_y)**2)/2.)
                return g
            return rotgauss
        
        def _create(weights,xf,yf,x_obj,y_obj, radius, ib, ia, iphi, weights_type):
            r = np.shape(self.data)[0]/2
           
            #if weights_type == 'acfgaussian':
            #   radius = self.save_radius
            #else:self.save_radius=radius
            #print weights_type, xf,yf,x_obj,y_obj, radius
            
            rx0 = int(x_obj)-r
            rxf = int(x_obj)+r
            ry0 = int(y_obj)-r
            ryf = int(y_obj)+r

            if rx0 < 0 : rx0=0
            if rxf >=xf: rxf=xf-1
            if ry0 < 0 : ry0=0
            if ryf >=xf: ryf=yf-1
            
            x = np.linspace(rx0,rxf-1,rxf-rx0)-x_obj
            y = np.linspace(ry0,ryf-1,ryf-ry0)-y_obj
            x,y = np.meshgrid(-x, y)

            if radius < 1e-9: 
                logger.warning('object at %3.4f,%3.4f could not be treated. Ignoring...' % (x_obj, y_obj))
            else:
                if weights_type == 'gaussian':
                    aa = gaussian(radius, ia/ib*radius, iphi)(x,y)
                else:
                    raise NotImplemented("Unknown weight type")
                weights[ry0:ryf,rx0:rxf] += aa

            return 1
            
        if weights_params == None: 
            cat = self.find_obj_gs(data)
            if np.shape(cat)[0]>1: logger.error("Got more than 1 match")
            elif np.shape(cat)[0]==0: logger.error("No match")
        else: cat = weights_params
        xf,yf=np.shape(data)

        x = np.linspace(0,xf-1,xf)#-x_obj
        y = np.linspace(0,yf-1,yf)#-y_obj
        x,y = np.meshgrid(x, y)
        
        weights = np.zeros_like(data)
        #np.asarray([_create(weights, xf,yf,x_obj,y_obj, radius, ia, ib, iphi, weights_type) for x_obj, y_obj, radius, ia, ib, iphi in cat])
        if weights_type == 'gaussian':
            np.asarray([_create(weights, xf,yf,x_obj,y_obj, 2.5*radius, 1., 1., 0., weights_type) for x_obj, y_obj, radius, ia, ib, iphi in cat])

        # Normalisation to 1
        weights /= np.sum(weights)

        return weights
# END OF CLASS
###################################################################################################
class QuadrupoleMoments(_ACF):
    ''' ACF measurement class
        Uses quadrupole moments to measure the ellipticity
        Example usage::
            >>> img = QuadrupoleMoments(image_filename)
            >>> img.compute_acf(clip=True, weights='gaussian')
            >>> img.measure(region=region)
            >>> g1os, g2os = img.Get_Shear()
    '''
    def __init__(self,image=None, show=True): 
        _ACF.__init__(self, image, show)
        logger.info('*** Using %s ***' % (self.__class__.__name__))
    
    def measure(self, region=None):
        if self.acf == None:
            raise RuntimeError('Error: cannot measure ellipticity, acf not computed!')
        
        cx, cy = np.shape(self.acf)
        cx /= 2
        cy /= 2
        
        if region == None:
            x0 = y0 = 0
            xf, yf = np.shape(self.acf)
        else:
            dx, dy = region
            x0 = cx - dx/2
            y0 = cy - dy/2
            xf = cx + dx/2
            yf = cy + dy/2
            
        acf = self.acf[x0:xf,y0:yf]
        self.acf = acf
        
        
        den = np.sum(acf)
        x = np.arange(x0,xf)-cx
        y = np.arange(y0,yf)-cy
        x,y = np.meshgrid(x, y)
        
        Ixx = np.sum(acf * x*x) / den
        Iyy = np.sum(acf * y*y) / den
        Ixy = np.sum(acf * x*y) / den
        
        xi = (Ixx - Iyy + 2.j*Ixy) / (Ixx+Iyy) / 2
        self.g1 = xi.real
        self.g2 = xi.imag
        '''
        elli = abs(xi)
        q = (1.+elli)/(1.-elli)
        self.a = min(np.abs(Ixx),np.abs(Iyy))
        self.b = self.a * q
        self.phi = np.arctan2(2.*Ixy,(Ixx - Iyy))/2.+np.pi/2.
        '''
# END OF CLASS
###################################################################################################

class EllipticityGradients(_ACF):
    ''' ACF measurement class
        Uses quadrupole moments to measure the ellipticity
        Example usage:
            img = QuadrupoleMoments(image_filename, verbose=False)
            img.compute_acf(clip=True, weights='gaussian')
            img.measure(region=region)
            g1os, g2os = img.Get_Shear()
    '''
    def __init__(self, image=None, show=True): 
        _ACF.__init__(self, image, show)
        logger.info('*** Using %s ***' % (self.__class__.__name__))
    
    def measure(self):
        if self.acf == None:
            raise RuntimeError('Error: cannot measure ellipticity, acf not computed!')
        
        dy,dx = np.gradient(self.acf)
        delta = 0
        
        self.g1= -np.mean(dx*dx - dy*dy)/np.mean(dx*dx + dy*dy+delta)/2.
        self.g2= -np.mean(dx*dy)/np.mean(dx*dx + dy*dy+delta)#*2.
        
        
# END OF CLASS
###################################################################################################
class AdaptiveMoments(_ACF):
    ''' ACF measurement class
        Uses quadrupole moments to measure the ellipticity
        Example usage:
            img = QuadrupoleMoments(image_filename, verbose=False)
            img.compute_acf(clip=True, weights='gaussian')
            img.measure(region=region)
            g1os, g2os = img.Get_Shear()
    '''
    
    
    
    def __init__(self, image=None, show=True): 
        _ACF.__init__(self, image, show)
        logger.info('*** Using %s ***' % (self.__class__.__name__))
    
    def measure(self):
        if self.acf == None:
            raise RuntimeError('Error: cannot measure ellipticity, acf not computed!')
        
        import galsim
        stampsize = np.shape(self.acf)
        bounds = galsim.BoundsI(1 , stampsize[0], 1, stampsize[1]) # Default Galsim convention, index starts at 1.
        gps=galsim.ImageD(self.acf)#, bounds=bounds)
        res = galsim.hsm.FindAdaptiveMom(gps)
        
        self.res = res
        self.g1=res.observed_shape.g1
        self.g2=res.observed_shape.g2
        
    def get_measurements(self, prefix="acf_"):
        gal={}
        gal[prefix+"_flux"] = self.res.moments_amp
        gal[prefix+"_x"] = self.res.moments_centroid.x + 1.0 # Not fully clear why this +1 is needed. Maybe it's the setOrigin(0, 0).
        gal[prefix+"_y"] = self.res.moments_centroid.y + 1.0 # But I would expect that GalSim would internally keep track of these origin issues.
        gal[prefix+"_g1"] = self.res.observed_shape.g1
        gal[prefix+"_g2"] = self.res.observed_shape.g2
        gal[prefix+"_sigma"] = self.res.moments_sigma
        gal[prefix+"_rho4"] = self.res.moments_rho4
        
        return gal
