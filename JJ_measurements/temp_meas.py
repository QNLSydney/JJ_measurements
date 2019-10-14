import requests
from functools import partial
from qcodes import Instrument

class FridgeTemps(Instrument):
    def __init__(self, fridge, url):
        super().__init__(fridge)
        self.url = url
        
        params = requests.get(url)
        if params.status_code != 200:
            raise RuntimeError("Unable to query fridge")
        params = set(params.json().keys())
        params.remove("Time")
        params = tuple(params)
        self.params = params
        
        for param in params:
            self.add_parameter(f"{param}_temp",
                               unit="K",
                               label=f"{param}",
                               get_cmd=partial(self.get_param, param),
                               snapshot_get=False)
        
    def get_param(self, param):
        temps = requests.get(self.url)
        if temps.status_code != 200:
            raise RuntimeError("Unable to query fridge")
        temps = temps.json()
        return temps[param]