"""PWA pipeline — umbrella package.

Provides:

* **CLI entry points** (registered via ``pyproject.toml``'s
  ``[project.scripts]``): ``pwa-hydrocondition``, ``pwa-nc-processing``,
  ``pwa-raven-inputs``, ``pwa-calibrate`` and the four ``pwa-init-*``
  config builders.
* **Python API re-exports** for notebook use, so users can drive the
  pipeline with one familiar namespace::

      import pwa
      cfg = pwa.NcProcessingConfig.from_yaml("nc_processing.yml")
      result = pwa.run_nc_processing(cfg)

The re-exports below name the canonical public API of each step.
Direct imports from the source package (``from pwa_raven.nc_processing
import run_nc_processing``) continue to work and are equivalent — use
whichever style fits the calling code.
"""

__version__ = "0.1.0"

# Step 0 — hydro-conditioning (pwa-tools)
from pwa_tools.config import PwaConfig
from pwa_tools.runner import Step0Result, run_step0

# Step 1 — NetCDF processing (pwa-raven)
from pwa_raven.nc_processing import (
    NcProcessingConfig,
    NcProcessingResult,
    run_nc_processing,
)

# Step 2 — Raven input generation (pwa-raven)
from pwa_raven.raven_inputs import (
    RavenInputsConfig,
    RavenInputsResult,
    run_raven_inputs,
)

# RavenView export — visualization side-output. Runs automatically as
# part of Step 2 when ``rivers_shapefile`` is set on the config; also
# callable directly for one-off exports outside the pipeline.
from pwa_raven.raven.ravenview import (
    export_for_ravenview,
    export_for_ravenview_from_config,
    validate_ravenview_geojson,
)

# Step 3 — calibration (pwa-calibration)
from pwa_calibration.runner import run_calibration
from pwa_calibration.setup import CalibrationConfig

__all__ = [
    "__version__",
    # Step 0
    "PwaConfig",
    "Step0Result",
    "run_step0",
    # Step 1
    "NcProcessingConfig",
    "NcProcessingResult",
    "run_nc_processing",
    # Step 2
    "RavenInputsConfig",
    "RavenInputsResult",
    "run_raven_inputs",
    # RavenView
    "export_for_ravenview",
    "export_for_ravenview_from_config",
    "validate_ravenview_geojson",
    # Step 3
    "CalibrationConfig",
    "run_calibration",
]
