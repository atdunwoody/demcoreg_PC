from demcoreg import dem_align as da
from difflib import match_diff
import os

def main():
    src_dems = [ r"Y:\ATD\Drone Data Processing\Exports\East_Troublesome\LPM\LPM_Intersection_PA3_RMSE_018 Exports\LPM_Intersection_PA3_RMSE_018____LPM_081222_PostError_PCFiltered_DEM.tif",   
                ]    
    
    for src in src_dems:    
        kwargs = {
            'ref_dem_fn': r"Y:\ATD\Drone Data Processing\Exports\East_Troublesome\LPM\LPM_Intersection_PA3_RMSE_018 Exports\LPM_Intersection_PA3_RMSE_018____LPM_102123_PostError_PCFiltered_DEM.tif",# Fixed Reference DEM
            'src_dem_fn': src, # Source DEM to be shifted
            'mode': 'nuth', # Co-registration mode to use; choices= 'ncc', 'sad', 'nuth', 'none'
            'mask_list': [],  # choices = 'toa', 'snodas', 'modscag', 'bareground', 'glaciers', 'nlcd', 'none'. See demcoreg/dem_mask.py for more
            'max_offset': 100, # Maximum horizontal offset expected between DEMs, used to limit search space
            'max_dz': 10, # Maximum vertical difference allowed between DEMs before considered an outlier
            'slope_lim': (0.1, 40), # Range of surface slopes to consider in the alignment, outside values are disregarded
            'tiltcorr': False, # Whether to perform tilt correction as a post-process
            'polyorder': 1, # Order of polynomial used for tilt correction, if enabled
            'res': 'min', # Resolution strategy for the alignment; 'max' prioritizes the higher resolution of the two DEMs, 'min' the lower, 'common_scale_factor' the lower scaled to the higher
            'max_iter': 30, # Maximum number of iterations to perform in seeking alignment  
            'tol': 0.02, # Tolerance threshold for iterative process; smaller changes than this will end the iteration
            'outdir': r"Y:\ATD\Drone Data Processing\Alignment_Tests\LPM_Aligned_with_LIDAR\1m co-alignment" # Output directory for aligned DEMs
        }
        #make sure the output directory exists
        if not os.path.exists(kwargs['outdir']):
            os.makedirs(kwargs['outdir'])
        
        #write parameters to a text file in the output directory
        with open(os.path.join(kwargs['outdir'], 'alignment_parameters.txt'), 'w') as f:
            for key, value in kwargs.items():
                f.write(f"{key}: {value}\n")
        
        result_dict = da.dem_align(**kwargs)  
        for key, value in result_dict.items():
            print(f"{key}: {value}")
        
        aligned_src_fn = result_dict['align_fn']
        
        match_diff(aligned_src_fn, kwargs['ref_dem_fn'], kwargs['res'], kwargs['extent'], 
                   outdir = kwargs['outdir'], align_stats_fn =None, orig_stats = False)
if __name__ == "__main__":
    main()