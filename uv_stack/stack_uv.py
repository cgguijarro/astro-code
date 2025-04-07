# Script to stack pointings for a given list of coordinates
#
# NOTE: Works under CASA
#
# Input:
# - Visibilities names
# - Start and end field values
# - Coordinates to stack

# import libraries
from astropy.io import fits
from astropy.wcs import WCS
import os

##################################################

path_inp = '/Volumes/Data/raw/GOODS_ALMA_project/uv_pointings/'
myvisbase = 'GOODS_av_'
field_ini = 4
field_fin = 1703
output = 'stack_uv'

source = ['A2GS1', 'A2GS2', 'A2GS3']
coords = ['J2000 3h32m28.5151s -27d46m58.38383s', 'J2000 3h32m34.2815s -27d49m40.42355s', 'J2000 3h32m35.7287s -27d49m16.26597s']
ra = [53.1188128077, 53.1428397895, 53.1488695984]
dec = [-27.7828843966, -27.8278954306, -27.8211849910]

##################################################

vis_concat = []
for i in range(0, len(source), 1):
	for j in range(field_ini, field_fin + 1, 1):
		try:
			myimagebase = path_inp + myvisbase + str(j) + '_nat_dirty_005'
			img = fits.open(myimagebase + '.pb.fits', checksum = True)
			hdr = img[0].header
			scidata = img[0].data
		except IOError:
			pass
		else:
			if hdr['CRVAL1'] - abs(hdr['CDELT1'] * (hdr['NAXIS1'] / 2)) < ra[i] and ra[i] < hdr['CRVAL1'] + abs(hdr['CDELT1'] * (hdr['NAXIS1'] / 2)) and hdr['CRVAL2'] - abs(hdr['CDELT2'] * (hdr['NAXIS2'] / 2)) < dec[i] and dec[i] < hdr['CRVAL2'] + abs(hdr['CDELT2'] * (hdr['NAXIS2'] / 2)):
				w = WCS(hdr)
				xypix = w.wcs_world2pix([[ra[i], dec[i], 0, 0]], 1)
				x = xypix[0][0]
				y = xypix[0][1]
				img_val = scidata[0, 0, x-1, y-1]
				if img_val >= 0.0:
					fixvis(vis = path_inp + myvisbase + str(j) + '.ms', outputvis = myvisbase + str(j) + '_shift.ms', phasecenter = coords[i])
					ms.open(myvisbase + str(j) + '_shift.ms', nomodify = False)
					rec = ms.getdata(['data', 'weight'])
					rec['data'][:,:] = rec['data'][:,:] / img_val
					rec['weight'][:,:] = rec['weight'][:,:] * img_val**2
					ms.putdata(rec)
					ms.close()
					fixplanets(vis = myvisbase + str(j) + '_shift.ms', field = 'GOODS-S', direction = 'J2000 00h00m00 00d00m00')
					statwt(vis = myvisbase + str(j) + '_shift.ms', field = 'GOODS-S', datacolumn = 'data')
					vis_concat = [myvisbase + str(j) + '_shift.ms'] + vis_concat
					#tclean(vis = myvisbase + str(j) + '_shift.ms', imagename = myvisbase + str(j) + '_shift' + '_nat_dirty_005', imsize = 1000, cell = '0.05arcsec', interpolation = 'linear', outframe = 'BARY', pbcor = True, weighting = 'natural', interactive = False, niter = 0)
					#exportfits(imagename = myvisbase + str(j) + '_shift' + '_nat_dirty_005' + '.image', fitsimage = myvisbase + str(j) + '_shift' + '_nat_dirty_005' + '.image.fits')
				else:
					continue
			else:
				continue

concat(vis = vis_concat, concatvis = myvisbase + output + '.ms', freqtol = '500MHz', dirtol = '5arcsec', copypointing = False)
tclean(vis =  myvisbase + output + '.ms', imagename = myvisbase + output + '_nat_dirty_005', imsize = 1000, cell = '0.05arcsec', interpolation = 'linear', outframe = 'BARY', pbcor = True, weighting = 'natural', interactive = False, niter = 0)
exportfits(imagename = myvisbase + output + '_nat_dirty_005' + '.image', fitsimage = myvisbase + output + '_nat_dirty_005' + '.image.fits')
exportfits(imagename = myvisbase + output + '_nat_dirty_005' + '.image.pbcor', fitsimage = myvisbase + output + '_nat_dirty_005' + '.image.pbcor.fits')
os.system('rm -rf *shift*')
