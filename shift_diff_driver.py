from utilities.dem_align import get_shift
from utilities.difflib import match_diff, shift_dem


src_fn = r"Y:\ATD\Drone Data Processing\Exports\East_Troublesome\LPM\LPM_Intersection_PA3_RMSE_018 Exports\LPM_Intersection_PA3_RMSE_018____LPM_081222_PostError_PCFiltered_DEM.tif"

ref_fn = r"Y:\ATD\Drone Data Processing\Exports\East_Troublesome\LPM\LPM_Intersection_PA3_RMSE_018 Exports\LPM_Intersection_PA3_RMSE_018____LPM_102123_PostError_PCFiltered_DEM.tif"
LIDAR = r"Y:\ATD\Drone Data Processing\Exports\East_Troublesome\LIDAR\Reprojected to UTM Zone 13N\ET_low_LIDAR_2020_1m_DEM_reproj.tif"
outdir = r"Y:\ATD\Drone Data Processing\Alignment_Tests\LPM_Aligned_with_LIDAR\Max Res LIDAR Alignment"
mode = 'nuth'
res = 'max'
extent = 'intersection'
kwargs = {   
'mask_list': [],
'max_offset': 100,
'max_dz': 100,
'slope_lim': (0.1, 40),
'tiltcorr': False,
'polyorder': 1,
'res': 'max',
'max_iter': 30,
'tol': 0.02,
}

align_src_fn, shift = get_shift(LIDAR, src_fn, outdir, mode = mode, res = res, **kwargs)   
shifted_src_fn = shift_dem(src_fn, outdir, shift)
match_diff(shifted_src_fn, ref_fn, res, extent, outdir = outdir, align_stats_fn =None, orig_stats = False)