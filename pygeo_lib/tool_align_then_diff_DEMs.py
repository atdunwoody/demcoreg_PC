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
import GIStools.vector.utilities as utilities
import coreglib
import difflib as diff
import dem_align as da

def main():
    """
    Each DEM in src_dem_list is aligned to the reference DEM
    Then the difference between the first DEM in the list and each aligned DEM is calculated
    A plot of the difference is created 
    All outputs are saved to the outdir
    """
    
    src_dem_list =[r"Z:\ATD\Drone Data Processing\Exports\Differencing_Testing\East_Troublesome\MM\Script_Processed\072023-102023\MM072023___MM090122_PE_PCFilt.tif",
                    r"Z:\ATD\Drone Data Processing\Exports\Differencing_Testing\East_Troublesome\MM\Script_Processed\072023-102023\MM102022___MM090122_PE_PCFilt.tif"
                    ]#First DEM in list should be fi

    ref_dem_fn =r"Z:\ATD\Drone Data Processing\Exports\East_Troublesome\LIDAR\Reprojected to UTM Zone 13N\ET_middle_LIDAR_2020_1m_DEM_reproj.tif" #path to the reference DEM to align DEMs to(LIDAR)
    outdir = r"Z:\ATD\Drone Data Processing\Exports\Differencing_Testing\East_Troublesome\MM\Script_Processed\LIDAR_Alignment_slope0-50" #folder to save the output
    LIDAR = r"Z:\ATD\Drone Data Processing\Exports\Bennett\LIDAR\092021_LIDAR.tin.tif"
    #LIDAR = r"Z:\ATD\Drone Data Processing\Exports\East_Troublesome\LIDAR\Reprojected to UTM Zone 13N\ET_middle_LIDAR_2020_1m_DEM_reproj.tif"
    res = 'max' #resolution of the output
    extent = 'intersection' #extent of the output
    mode ='nuth' # choices: 'nuth' : Nuth and Kaab 2011, 'sad': Sum of Absolute Differences, or 'ncc' : Normalized cross-correlation
    log_file = os.path.join(outdir, 'Stats_log_090122_Aligned_to_Lidar.txt')
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    aligned_dem_list = []
    shift_list = []
    for src in src_dem_list:
        align_fn, shift = da.get_shift(ref_dem_fn, src, outdir, mode = mode, res = res)
        aligned_dem_list.append(align_fn)
        shift_list.append(shift)
        utilities.log(f"Shift for {os.path.basename(src)} is {shift}", log_file)
        utilities.log(f"Aligned DEM for {os.path.basename(src)} is {align_fn}", log_file)

    DoD, stats_fn = diff.match_diff(aligned_dem_list[0], aligned_dem_list[1], res, extent, align_stats_fn = log_file)
    diff.plot_DoD(DoD, LIDAR, stats_fn)
    
if __name__ == "__main__":
    main()