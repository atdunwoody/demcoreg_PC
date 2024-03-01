import sys
import os
import argparse
import subprocess
import json
from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from matplotlib.colors import LightSource

import geolib
import iolib
import malib
import warplib
import utilities
import coreglib


def DoD_Stats(src_dem_fn, ref_dem_fn, outdir, res, extent, match = True, log_file = None, out_diff_fn = None):

    if type(ref_dem_fn) is list:
        ref_dem_fn = ref_dem_fn[0]
    if type(src_dem_fn) is list:
        src_dem_fn = src_dem_fn[0]
    if out_diff_fn is None:
        out_diff_fn = outdir + os.path.basename(os.path.splitext(src_dem_fn)[0]) + '_diff.tif'
    if log_file is None:  
        print("No log file specified, creating file") 
        log_file = outdir + os.path.basename(os.path.splitext(src_dem_fn)[0]) + '_stats.txt'
    print(f"Log file: {log_file}")
    if match:
        ref_out_fn, src_out_fn = match_dems(ref_dem_fn, src_dem_fn, outdir, res, extent)
        print("Computing DoD statistics for common intersection")
    ref_dem_clip_ds = gdal.Open(ref_out_fn)
    src_dem_clip_ds = gdal.Open(src_out_fn)
    #Get resolution of src and ref DEMs
    ref_res = geolib.get_res(ref_dem_clip_ds, square=True)[0]
    src_res = geolib.get_res(src_dem_clip_ds, square=True)[0]
    # check if the resolution of the two DEMs are the same to four decimals
    if round(ref_res, 4) != round(src_res, 4):
        print("WARNIUNG: Resolution of source, reference DEMs: %0.4f, %0.4f" % (src_res, ref_res))
    print("Opening masked reference DEM array: %s" % ref_out_fn)
    ref_dem_match = iolib.ds_getma(ref_dem_clip_ds)
    print("Opening masked source DEM array: %s" % src_out_fn)
    src_dem_match = iolib.ds_getma(src_dem_clip_ds)
    print("Computing difference map...")
    
    diff_match = src_dem_match - ref_dem_match
    avg_diff = np.nanmean(diff_match.compressed())
    pos_avg_diff = np.nanmean(diff_match.compressed()[diff_match.compressed() > 0]) #average of positive values
    neg_avg_diff = np.nanmean(diff_match.compressed()[diff_match.compressed() < 0]) #average of negative values
    abs_avg_diff = np.nanmean(np.abs(diff_match.compressed()))
    abs_med = np.nanmedian(np.abs(diff_match.compressed()))
    abs_std = np.nanstd(np.abs(diff_match.compressed()))
    abs_min = np.nanmin(np.abs(diff_match.compressed()))
    abs_max = np.nanmax(np.abs(diff_match.compressed()))
    abs_1_percentile_diff = np.nanpercentile(np.abs(diff_match.compressed()), 1)
    abs_5_percentile_diff = np.nanpercentile(np.abs(diff_match.compressed()), 5)
    abs_95_percentile_diff = np.nanpercentile(np.abs(diff_match.compressed()), 95)
    abs_99_percentile_diff = np.nanpercentile(np.abs(diff_match.compressed()), 99)
    #NMAD is 
    utilities.log("Source DEM: %s" % os.path.basename(src_dem_fn), log_file)
    utilities.log("Reference DEM: %s" % os.path.basename(ref_dem_fn), log_file)
    utilities.log("DoD File (src-ref): %s" % os.path.basename(out_diff_fn), log_file)
    utilities.log("Output directory: %s" % outdir, log_file)
    utilities.log("Resolution of source, reference DEMs: %0.4f, %0.4f" % (src_res, ref_res), log_file)
    utilities.log("Average difference: %0.4f" % avg_diff, log_file)
    utilities.log(("Average of positive difference values: %0.4f" % pos_avg_diff), log_file)
    utilities.log(("Average of negative difference values: %0.4f" % neg_avg_diff), log_file)
    utilities.log(("Absolute average difference: %0.4f" % abs_avg_diff), log_file)
    utilities.log(("Absolute median difference: %0.4f" % abs_med), log_file)
    utilities.log(("Absolute standard deviation: %0.4f" % abs_std), log_file)
    utilities.log(("Absolute minimum difference: %0.4f" % abs_min), log_file)
    utilities.log(("Absolute maximum difference: %0.4f" % abs_max), log_file)
    utilities.log(("Absolute 1st percentile difference: %0.4f" % abs_1_percentile_diff), log_file)
    utilities.log(("Absolute 5th percentile difference: %0.4f" % abs_5_percentile_diff), log_file)
    utilities.log(("Absolute 95th percentile difference: %0.4f" % abs_95_percentile_diff), log_file)
    utilities.log(("Absolute 99th percentile difference: %0.4f" % abs_99_percentile_diff), log_file)
 
    print("Writing out difference map for common intersection")
    iolib.writeGTiff(diff_match, out_diff_fn, ref_dem_clip_ds)
    src_dem_clip_ds = None
    ref_dem_clip_ds = None
  
