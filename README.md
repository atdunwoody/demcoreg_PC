# demcoreg_PC
David Shean's demcoreg library adapted to work on windows.

# Installation

## Open a Command Prompt or PowerShell Window

- Open a Command Prompt or PowerShell by searching for "cmd" or "PowerShell" in the Start menu.

## Create and Activate Python Environment

1. **Create the environment** by running:

    ```cmd
    conda create -c conda-forge -n demcoreg_env python gdal rasterio geopandas
    ```

2. **Activate the environment**:

    ```cmd
    conda activate demcoreg_env
    ```

3. **Create a directory to store code from GitHub repositories**. For example, `C:\Users\<YourUsername>\src`. You can create this directory using File Explorer or the command line:

    ```cmd
    mkdir C:\Users\<YourUsername>\src
    ```

4. **Navigate to the new directory**:

    ```cmd
    cd C:\Users\<YourUsername>\src
    ```

5. **Clone GitHub repositories**:

    ```cmd
    git clone https://github.com/atdunwoody/pygeotools.git
    git clone https://github.com/atdunwoody/demcoreg.git
    git clone https://github.com/atdunwoody/imview.git
    ```

6. **Install these packages with Conda Python**:

    ```cmd
    pip install -e pygeotools\
    pip install -e demcoreg\
    pip install -e imview\
    ```

## Making Command-Line Scripts Convenient to Run

In Windows, you add directories to the system or user PATH environment variable to make command-line scripts easily executable from anywhere.

1. **Add directories to the PATH**:

    - Right-click on 'This PC' or 'Computer' and select 'Properties'.
    - Click on 'Advanced system settings'.
    - In the System Properties window, go to the 'Advanced' tab and click on 'Environment Variables'.
    - Under 'System variables' (for all users) or 'User variables' (for the current user only), find the 'Path' variable and click 'Edit'.
    - Click 'New' and add the full path to each of the directories you wish to add to the PATH, such as the paths to the `pygeotools`, `demcoreg`, and `imview` directories inside `C:\Users\<YourUsername>\src`.
    - Click 'OK' to close all dialog boxes.

2. **Apply Changes**:

    - Restart your command prompt or PowerShell window for the changes to take effect.


## Masking Options

### Reflectance & Snow Cover Options
- `--toa`: Use top-of-atmosphere reflectance values.
- `--toa_thresh [0.0-1.0]`: TOA reflectance threshold.
- `--snodas`: Use SNODAS snow depth products.
- `--snodas_thresh [m]`: SNODAS snow depth threshold.
- `--modscag`: Use MODSCAG fractional snow cover products.
- `--modscag_thresh [0-100]%`: MODSCAG snow cover percent threshold.

### Land Cover & Filters
- `--bareground`: Enable bareground filter.
- `--bareground_thresh [0-100]%`: Percent bareground threshold.
- `--glaciers`: Mask glacier polygons.
- `--nlcd`: Enable NLCD LULC filter (for CONUS).
- `--nlcd_filter [options]`: NLCD pixel preservation category. Choices are 'rock', 'rock+ice', 'rock+ice+water', 'not_forest', 'not_forest+not_water', 'none'.

### Mask Modification
- `--dilate [iterations]`: Dilate mask with this many iterations.


