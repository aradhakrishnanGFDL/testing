import json
from pathlib import Path
import sys
import intake

#catalog json update paths to csv https://github.com/aradhakrishnanGFDL/gfdl-aws-analysis/blob/master/esm-collection-spec-examples/intake-uda.json
#catalog csv https://github.com/aradhakrishnanGFDL/gfdl-aws-analysis/blob/master/esm-collection-spec-examples/intake_uda.csv.gz

class Metadata:
    def meta(self):
      metadata = {"model": "GFDL-ESM4",
        "mip_table" : "Amon",
        "experiment_id" : "historical",
        "version": "v20190726"
         }
      return(metadata) 

    def variables(self):
        return {
            "tasmax": "tasmax",
        }


class RadiationAnalysisScript:
    """Abstract base class for analysis scripts.  User-defined analysis scripts
       should inhert from this class and override the requires and run_analysis methods.

    Attributes:
       description: Longer form description for the analysis.
       title: Title that describes the analysis.
    """
    def __init__(self):
        self.metadata = Metadata()
        self.description = "Calculates radiative flux metrics."
        self.title = "Radiative Fluxes"

    def requires(self):
        """Provides metadata describing what is needed for this analysis to run.

        Returns:
            A json string containing the metadata.
        """
        columns = Metadata.__annotations__.keys()
        settings = {x: getattr(self.metadata, x) for x in columns}
        return json.dumps({
            "settings": settings,
            "dimensions": {
                "lat": {"standard_name": "latitude"},
                "lon": {"standard_name": "longitude"},
                "time": {"standard_name": "time"}
            },
            "varlist": {
                "tasmax": {
                    "standard_name": "air_temperature",
                },
            },
        })

    def run_analysis(self, catalog, png_dir, config=None, reference_catalog=None):
        """Runs the analysis and generates all plots and associated datasets.

        Args:
            catalog: Path to a catalog.
            png_dir: Path to the directory where the figures will be made.
            config: Dictionary of catalog metadata.  Will overwrite the data
                    defined in the Metadata helper class if they both contain
                    the same keys.
            reference_catalog: Path to a catalog of reference data.

        Returns:
            A list of paths to the figures that were created.
        """

        # Connect to the catalog and find the necessary datasets.
        catalog = intake.open_esm_datastore(catalog)
        print(catalog.df)
        anomalies = {}
        maps = {}
        timeseries = {}
        for name, variable in self.metadata.variables().items():
            # Filter the catalog down to a single dataset for each variable.
            query_params = {"variable": variable}
            print(self.metadata.meta())
            query_params.update(self.metadata.meta())
            if config:
                query_params.update(config)
            print(f"About to load with '{query_params}'")
            cat_datasets = catalog.search(**query_params)
            print(cat_datasets.df)
            datasets = cat_datasets.to_dataset_dict(
                progressbar=True,xarray_open_kwargs={'engine':'h5netcdf'} 
            )
           
            if len(list(datasets.values())) != 1:
                raise ValueError(f"could not filter the dataset down to just {variable}.")
            dataset = list(datasets.values())[0]


my_script = RadiationAnalysisScript()
print(my_script)
my_script.run_analysis(catalog='intake_uda.json', png_dir='output')