def shift_dem(src_dem_fn, outdir, shift):

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

def plot_DoD(dod_fn, dem_fn, stats_fn):
    print("Plotting DoD...")
    with rasterio.open(dod_fn) as dod:
        dod_dem = dod.read(1)

    # Reading the DEM for hillshade
    with rasterio.open(dem_fn) as dem:
        dem_data = dem.read(1)
    #Mask no data from DEM
    dod_nodata = dod.nodata
    dod_dem_ma = np.ma.masked_equal(dod_dem, dod_nodata)
    #Count valid pixels
    valid_pixels = np.sum(~dod_dem_ma.mask)
    print(f"Valid pixels: {valid_pixels}")
    # Generate hillshade from the DEM
    print("Generating hillshade from DEM")
    ls = LightSource(azdeg=315, altdeg=45)
    hillshade = ls.hillshade(dem_data, vert_exag=1, dx=1, dy=1)

    # Normalize based on 2nd and 98th percentiles for DoD
    print("Normalizing DoD for plotting based on 2nd and 98th percentiles")
    dod_clim = np.percentile(dod_dem_ma.compressed(), [2, 98])
    #check if 2 and 98 percentiles are 0
    if dod_clim[0] == 0 and dod_clim[1] == 0:
        dod_clim = [-1, 1]
    # Determine the bounds for the area of interest (Zoom in on the DoD)
    # Here we use a simple threshold method; adjust as needed
    threshold = np.nanmean(dod_dem_ma) + np.nanstd(dod_dem_ma)
    significant_changes = np.where(dod_dem_ma > threshold)
    ymin, ymax = significant_changes[0].min(), significant_changes[0].max()
    xmin, xmax = significant_changes[1].min(), significant_changes[1].max()
    print("DoD bounds: ", xmin, xmax, ymin, ymax)
    
    # Create output plot
    f, axa = plt.subplots(1, 2, figsize=(16, 10))

    # Plotting Hillshade
    axa[0].imshow(hillshade, cmap='gray', clim=dod_clim, aspect='auto')
    # Overlaying DoD with adjusted transparency
    im = axa[0].imshow(dod_dem_ma, cmap='coolwarm_r', clim=dod_clim, alpha=0.5)  # Adjusted alpha
    axa[0].set_title('Elevation Difference (DoD)', fontsize=14)
    axa[0].set_xlim(xmin, xmax)
    axa[0].set_ylim(ymax, ymin)  # Note: y-axis is inverted

    # Add colorbar for DoD
    cbar = plt.colorbar(im, ax=axa[0], orientation='vertical', fraction=0.046, pad=0.04)
    cbar.set_label('Elevation Difference (m)', fontsize=12)

    # Plotting Histogram of DoD with Log Scale
    bins = np.linspace(dod_clim[0], dod_clim[1], 50)
    print("Plotting histogram of DoD")
    axa[1].hist(dod_dem_ma.ravel(), bins, color='skyblue', alpha=0.7)  # Add , log=True for log scale
    axa[1].set_xlim((dod_clim[0], dod_clim[1]))
    axa[1].set_title("Histogram of DoD", fontsize=14)
    axa[1].set_ylabel("Count (Pixels)", fontsize=12)
    axa[1].set_xlabel("Elevation Difference (m)", fontsize=12)

    # Saving the figure
    f.tight_layout()
    fig_fn = os.path.splitext(dod_fn)[0] + '_DoD_Summary.png'
    f.savefig(fig_fn, dpi=300)
    print(f"Saved figure: {fig_fn}")
    plt.show()


def main():
    
    src_fn = r"Z:\ATD\Drone Data Processing\Exports\Differencing_Testing\East_Troublesome\MM\LIDAR_Clip_Test\MM_2023___MM090122_DEM_shifted.tif"
    ref_fn = r"Z:\ATD\Drone Data Processing\Exports\Differencing_Testing\East_Troublesome\MM\LIDAR_Clip_Test\Mod_CoReg_All____MM090122_DEM_shifted.tif"
    res = 'max'  # Resolution parameters include 'min', 'max', 'mean', 'common_scale_factor'
    extent = 'intersection'
    outdir = r"Z:\ATD\Drone Data Processing\Exports\Differencing_Testing\East_Troublesome\MM\LIDAR_Clip_Test"
    shift = [1.4852490064507742, -0.5286683072942407, 0.99560546875] #dx, dy, dz

    #LIDAR = r"Z:\ATD\Drone Data Processing\Exports\Bennett\LIDAR\092021_LIDAR.tin.tif"
    LIDAR = r"Z:\ATD\Drone Data Processing\Exports\East_Troublesome\LIDAR\Reprojected to UTM Zone 13N\ET_middle_LIDAR_2020_1m_DEM_reproj.tif"

    DoD, stats_fn = match_diff(src_fn, ref_fn, res, extent)
    
    print(f"Stats file: {stats_fn}")
    print(f"DoD file: {DoD}")

    plot_DoD(DoD, LIDAR, stats_fn)
        
if __name__ == "__main__":
    main()