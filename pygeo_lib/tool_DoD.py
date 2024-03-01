import difflib as dl
import os

src_fn = r"Z:\ATD\Metashape_Alignment_Tests\Only_Checking_Initial_Photos_Recent_Surveys\MM_0723_1022 Exports\MM_0723_1022____MM_070923_PostError_PCFiltered_DEM.tif"

ref_fn = r"Z:\ATD\Metashape_Alignment_Tests\Only_Checking_Initial_Photos_Recent_Surveys\MM_0723_1023 Exports\MM_0723_1023____MM_070923_PostError_PCFiltered_DEM.tif"
res = 'max'  # Resolution parameters include 'min', 'max', 'mean', 'common_scale_factor'
extent = 'intersection'
outdir = r"Z:\ATD\Metashape_Alignment_Tests\Only_Checking_Initial_Photos\DoD\No_Interp_Matched_Build"
log_file = os.path.join(outdir, 'Stats_log_072023_PPK_Reprocessed.txt')
if not os.path.exists(outdir):
    os.makedirs(outdir)
#LIDAR = r"Z:\ATD\Drone Data Processing\Exports\Bennett\LIDAR\092021_LIDAR.tin.tif"
LIDAR = r"Z:\ATD\Drone Data Processing\Exports\East_Troublesome\LIDAR\Reprojected to UTM Zone 13N\ET_middle_LIDAR_2020_1m_DEM_reproj.tif"

DoD, stats_fn = dl.match_diff(src_fn, ref_fn, res, extent, align_stats_fn = log_file)

print(f"Stats file: {stats_fn}")
print(f"DoD file: {DoD}")

dl.plot_DoD(DoD, LIDAR, stats_fn)