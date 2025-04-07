# CHECK BEFORE RUN
from astropy.io import fits
from photutils import CircularAperture, CircularAnnulus, aperture_photometry
from astropy.wcs import WCS
import os
import subprocess
import numpy as np
from math import fabs, log10

##################################################

PARAMETERS = '/Users/Documents/params.txt' # list of input parameters: ra, dec, aperture radius, inner annulus radius, outer annulus radius
IMAGE = '/Users/Documents/images.txt' # list of input images paths
OUTPUT = '/Users/Documents/output.txt' # name of the output photometry file
pix_scl = 0.6 # pixel scale

##################################################

# reading input file PARAMETERS

datafile_param = open(PARAMETERS)
ra = []
dec = []
radius = []
ring_in = []
ring_out = []

for key in datafile_param:
  key = key.replace('\n','')
  key = key.replace('\t',' ')
  for kk in np.arange(5):
    key = key.replace('  ',' ')
  data = key.split(' ')
  ra.append(float(data[0]))
  dec.append(float(data[1]))
  radius.append(float(data[2]))
  ring_in.append(float(data[3]))
  ring_out.append(float(data[4]))

# reading list of input images paths

datafile_img = open(IMAGE)
imgname = []

for key in datafile_img:
  key = key.replace('\n','')
  key = key.replace('\t',' ')
  for kk in np.arange(5):
    key = key.replace('  ',' ')
  data = key.split(' ')
  imgname.append(str(data[0]))

# generating output file

outfile = open(OUTPUT, "w")
outfile.write('#mag_ab'  + ' ' + 'err_mag_ab' + ' ' + 'fnu' + ' ' + 'err_fnu' + '\n')
count = 1

# looping over the coordinates and images

for i in range(len(ra)):
  outfile.write('#Aperture #' + str(count) + '\n')

  for j in range(len(imgname)):
    
    # opening the fits

    img = fits.open(imgname[j], checksum = True)
    hdr = img[0].header # opening the header - CHANGE TO DEAL WITH IMAGE EXTENSION
    scidata = img[0].data # opening the data - CHANGE TO DEAL WITH IMAGE EXTENSION

    # position to perform the apperture photometry

    w = WCS(hdr)
    x, y = w.wcs_world2pix(ra[i], dec[i], 1) # transforming the WCS coordinates to pixel coordinates
    positions = [(x.tolist(),y.tolist())]

    # performing the aperture photometry
    
    apertures = CircularAperture(positions, radius[i]) # defining a circular aperture
    rawflux_table = aperture_photometry(scidata, apertures) # aperture photometry in the circular aperture
    rawflux = rawflux_table['aperture_sum'][0]
    flux = rawflux

    # calculating the flux uncertainty

    # calling extrenal R script to create random numbers in a XY plane
    command = 'Rscript --vanilla /Users/cgguijarro/Documents/code/classes/photometry/rand_xy_photclass.R '
    size_pix = 60 / pix_scl
    minimum_x = positions[0][0] - size_pix/2
    maximum_x = positions[0][0] + size_pix/2
    minimum_y = positions[0][1] - size_pix/2
    maximum_y = positions[0][1] + size_pix/2
    args = str(minimum_x) + ' ' + str(maximum_x) + ' ' + str(minimum_y) + ' ' + str(maximum_y) + ' ' + str(radius[i]) # input arguments for R script
    cmd = command + args # building subprocess command
    subprocess.call(cmd, shell = True) # running R script

    # reading output file
    datafile_rand_xy = open('rand_xy.txt')
    x = []
    y = []

    for key in datafile_rand_xy:
      key = key.replace('\n','')
      key = key.replace('\t',' ')
      for kk in np.arange(5):
        key = key.replace('  ',' ')
      data = key.split(' ')
      x.append(float(data[0]))
      y.append(float(data[1]))

    # random positions generated to perform the aperture photometry
    positions_randap = []
    for k in range(len(x)):
      positions_randap.append((x[k],y[k]))

    # performing the aperture photometry
    flux_randap = []
    for k in range(len(positions_randap)):
      apertures_randap = CircularAperture(positions_randap[k], radius[i])
      rawflux_table_randap = aperture_photometry(scidata, apertures_randap)
      rawflux_randap = rawflux_table_randap['aperture_sum'][0]
      flux_randap.append(rawflux_randap)

    # generating ouput file
    outfile_randap = open('randapflux.txt', "w")
    for k in range(len(flux_randap)):
      dataline = str(flux_randap[k])
      outfile_randap.write(dataline  + '\n')
    outfile_randap.close()

    # calling extrenal R script to calculate the sigma in the random empty apertures distribution
    command = 'Rscript --vanilla /Users/cgguijarro/Documents/code/classes/photometry/apphot_err_photclass.R '
    args = 'randapflux.txt' # input arguments for R script
    cmd = command + args # building subprocess command
    skybkg = subprocess.check_output(cmd, shell = True) # running R script and storing result
    skybkg = skybkg.split()
    skymode = float(skybkg[0])
    skysigma = float(skybkg[1])
    err_flux = skysigma # flux error is the sigma in the random empty apertures distribution

    # calculating sky background

    # method 1: empty annulus apertures
    annulus_apertures = CircularAnnulus(positions, r_in=ring_in[i], r_out=ring_out[i]) # defining annulus aperture
    bkgflux_table = aperture_photometry(scidata, annulus_apertures) # aperture photometry in the annulus aperture to measure the local background
    bkg_mean = bkgflux_table['aperture_sum'][0] / annulus_apertures.area() # local background per unit area (mean)
    bkg_sum_1 = bkg_mean * apertures.area() # background in the measured area

    # method 2: image sky distribution
    bkg_sum_2 = skymode # background in the measured area

    #flux = rawflux - bkg_sum_1 # subtracting the background - CHANGE TO DEAL WITH BKG SUBTRACTION
    flux = rawflux - bkg_sum_2 # subtracting the background - CHANGE TO DEAL WITH BKG SUBTRACTION

    print 'rawflux = ' + str(rawflux)
    print 'bkgflux_1 = ' + str(bkg_sum_1)
    print 'bkgflux_2 = ' + str(bkg_sum_2)
    print 'flux = ' + str(flux)
    print 'err_flux = ' + str(err_flux)

    # converting to physical units

    mag_ab = -2.5 * log10(flux) + 30 # CHANGE TO DEAL WITH ZERO POINT
    err_mag_ab = fabs(2.5 * log10(1 + err_flux/flux))
    fnu = 10**((mag_ab + 48.6)/-2.5)
    err_fnu = fabs((10**(err_mag_ab/2.5) - 1) * fnu)

    # writting in the ouput file

    dataline = str(mag_ab) + ' ' + str(err_mag_ab) + ' ' + str(fnu) + ' ' + str(err_fnu)
    outfile.write(dataline  + '\n')
    
    # removing temp files

    os.system('rm rand_xy.txt randapflux.txt')

  count = count + 1

outfile.close()
