import os
from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from matplotlib.colors import LightSource

from pygeotools.lib import iolib, warplib, geolib
from demcoreg import coreglib 
from statslib import DoD_Stats, plot_DoD
  
def shift_dem(src_dem_fn, outdir, shift):
    """
    Shifts a Digital Elevation Model (DEM) by a specified amount in the x, y, and z directions using pygeotools library functions.
    Parameters:
    - src_dem_fn (str): The file path of the source DEM to be shifted.
    - outdir (str): The directory where the shifted DEM will be saved as a GeoTIFF file.
    - shift (tuple): The amount to shift the DEM in the x, y, and z directions.
    Returns:
    - src_out_fn (str): The file path for the shifted DEM GeoTIFF.
    """
    dx = shift[0]
    dy = shift[1]
    dz = shift[2]
    src_dem_ds = gdal.Open(src_dem_fn)
    print(f"Shifting DEM by: {dx}, {dy}, {dz}")
    src_dem_ds_align = iolib.mem_drv.CreateCopy('', src_dem_ds, 0)
    if dx is not None and dy is not None and dz is not None:
        #Apply the horizontal shift to the original dataset
        print("Applying xy shift: %0.2f, %0.2f" % (dx, dy))
        src_dem_ds_align = coreglib.apply_xy_shift(src_dem_ds_align, dx, dy, createcopy=False)
        print("Applying z shift: %0.2f" % dz)
        src_dem_ds_align = coreglib.apply_z_shift(src_dem_ds_align, dz, createcopy=False)
    
    print("Converting source DEM to array...")
    src_dem_full_align = iolib.ds_getma(src_dem_ds_align)
    src_out_fn = os.path.join(outdir, os.path.splitext(os.path.split(src_dem_fn)[-1])[0] + '_shifted.tif')
    print("Writing source DEM to: %s" % src_out_fn)
    iolib.writeGTiff(src_dem_full_align, src_out_fn, src_dem_ds_align)
    return src_out_fn
    
def match_dems(src_dem_fn, ref_dem_fn, outdir, res, extent, writeref=False):
    """
    Aligns and resamples two Digital Elevation Models (DEMs) to a common grid and resolution using pygeotools library functions.

    Parameters:
    - ref_dem_fn (str): The file path of the reference DEM.
    - src_dem_fn (str): The file path of the source DEM to be aligned with the reference.
    - outdir (str): The directory where the aligned and resampled DEMs will be saved as GeoTIFF files.

    Returns:
    - ref_out_fn (str): The file path for the processed reference DEM GeoTIFF.
    - src_out_fn (str): The file path for the processed source DEM GeoTIFF.

    """

    ref_dem_ds = gdal.Open(ref_dem_fn)
    src_dem_ds = gdal.Open(src_dem_fn)
    
    local_srs = geolib.get_ds_srs(src_dem_ds)
    print("Source DEM SRS:", geolib.get_ds_srs(src_dem_ds))
    print("Local SRS:", local_srs)

    #Resample to common grid
    ref_dem_res = np.round(float(geolib.get_res(ref_dem_ds, t_srs=local_srs, square=True)[0]), 5)
    src_dem_res = np.round(float(geolib.get_res(src_dem_ds, t_srs=local_srs, square=True)[0]),5)
    ref_extent = geolib.ds_geom_extent(ref_dem_ds, t_srs=local_srs)
    src_extent = geolib.ds_geom_extent(src_dem_ds, t_srs=local_srs)
    #Round extent to 3 decimal places
    ref_extent = [round(x, 3) for x in ref_extent]
    src_extent = [round(x, 3) for x in src_extent]
    if ref_dem_res == src_dem_res and ref_extent == src_extent:
        print("Reference and source DEMs are already aligned")
        #Close datasets
        src_dem_ds = None
        ref_dem_ds = None
        return ref_dem_fn, src_dem_fn
    else:
        print("Warping raster to common grid")
        print("Reference DEM res: %0.4f" % ref_dem_res)
        print("Source DEM res: %0.4f" % src_dem_res)
        print("Reference DEM extent: %s" % ref_extent)
        print("Source DEM extent: %s" % src_extent)
        print("Matching resolution by using mode: %s" % res)

    #Create a copy to be updated in place
    src_dem_ds_align = iolib.mem_drv.CreateCopy('', src_dem_ds, 0)
    
    #Resample to user-specified resolution
    print("Warping from Source DEM SRS to Local SRS")
    ref_dem_ds, src_dem_ds_align = warplib.memwarp_multi([ref_dem_ds, src_dem_ds_align], \
            extent= extent, res=res, t_srs=local_srs, r='cubic')
    
    res_out = float(geolib.get_res(src_dem_ds_align, square=True)[0])
    
    print("Getting source DEM array for writing new DEM to file")
    src_dem_array = iolib.ds_getma(src_dem_ds_align)

    ref_out_fn = os.path.join(outdir, os.path.splitext(os.path.split(ref_dem_fn)[-1])[0] + '_matched.tif')

    print("Matched resolution: %0.3f m" % geolib.get_res(src_dem_ds_align, square=True)[0])
    src_out_fn = os.path.join(outdir, os.path.splitext(os.path.split(src_dem_fn)[-1])[0] + '_matched.tif')
    print("Writing source DEM to: %s" % src_out_fn)
    iolib.writeGTiff(src_dem_array, src_out_fn, ref_dem_ds)
    if writeref:
        print("Getting reference DEM array for writing new DEM to file")
        ref_dem_array = iolib.ds_getma(ref_dem_ds)
        print("Writing reference DEM to: %s" % ref_out_fn)
        iolib.writeGTiff(ref_dem_array, ref_out_fn, ref_dem_ds)
        src_dem_ds_align = None
        ref_dem_ds = None
        return ref_out_fn, src_out_fn
    else:
    #Close datasets
        src_dem_ds_align = None
        ref_dem_ds = None
        return ref_out_fn, src_out_fn
          
