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
    
    src_dem_list =[r"Z:\ATD\Drone Data Processing\Exports\Differencing_Testing\East_Troublesome\MM\No_Interpolation\MM_2023___MM090122_PE_PCFilt_ATD.tif",
                    r"Z:\ATD\Drone Data Processing\Exports\Differencing_Testing\East_Troublesome\MM\No_Interpolation\Mid_CoReg_All_____MM090122_Final_Op_ATD.tif" 
                    ]#First DEM in list should be first in time, last should be last in time
    #ref_dem_fn =r"Z:\ATD\Drone Data Processing\Exports\East_Troublesome\LIDAR\Reprojected to UTM Zone 13N\ET_middle_LIDAR_2020_1m_DEM_reproj.tif" #path to the reference DEM to align DEMs to(LIDAR)
    ref_dem_fn =r"Z:\ATD\Drone Data Processing\Exports\Differencing_Testing\East_Troublesome\MM\No_Interpolation\MM_2023___MM090122_PE_PCFilt_ATD.tif" #path to the reference DEM to align DEMs to
    outdir = r"Z:\ATD\Drone Data Processing\Exports\Differencing_Testing\East_Troublesome\MM\Co-Aligned_SfM_No_LIDAR_nuth_max" #folder to save the output
    res = 'max' #resolution of the output
    matchres = 0.25
    extent = 'intersection' #extent of the output
    mode ='nuth' # choices: 'nuth' : Nuth and Kaab 2011, 'sad': Sum of Absolute Differences, or 'ncc' : Normalized cross-correlation
    
    ref_out, src_out = diff.match_dems(src_dem_list[1], ref_dem_fn, outdir, matchres, extent, writeref=True)
    
    aligned_dem_list = []
    shift_list = []
    resampled_dem_list = [ref_out, src_out]
    align_fn, shift = da.get_shift(ref_out, src_out, outdir, mode = mode, res = res)
    shift_fn = diff.shift_dem(src_dem_list[1], outdir, shift)

    i = 1
    for align_fn in src_dem_list[1:]:
        DoD_stats_fn = os.path.join(outdir, os.path.basename(src_dem_list[i]).replace('.tif', '_DoD_stats.txt')) 
        utilities.log('DoD Statistics', DoD_stats_fn, header=True)
        utilities.log('1. and 2. below were aligned to 1. using Nuth & Kaab algorithm', DoD_stats_fn)
        utilities.log('4. below is the difference of the aligned 1. and 2. DEMs', DoD_stats_fn)
        utilities.log('1. Reference  DEM: {}'.format(src_dem_list[0]), DoD_stats_fn)
        utilities.log('2. Current pre-shift DEM: {}'.format(src_dem_list[i]), DoD_stats_fn)
        utilities.log('Shift applied to current DEM: {}'.format(shift_list), DoD_stats_fn)

        
        dod_fn, stats_fn = diff.match_diff(ref_dem_fn, shift_fn, res, extent, align_stats_fn = DoD_stats_fn)
        #Option to difference without changing res or extent.p
        #diff.DoD_Stats(ref_out_fn, src_out_fn, outdir, res, extent, log_file = align_stats_fn, out_diff_fn=diff_fn)
        diff.plot_DoD(dod_fn, ref_dem_fn, stats_fn)
        i += 1
if __name__ == "__main__":
    main()