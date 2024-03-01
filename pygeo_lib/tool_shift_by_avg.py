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
                    ]#First DEM in list should be first in time, last should be last in time
    ref_dem_fn =r"Z:\ATD\Drone Data Processing\Exports\East_Troublesome\LIDAR\Reprojected to UTM Zone 13N\ET_middle_LIDAR_2020_1m_DEM_reproj.tif" #path to the reference DEM to align DEMs to(LIDAR)
    outdir = r"Z:\ATD\Drone Data Processing\Exports\Differencing_Testing\East_Troublesome\MM\Script_Processed\072023-102023\Alignment_test" #folder to save the output
    res = 'max' #resolution of the output
    extent = 'intersection' #extent of the output
    mode ='nuth' # choices: 'nuth' : Nuth and Kaab 2011, 'sad': Sum of Absolute Differences, or 'ncc' : Normalized cross-correlation
    
    aligned_dem_list = []
    shift_list = []
    for src in src_dem_list:
        align_fn, shift = da.get_shift(ref_dem_fn, src, outdir, mode = mode, res = res)
        aligned_dem_list.append(align_fn)
        shift_list.append(shift)
    average_shift = np.mean(shift_list, axis = 0)
    
    shift_list = []
    for src in src_dem_list:
        shifted_dem = diff.shift_dem(src, outdir, average_shift)
        shift_list.append(shifted_dem)
    diff.match_diff(shift_list[0], shift_list[1], res, extent)
if __name__ == "__main__":
    main()