def match_diff(src_dem_fn, ref_dem_fn, res, extent, outdir = None, align_stats_fn =None, orig_stats = False):
    """ Match resolution and extent of two DEMs before differencing them

    Args:
    src_dem_fn (str): The file path of the source DEM to be aligned with the reference.
    ref_dem_fn (str): The file path of the reference DEM.
    res (str): The resolution parameter for matching the DEMs. Options include 'min', 'max', 'mean', 'common_scale_factor'.
    extent (str): The extent parameter for matching the DEMs. Options include 'intersection', 'union', 'first', 'second'.
    outdir (str): The directory where the aligned and resampled DEMs will be saved as GeoTIFF files.
    orig_stats (bool): If True, the original statistics will be computed for the difference map.
    
    Returns:
    diff_fn (str): The file path for the difference map GeoTIFF.
    align_stats_fn (str): The file path for the alignment statistics text file.
    """
    
    #checked if outdir ends with .tif
    if outdir is None:
        #Make output directory the same as parent directory
        outdir = os.path.dirname(src_dem_fn)
        print(f"Output directory: {outdir}")
        diff_fn = os.path.splitext(src_dem_fn)[0] + '_diff.tif'    
    elif outdir.endswith('.tif'):
        diff_fn = outdir
    else:
        diff_fn = os.path.join(outdir, 'Matched_DoD.tif')

    ref_out_fn, src_out_fn = match_dems(ref_dem_fn, src_dem_fn, outdir, res, extent, writeref= True)
    
    ref_out_ds = gdal.Open(ref_out_fn)
    src_out_ds = gdal.Open(src_out_fn)
    ref_dem_ds = gdal.Open(ref_dem_fn)
    src_dem_ds = gdal.Open(src_dem_fn)
    local_srs = geolib.get_ds_srs(src_dem_ds)
    
    print("Reference: %s" % ref_dem_fn)
    print("Source: %s" % src_dem_fn)
    print("Output: %s\n" % diff_fn)
    
    if align_stats_fn is None:
        align_stats_fn = os.path.join(outdir, 'Matched_DoD_Stats.txt')
    print(f"Align stats file: {align_stats_fn}")

    DoD_Stats(ref_out_fn, src_out_fn, outdir, res, extent, log_file = align_stats_fn, out_diff_fn=diff_fn)

    #Close datasets
    src_dem_ds = None
    ref_dem_ds = None
    src_out_ds = None
    ref_out_ds = None
    return diff_fn, align_stats_fn


def main():
    
    src_fn = r""
        
if __name__ == "__main__":
    main()