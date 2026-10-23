# PWA-hydro-conditioning-main
Author: Idil Yaktubay (iyaktubay@iisd-ela.org), IISD-ELA

This repository is the **orchestrator entry point** for the PWA pipeline. Installing it gives you a unified command-line interface (`pwa-step0` … `pwa-step3`) for the four packages that implement the pipeline:

| Package | Step(s) it owns | Source repo |
|---|---|---|
| [`pwa-tools`](https://github.com/IISD-ELA/PWA-hydro-conditioning-tools) | Step 0 — hydro-conditioning | PWA-hydro-conditioning-tools |
| [`pwa-raven`](https://github.com/IISD-ELA/PWA) | Steps 1 & 2 — NetCDF processing + Raven inputs | PWA / pwa_raven |
| [`pwa-calibration`](https://github.com/IISD-ELA/PWA) | Step 3 — calibration | PWA / pwa_calibration |

You can install just this repository and pip will pull the underlying packages along with it.

## Unified CLI (Recommended)

After [installation](#setup-instructions), every pipeline step uses the same command shape (`pwa-<name>` to run, `pwa-init-<name>` to interactively build its config):

```bash
pwa-init-hydrocondition pwa_config.yml
pwa-hydrocondition --config pwa_config.yml      # Step 0 — hydro-conditioning

pwa-init-nc-processing nc_processing.yml
pwa-nc-processing --config nc_processing.yml    # Step 1 — NetCDF / forcing processing

pwa-init-raven-inputs raven_inputs.yml
pwa-raven-inputs --config raven_inputs.yml      # Step 2 — Raven input generation
                                                # (also writes RavenView visualization
                                                #  files when rivers_shapefile is set)

pwa-init-calibration calibration.yml
pwa-calibrate --config calibration.yml          # Step 3 — calibration
```

### RavenView visualization

When `rivers_shapefile` is set in `raven_inputs.yml`, `pwa-raven-inputs` also writes a [RavenView](https://raven.uwaterloo.ca/RavenView/RavenView.html)-compatible GeoJSON pair into `<output_dir>/Raven/RavenView/`:

```
<output_dir>/Raven/RavenView/
    <watershed_name>.json         # subbasins
    <watershed_name>Rivers.json   # rivers
```

Upload both at <https://raven.uwaterloo.ca/RavenView/RavenView.html> to render the watershed in the browser. Set `write_ravenview: false` to opt out, or leave `rivers_shapefile` unset to skip the export entirely. A standalone `pwa-ravenview` CLI exists for one-off exports outside the pipeline.

These commands are also available as Python modules (`python -m pwa_tools.run_step0`, `python -m pwa_raven.run_nc_processing`, etc.) for users who prefer that style.

The `hydro_condition_v2.py` and `hydro_condition.py` scripts in this directory remain as backwards-compatibility shims for Step 0; new users should prefer `pwa-hydrocondition`.

## Notebook / Python API usage

The CLI is the easiest path for one-shot runs. Inside Jupyter or a custom script you have **two equivalent import styles** — pick whichever fits your code:

### Style A — Umbrella import (recommended for notebooks)

After installing the `pwa` package, every public callable and config class is available under a single namespace:

```python
import pwa

# Step 0 — hydro-conditioning
config0 = pwa.PwaConfig.from_yaml("pwa_config.yml")
step0 = pwa.run_step0(config0, generate_wetlands=False)

# Step 1 — NetCDF processing
config1 = pwa.NcProcessingConfig.from_yaml("nc_processing.yml")
step1 = pwa.run_nc_processing(config1)

# Step 2 — Raven input generation (also writes RavenView GeoJSON when
# rivers_shapefile is set in the config).
config2 = pwa.RavenInputsConfig.from_yaml("raven_inputs.yml")
step2 = pwa.run_raven_inputs(config2)
# step2.ravenview_subbasins and .ravenview_rivers point at the GeoJSON
# pair, or are None if RavenView export was skipped.

# Or generate a one-off RavenView export from an existing config:
# sub, riv = pwa.export_for_ravenview_from_config(config2)

# Step 3 — calibration
config3 = pwa.CalibrationConfig.from_yaml("calibration.yml")
step3 = pwa.run_calibration(config3, db_suffix="notebook_run", repetitions=10)
```

Or import only what you need:
```python
from pwa import PwaConfig, run_step0, NcProcessingConfig, run_nc_processing
```

`pwa.__all__` lists every re-exported symbol; `dir(pwa)` and IDE autocomplete both surface them.

### Style B — Source-package imports

Importing directly from the package that defines each function works the same and makes ownership explicit. Useful when reading code that crosses package boundaries, or when a future maintainer wants to know exactly where a callable lives:

```python
from pwa_tools.config import PwaConfig
from pwa_tools.runner import run_step0

from pwa_raven.nc_processing import NcProcessingConfig, run_nc_processing
from pwa_raven.raven_inputs import RavenInputsConfig, run_raven_inputs

from pwa_calibration.setup import CalibrationConfig
from pwa_calibration.runner import run_calibration
```

Behaviour is identical; the `pwa.*` symbols are direct re-exports of these.

### Common patterns

- **`<Config>.from_yaml(path)`** loads a YAML file written by the corresponding `pwa-init-*` command. This is the most ergonomic path for notebooks — generate the config once interactively, then iterate in the notebook by reloading.
- **`<Config>.from_dict({...})`** builds a config without ever touching the filesystem. Useful for parameter sweeps or programmatically generated configs.
- **All `run_*` functions return a result dataclass** with `Path` attributes pointing at the produced files — easy to chain into matplotlib, geopandas, or rasterio for downstream analysis in the same notebook.
- **The pipeline is logged through Python's standard `logging` module**. To see progress in a notebook, configure logging once at the top:
  ```python
  import logging
  logging.basicConfig(level=logging.INFO, format="%(message)s")
  ```

## Quick install (for the impatient)

Today (GitHub-only, before the packages are on PyPI), clone all three source repos and pip-install them in dependency order:

```bash
git clone https://github.com/IISD-ELA/PWA-hydro-conditioning-tools.git
git clone https://github.com/IISD-ELA/PWA.git
git clone https://github.com/IISD-ELA/PWA-hydro-conditioning-main.git

conda create -n pwa python=3.12
conda activate pwa
conda install -c conda-forge gdal

pip install -e ./PWA-hydro-conditioning-tools
pip install -e ./PWA/pwa_raven
pip install -e ./PWA/pwa_calibration
pip install -e ./PWA-hydro-conditioning-main      # registers pwa-step0 .. pwa-step3 on PATH
```

Verify:

```bash
pwa-hydrocondition --help
```

**Future (post-PyPI publish)**: a single `pip install pwa` will replace the four-line install block above.

## Repository Structure
```
PWA-hydro-conditioning-main/
├── pyproject.toml              # Orchestrator package — declares pwa-tools / pwa-raven / pwa-calibration as deps + console scripts
├── src/pwa/__init__.py         # Empty namespace anchor for the orchestrator package
├── hydro_condition_v2.py       # Backwards-compat shim — equivalent to `pwa-step0`
├── hydro_condition.py          # Legacy interactive runner (will be deprecated)
├── pwa_config.example.yml      # Sample config for Step 0
├── README.md                   # This documentation
├── hydrocon_env.yml            # Conda environment file
└── .gitignore                  # Tells Git to ignore the "Data" folder
```

## Prerequisites
To be able to run this pipeline, the user must do the following:
1) **Install Anaconda**: You can install the latest version of Anaconda [here](https://www.anaconda.com/download). While any recent version of Conda should work, this documentation was prepared using Conda version **24.9.2**. If you encounter issues that may be related to your Conda version, please reach out to us. We recommend installing the full Anaconda distribution (rather than Miniconda), as the steps in this documentation assume a full Conda installation.
2) **Configure Git**:
   
    2(a) If you don't already have one, [create a GitHub account](https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github#signing-up-for-a-new-personal-account).
   
   2(b) Download and install Git to your desktop from the [official site](https://git-scm.com/downloads).
   
   2(c) Connect your local machine to GitHub using SSH. This allows you to securely clone and push repositories without typing your password everytime. For step-by-step instructions, see [GitHub's official documentation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).
   
   2(d) Install and enable the Python extension in VS Code from the Extensions panel in VS Code:

   <img width="593" height="359" alt="image" src="https://github.com/user-attachments/assets/e6bbe9d9-b95c-48eb-a5b7-4b3f5f24455d" />
4) **Install GDAL**: GDAL is a geospatial data processing software that our hydro-conditioning product utilizes. You can install ```GDAL``` by running the ```conda install -c conda-forge gdal```command on Anaconda PowerShell Prompt. You can verify the install with ```gdalinfo --version```.


## Setup Instructions
### 1. Clone this repository and the pwa-tools repository
1.1 Open the Visual Studio Code app on your desktop.
1.2 Open a new Powershell terminal by using the toolbar on the top left corner.

<img width="604" height="146" alt="image" src="https://github.com/user-attachments/assets/d3960591-8bfb-49e4-8c2c-9ad2cfa8a521" />

Your terminal should look something like this:
```powershell
(base) PS C:\Users\iyaktubay>
```
1.3 Clone this repository to your workspace by running the following command:
```powershell
(base) PS C:\Users\iyaktubay> git clone https://github.com/IISD-ELA/PWA-hydro-conditioning-main.git
```
1.4 In the same workspace, clone the [pwa-tools repository](https://github.com/IISD-ELA/PWA-hydro-conditioning-tools) by running the following command:
```powershell
(base) PS C:\Users\iyaktubay> git clone https://github.com/IISD-ELA/PWA-hydro-conditioning-tools.git
```
1.5 Close the Visual Studio Code app.
### 2. Create your environment
2.1 Navigate to the Anaconda PowerShell Prompt App: 

<img width="292" height="66" alt="image" src="https://github.com/user-attachments/assets/aac6a61a-4dc6-48e4-90bc-b97c5ac431c9" />

2.2 In the command line, change your working directory to the cloned ```PWA-hydro-conditioning-tools``` folder.
You can do this with the ```cd``` command, followed by a space and the path to the folder (relative to your current location). For example, if the cloned folder is located ```C:\Users\iyaktubay\PWA-hydro-conditioning-main``` and your current location is ```C:\Users\iyaktubay```, then the appropriate command would be:
```powershell
(base) PS C:\Users\iyaktubay> cd PWA-hydro-conditioning-main
```
And, after running the command, your terminal would look like this:
```powershell
(base) PS C:\Users\iyaktubay\PWA-hydro-conditioning-main>
```
2.3 Now that your working directory is the ```PWA-hydro-conditioning-tools``` folder, you can create your environment by running the following command:
```powershell
(base) PS C:\Users\iyaktubay\PWA-hydro-conditioning-main> conda env create -f hydrocon_env.yml
```
2.4 To confirm that your environment has been successfully created, you can run the following command:
```powershell
(base) PS C:\Users\iyaktubay\PWA-hydro-conditioning-main> conda env list
```
This should return something like this:
```powershell
# conda environments:
#
base                  *  C:\Users\iyaktubay\AppData\Local\anaconda3
geotest                  C:\Users\iyaktubay\AppData\Local\anaconda3\envs\geotest
hydrocon_env             C:\Users\iyaktubay\AppData\Local\anaconda3\envs\hydrocon_env
pwa_dev                  C:\Users\iyaktubay\AppData\Local\anaconda3\envs\pwa_dev
test_env                 C:\Users\iyaktubay\AppData\Local\anaconda3\envs\test_env
(base) PS C:\Users\iyaktubay\PWA-hydro-conditioning-main>
```
### 3. Install the pwa-tools package
3.1 Reopen the Visual Studio Code app and open a new PowerShell terminal just as you did in step 1.2. Your terminal should look like:
```powershell
(base) PS C:\Users\iyaktubay>
```
3.2 Activate the ```hydrocon_env``` environment you have created in step 2 by running the following command:
```powershell
(base) PS C:\Users\iyaktubay> conda activate hydrocon_env
```
Your terminal should now look something like this:
```powershell
(hydrocon_dev) PS C:\Users\iyaktubay>
```
3.3 Change your working directory to the cloned ```PWA-hydro-conditioning-tools``` folder by running the following command (change the path to match your relative path):
```powershell
(hydrocon_dev) PS C:\Users\iyaktubay> cd PWA-hydro-conditioning-tools
```
Your terminal should now look like this:
```powershell
(hydrocon_dev) PS C:\Users\iyaktubay\PWA-hydro-conditioning-tools>
```
3.4 Install the custom ```pwa-tools``` package in editable mode by running the following command. You must install it in editable mode for the pipeline to work correctly.
```powershell
(hydrocon_dev) PS C:\Users\iyaktubay\PWA-hydro-conditioning-tools> pip install -e .
```
3.5 After installation, if the ```pwa-tools``` package was updated in the remote repository, you can locally update the package by uninstalling the package and re-installing it in editing mode:
```powershell
(hydrocon_env) PS C:\Users\iyaktubay\PWA-hydro-conditioning-tools> pip uninstall pwa-tools
```
```powershell
(hydrocon_env) PS C:\Users\iyaktubay\PWA-hydro-conditioning-tools> pip install -e .
```
You can check whether the package was updated in the remote repository by running the following command: 
```powershell
(hydrocon_env) PS C:\Users\iyaktubay\PWA-hydro-conditioning-tools> git status
```
If the package is up to date, you should see something like this:
```powershell
(hydrocon_env) PS C:\Users\iyaktubay\PWA-hydro-conditioning-tools> git status
On branch main
Your branch is up to date with 'origin/main'.
```
### 4. Prepare the input data
Create a ```Data/``` folder inside the ```PWA-hydro-conditioning-main``` folder and download and extract the following zip files into it. Do **not** create any subfolders in the ```Data/``` folder as the ```hydro_condition.py``` script expects all data files to **not** be in subfolders. The script will automatically organize input and output files into subfolders itself.
- Watershed of interest based on outlet point from the [CLRH Hydrofabrics website](https://hydrology.uwaterloo.ca/CLRH/Hydrofabric.html) (e.g., ID: 05OE006 for Manning Canal)
- Streams dataset of interest from [NHN streams website](https://ftp.maps.canada.ca/pub/nrcan_rncan/vector/geobase_nhn_rhn/shp_en/).
     1. In the directory, open the folder named with the first two digits of your CLRH station ID (e.g., open the ```05/``` folder if your CLRH station ID is ```05OE006```).
     2. Download the ```.zip``` file whose name contains the third and fourth digits of your CLRH station ID (e.g., download ```nhn_rhn_05oe000_shp...``` if your CLRH station ID is ```05OE006```).
     3. If multiple ```.zip``` files match, download both and check which shapefile covers the geographic extent of your watershed. You can do this by using a GIS tool such as ArcGIS.
- Raster DEM(s) of interest from [LiDAR DEMs](https://mli.gov.mb.ca/dems/index_external_lidar.html) (e.g., Seine & Rat 2016 for Manning Canal)
- Culvert inventory (optional): Prepare your culvert inventory (only Shapefiles in Line format are currently accepted)

Your local workspace should now have the following structure:
```powershell
your-working-directory/
├── PWA-hydro-conditioning-main/
    ├── hydro_condition.py
    ├── README.md
    ├── .gitignore
    └── Data
        └──  ...data files you downloaded...
└── PWA-hydro-conditioning-tools/
    └──  ...repository contents...
```

### 5. Run the hydroconditioning script
5.1 On Visual Studio Code's welcome page, open the ```PWA-hydro-conditioning-main``` folder by clicking "Open folder...":

<img width="450" height="339" alt="image" src="https://github.com/user-attachments/assets/a307cdca-e5ce-4f85-8038-73004327e639" />

5.2 Open up terminal on Visual Studio Code once again if it's not already open and change your working directory to the ```PWA-hydro-conditioning-main``` folder if it's not already there.

5.3 Run the pipeline. **Two options**:

#### Option A (recommended): `hydro_condition_v2.py` with a config file

Generate a config file once (interactively):
```powershell
python -m pwa_tools.init_config pwa_config.yml
```
The prompts mirror the legacy script's. Or, copy `pwa_config.example.yml` to `pwa_config.yml` and edit by hand.

Then run the pipeline as many times as you like:
```powershell
python hydro_condition_v2.py
python hydro_condition_v2.py --wetlands           # also generate wetlands shapefile
python hydro_condition_v2.py --log-level DEBUG    # extra diagnostic output
python hydro_condition_v2.py --config other.yml   # alternative config
```

The new runner fails fast (with a clear error listing every missing file) if your `Data/` folder is incomplete, instead of crashing partway through a 30-minute LiDAR resample.

#### Option B (legacy): `hydro_condition.py` interactive prompts

The original script that asks for filenames on every run:
```powershell
python hydro_condition.py
```
Still supported during the migration period.

5.4 Once the script has fully run, you will see the output files under the ```Data\<watershed name you entered when prompted>\HydroConditioning\Processed``` folder:

<img width="396" height="268" alt="image" src="https://github.com/user-attachments/assets/c48b59a7-3551-45eb-99a9-38567594141d" />

You can also see any intermediate files in the ```...\Interim``` folder:

<img width="404" height="304" alt="image" src="https://github.com/user-attachments/assets/37a4b00b-21c6-4825-9036-143331cf4745" />

The output files include a depression depths raster .tif, depression depths shapefile, and a zonal statistics file for your watershed by default, as well as a wetland polygons shapefile with statistics (area, total storage, and median depth) if the user chooses to generate it.

### 6. Contact and support
For support or any other inquiries, please contact us at eladata@iisd.net.




