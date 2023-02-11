# %%
import urllib3
import json

base_url = "http://data.rcc-acis.org/StnData"

http = urllib3.PoolManager()
# %%
params = {
    "sid": "190736",
    "sdate": "2022-10-01",
    "edate": "2023-01-01",
    "output": "json",
    "elems": [{"name": "mint", "interval": "mly", "duration": 1, "reduce": "min"},
              {"name": "maxt", "interval": "mly", "duration": 1, "reduce": "max"}]}
# %%
url = base_url + "?params=" + json.dumps(params)
req = http.request('GET', url)
# %%
result = json.loads(req.data.decode('utf-8'))
print(result)
# %%
result["data"]

# %%
