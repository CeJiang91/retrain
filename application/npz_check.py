import numpy as np

fname = '/home/jc/Data/GD/gd_train/gd.npz_phasenet/waveform/GD.XFJ_GD.201303151730.0002.npz'
npz = np.load(fname)
meta = {}
if len(npz["data"].shape) == 2:
    meta["data"] = npz["data"][:, np.newaxis, :]
else:
    meta["data"] = npz["data"]
if "p_idx" in npz.files:
    if len(npz["p_idx"].shape) == 0:
        meta["itp"] = [[npz["p_idx"]]]
    else:
        meta["itp"] = npz["p_idx"]
if "s_idx" in npz.files:
    if len(npz["s_idx"].shape) == 0:
        meta["its"] = [[npz["s_idx"]]]
    else:
        meta["its"] = npz["s_idx"]
if "itp" in npz.files:
    breakpoint()
    if len(npz["itp"].shape) == 0:
        meta["itp"] = [[npz["itp"]]]
    else:
        meta["itp"] = npz["itp"]
if "its" in npz.files:
    if len(npz["its"].shape) == 0:
        meta["its"] = [[npz["its"]]]
    else:
        meta["its"] = npz["its"]
if "station_id" in npz.files:
    meta["station_id"] = npz["station_id"]
if "sta_id" in npz.files:
    meta["station_id"] = npz["sta_id"]
if "t0" in npz.files:
    meta["t0"] = npz["t0"]
breakpoint()