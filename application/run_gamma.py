import sys
sys.path.append('..')
import pandas as pd
import numpy as np
import sys
sys.path.append('..')
from pathlib import Path
from gamma.utils import association, from_seconds
from tqdm import tqdm
import os

root_path = Path('/home/jc/Data/GD/xfj_test')
config = {
    'staloc':root_path / "gd_sta.txt",
    'result_dir': root_path/'result',
    'center': (114, 23),
    'xlim_degree': [109, 119],
    'ylim_degree': [20, 26],
    'degree2km': 111.19492474777779,
}
data_dir = lambda x: os.path.join(config['result_dir'], x)
catalog_csv = data_dir("catalog_gamma.csv")
picks_csv = data_dir("picks_gamma.csv")
f = os.path.join(config['result_dir'],'picks.csv')
df=pd.read_csv(f)
picks = pd.DataFrame(columns = ['id', 'sta', 'type', 'timestamp', 'prob'])
picks['id'] = df['phase_index']
picks['sta']= df['station_id'].apply(lambda x:x.split('_')[1].split('.')[0]+'.'+x.split('_')[1].split('.')[1])
picks['type']=df['phase_type']
picks["timestamp"]=pd.to_datetime(df.phase_time)+pd.Timedelta(hours=8)
picks['prob']=df['phase_score']
picks["time_idx"] = picks["timestamp"].apply(lambda x: x.strftime("%Y-%m-%dT%H"))  ## process by hours
picks.reset_index(drop=True,inplace=True)
if "amp" not in picks.columns:
    picks["amp"] = 1
# -----station----------
stations = pd.read_csv(config['staloc'], sep="\s+", header=None)
stations.columns = ['id', 'latitude', 'longitude', 'elevation(m)']
stations["sta"] = stations.id.apply(lambda x: x[-2:] + '.' + x[0:-2])
stations["id"] = stations.sta.apply(lambda x: x + ".00.BH")
stations['unit'] = "m/s"
stations["x(km)"] = stations["longitude"].apply(lambda x: (x - config["center"][0]) * config["degree2km"])
stations["y(km)"] = stations["latitude"].apply(lambda x: (x - config["center"][1]) * config["degree2km"])
stations["z(km)"] = stations["elevation(m)"].apply(lambda x: -x / 1e3)
# ------picks merge with sta--------
picks_merge = picks.merge(stations["sta"], how="right", on="sta")
nan_idx = picks_merge.isnull().any(axis=1)
picks = picks_merge[~nan_idx]
# ------ setting GMMA configs
config["dims"] = ['x(km)', 'y(km)', 'z(km)']
config["use_dbscan"] = True
config["use_amplitude"] = False
config["x(km)"] = (np.array(config["xlim_degree"]) - np.array(config["center"][0])) * config["degree2km"]
config["y(km)"] = (np.array(config["ylim_degree"]) - np.array(config["center"][1])) * config["degree2km"]
config["z(km)"] = (0, 20)
config["vel"] = {"p": 6.0, "s": 6.0 / 1.75}
config["method"] = "BGMM"
if config["method"] == "BGMM":
    config["oversample_factor"] = 4
if config["method"] == "GMM":
    config["oversample_factor"] = 1
config["bfgs_bounds"] = (
    (config["x(km)"][0] - 1, config["x(km)"][1] + 1),  # x
    (config["y(km)"][0] - 1, config["y(km)"][1] + 1),  # y
    (0, config["z(km)"][1] + 1),  # x
    (None, None),  # t
)
config["dbscan_eps"] = min(
    6,  # seconds
    np.sqrt(
        (stations["x(km)"].max() - stations["x(km)"].min()) ** 2
        + (stations["y(km)"].max() - stations["y(km)"].min()) ** 2
    )
    / (6.0 / 1.75),
)
config["dbscan_eps"] = 15
config["dbscan_min_samples"] = min(3, len(stations))
config["min_picks_per_eq"] = 6
config["max_sigma11"] = 2.0
config["max_sigma22"] = 1.0
config["max_sigma12"] = 1.0
for k, v in config.items():
    print(f"{k}: {v}")
# --------------------
# --------------------
pbar = tqdm(sorted(list(set(picks["time_idx"]))))
event_idx0 = 0  ## current earthquake index
assignments = []
if (len(picks) > 0) and (len(picks) < 5000):
    catalogs, assignments = association(picks, stations, config, event_idx0, config["method"], pbar=pbar)
    event_idx0 += len(catalogs)
else:
    catalogs = []
    for i, hour in enumerate(pbar):
        picks_ = picks[picks["time_idx"] == hour]
        meta = picks_.merge(stations["sta"], how="right", on="sta")
        nan_idx = meta.isnull().any(axis=1)
        if len(set(meta[~nan_idx].sta)) < 3:
            continue
        catalog, assign = association(picks_, stations, config, event_idx0, config["method"], pbar=pbar)
        event_idx0 += len(catalog)
        catalogs.extend(catalog)
        assignments.extend(assign)

## create catalog
catalogs = pd.DataFrame(catalogs,
                        columns=["time(s)"] + config["dims"] + ["magnitude", "sigma_time", "sigma_amp",
                                                                "cov_time_amp",
                                                                "event_idx", "prob_gamma"])
catalogs["time(s)"] = catalogs["time(s)"]
catalogs["time"] = catalogs["time(s)"].apply(lambda x: from_seconds(x))
catalogs["longitude"] = catalogs["x(km)"].apply(lambda x: x / config["degree2km"] + config["center"][0])
catalogs["latitude"] = catalogs["y(km)"].apply(lambda x: x / config["degree2km"] + config["center"][1])
catalogs["depth(m)"] = catalogs["z(km)"].apply(lambda x: x * 1e3)
with open(catalog_csv, 'w') as fp:
    catalogs.to_csv(fp, sep="\t", index=False,
                    float_format="%.3f",
                    date_format='%Y-%m-%dT%H:%M:%S.%f',
                    columns=["time", "magnitude", "longitude", "latitude", "depth(m)", "sigma_time", "sigma_amp",
                             "cov_time_amp", "event_idx", "prob_gamma"])
catalogs = catalogs[
    ['time', 'magnitude', 'longitude', 'latitude', 'depth(m)', 'sigma_time', 'sigma_amp', 'prob_gamma']]

## add assignment to picks
assignments = pd.DataFrame(assignments, columns=["pick_idx", "event_idx", "prob_gamma"])
# picks["timestamp"] = picks.timestamp.apply(lambda x: x + pd.Timedelta(hours=8))
picks = picks.join(assignments.set_index("pick_idx")).fillna(-1).astype({'event_idx': int})
with open(picks_csv, 'w') as fp:
    picks.to_csv(fp, sep="\t", index=False,
                 date_format='%Y-%m-%dT%H:%M:%S.%f',
                 columns=["id", "sta", "timestamp", "type", "prob", "amp", "event_idx", "prob_gamma"])
# breakpoint()