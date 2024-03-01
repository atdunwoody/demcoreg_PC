import os
from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from matplotlib.colors import LightSource

from pygeotools.lib import iolib,  geolib
import logger

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
    logger.log("Source DEM: %s" % os.path.basename(src_dem_fn), log_file)
    logger.log("Reference DEM: %s" % os.path.basename(ref_dem_fn), log_file)
    logger.log("DoD File (src-ref): %s" % os.path.basename(out_diff_fn), log_file)
    logger.log("Output directory: %s" % outdir, log_file)
    logger.log("Resolution of source, reference DEMs: %0.4f, %0.4f" % (src_res, ref_res), log_file)
    logger.log("Average difference: %0.4f" % avg_diff, log_file)
    logger.log(("Average of positive difference values: %0.4f" % pos_avg_diff), log_file)
    logger.log(("Average of negative difference values: %0.4f" % neg_avg_diff), log_file)
    logger.log(("Absolute average difference: %0.4f" % abs_avg_diff), log_file)
    logger.log(("Absolute median difference: %0.4f" % abs_med), log_file)
    logger.log(("Absolute standard deviation: %0.4f" % abs_std), log_file)
    logger.log(("Absolute minimum difference: %0.4f" % abs_min), log_file)
    logger.log(("Absolute maximum difference: %0.4f" % abs_max), log_file)
    logger.log(("Absolute 1st percentile difference: %0.4f" % abs_1_percentile_diff), log_file)
    logger.log(("Absolute 5th percentile difference: %0.4f" % abs_5_percentile_diff), log_file)
    logger.log(("Absolute 95th percentile difference: %0.4f" % abs_95_percentile_diff), log_file)
    logger.log(("Absolute 99th percentile difference: %0.4f" % abs_99_percentile_diff), log_file)
 
    print("Writing out difference map for common intersection")
    iolib.writeGTiff(diff_match, out_diff_fn, ref_dem_clip_ds)
    src_dem_clip_ds = None
    ref_dem_clip_ds = None
  
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
    src_fn =r""
if __name__ == "__main__":
    main()