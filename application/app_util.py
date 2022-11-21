import numpy as np
from obspy import read, UTCDateTime, Stream
import csv
import pandas as pd
import math
from pathlib import Path
import subprocess
import glob
import multiprocessing
import os
import shutil
from functools import partial
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from obspy.geodetics import locations2degrees, degrees2kilometers


def bulletins2picks(bulletins_dir, picks):
    blts = glob.glob(r'%s/*.txt' % bulletins_dir)
    pks = []
    p = multiprocessing.Pool()
    for blt in blts:
        print(blt)
        maneqpha, _ = readjopenseqpha(blt)
        func = partial(_subfunction_bulletins2picks, maneqpha, 120)
        pks_scrap = p.map(func, maneqpha.keys())
        pks_scrap = pd.concat(pks_scrap)
        pks.append(pks_scrap)
    pks = pd.concat(pks)
    p.close()
    p.join()
    pks.to_csv(picks, index=False)


def _subfunction_bulletins2picks(maneqpha, epidis_max, key):
    pks = pd.DataFrame(columns=['sta', 'itp', 'its', 'id'])
    k = key
    sta_dict = {}
    for row in maneqpha[k]:
        net_sta = row[0]
        pha_type = row[1]
        timestamp = row[2]
        epidis = row[3]
        if ('2013-12-26T22:37' in timestamp) and net_sta == 'GD.ZHX':
            print(f"{timestamp},{net_sta},{pha_type}")
        if epidis > epidis_max:
            continue
        sta_dict[net_sta] = {} if net_sta not in sta_dict else sta_dict[net_sta]
        """
        #set1        
        if pha_type in ['Pg', 'Pn']:
            if 'P' in sta_dict[net_sta] and (UTCDateTime(sta_dict[net_sta]['P']) > UTCDateTime(timestamp)):
                sta_dict[net_sta]['P'] = timestamp
            if 'P' not in sta_dict[net_sta]:
                sta_dict[net_sta]['P'] = timestamp
        """
        # set2
        if pha_type in ['Pg']:
            sta_dict[net_sta]['P'] = timestamp
        elif pha_type in ['Sg']:
            sta_dict[net_sta]['S'] = timestamp
        sta_dict[net_sta]['key'] = k
    for net_sta in sta_dict:
        if ('P' in sta_dict[net_sta]) and ('S' in sta_dict[net_sta]):
            pks.loc[len(pks.index)] = [net_sta, sta_dict[net_sta]['P'], sta_dict[net_sta]['S'],
                                       sta_dict[net_sta]['key']]
    return pks


def readjopenseqpha(eqphasf):
    oeqphas = {}
    with open(eqphasf, encoding='GBK') as f:
        lines = f.readlines()
    neqs = [i for i, s in enumerate(lines) if '\n' == s][0]
    for line in lines[neqs + 1:]:
        # if 'eq'==line[61:63]:
        # if ('eq' in line) or ('ss' in line) or ('ep' in line):
        if "/" in line:
            eqymd = line[3:13]
            eqtime = UTCDateTime(line[3:13] + 'T' + line[14:24]).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
            # if '2013-12-26T22:37' in eqtime:
            #     breakpoint()
            if not ' ' in line[26:32]:
                dep = float(line[42:45]) if not line[42:45].isspace() else float('nan')
                eqloc = [float(line[25:32]), float(line[33:41]), dep]
            else:
                eqloc = [float('nan'), float('nan'), float('nan')]
            if not line[46:50].isspace():
                eqmag = float(line[46:50])
            elif not line[51:54].isspace():
                eqmag = float(line[51:54])
            else:
                eqmag = float('nan')
            key = "_".join([eqtime, "{:.4f}".format(eqloc[0]), "{:.4f}".format(eqloc[1]), "{:.2f}".format(eqloc[2]),
                            "{:.1f}".format(eqmag)])
            oeqphas[key] = []
        else:
            if not ' ' == line[0]:
                netstn = line[0:2] + '.' + line[3:8].rstrip()
                epidis = float(line[52:58]) if not line[52:58].isspace() else -12345.0
                try:
                    # if line[29:30] == 'V':
                    phaname = line[17:25].rstrip()
                    if phaname in ['Pn', 'Pg', 'Sn', 'Sg', 'PmP', 'SmS']:
                        if abs(float(line[43:50])) >= 3:  # skip machine time error
                            continue
                        if UTCDateTime(eqymd + 'T' + line[32:43]) - UTCDateTime(eqtime) >= -5:
                            # A partial error(-5s) is allowed
                            phatime = UTCDateTime(eqymd + 'T' + line[32:43]).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
                        else:
                            phatime = UTCDateTime(
                                (UTCDateTime(eqymd + 'T00:00:00.000') + 86400).strftime('%Y-%m-%d') + 'T' + line[
                                                                                                            32:43]).strftime(
                                '%Y-%m-%dT%H:%M:%S.%f')[:-3]
                    oeqphas[key].append([netstn, phaname, phatime, epidis])
                except Exception:
                    continue
            else:
                try:
                    # if line[29:30] == 'V':
                    phaname = line[17:25].rstrip()
                    if phaname in ['Pn', 'Pg', 'Sn', 'Sg', 'PmP', 'SmS']:
                        if abs(float(line[43:50])) >= 3:  # skip machine time error
                            continue
                        if UTCDateTime(eqymd + 'T' + line[32:43]) - UTCDateTime(eqtime) > 0.0:
                            phatime = UTCDateTime(eqymd + 'T' + line[32:43]).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
                        else:
                            phatime = UTCDateTime(
                                (UTCDateTime(eqymd + 'T00:00:00.000') + 86400).strftime('%Y-%m-%d') + 'T' + line[
                                                                                                            32:43]).strftime(
                                '%Y-%m-%dT%H:%M:%S.%f')[:-3]
                        oeqphas[key].append([netstn, phaname, phatime, epidis])
                except Exception:
                    continue
    eqphas = {}
    for key in oeqphas.keys():
        if 'nan' not in key:
            eqphas[key] = oeqphas[key]

    print(len(oeqphas), len(eqphas))
    return oeqphas, eqphas


def mseed2npz(input_dir, output_dir, picks_file):
    input_length = 120
    print('converting...')
    if os.path.isdir(output_dir):
        print('============================================================================')
        print(f' *** {output_dir} already exists!')
        inp = input(" --> Type (Yes or y) to create a new empty directory! otherwise it will overwrite!   ")
        if inp.lower() == "yes" or inp.lower() == "y":
            shutil.rmtree(output_dir)
    os.makedirs(os.path.join(output_dir, 'waveform'))
    clg = pd.read_csv(picks_file)
    clg['dayTime'] = clg.id.apply(lambda x: x.split('_')[0][0:16])
    clg.sort_values(by=['itp'], inplace=True)
    clg.reset_index(drop=True, inplace=True)
    fname = []
    sta_dayTime = []
    sta_id = []
    trn = 0
    csv_file = open(os.path.join(output_dir, "waveform.csv"), 'w', newline='')
    output_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    output_writer.writerow(['fname', 'itp', 'its', 'channels', 'event_id', 't0', 'sta_id'])
    for root, dirs, files in os.walk(input_dir, topdown=True):
        dirs.sort()
        for f in sorted(files):
            evn = f.strip('.seed')
            evnt = UTCDateTime(evn.split('.')[1])
            clg2 = clg[clg.dayTime == evnt.strftime('%Y-%m-%dT%H:%M')]
            if clg2.empty:
                continue
            try:
                trs = read(os.path.join(root, f))
            except Exception:
                print(f"Unknown format for {f}")
                continue
            for _, row in clg2.iterrows():
                net_sta = row.sta
                net = net_sta.split('.')[0]
                sta = net_sta.split('.')[1]
                staid_str = f"{net_sta}_{row.id}"
                if staid_str in sta_id:
                    continue
                tn = f"{net}.{sta}_{evn}.npz"
                trs2 = trs.copy()
                tr3 = trs2.select(network=net, station=sta)
                tr3.merge()
                if tr3.__len__() != 3:
                    continue
                start_time = UTCDateTime(row.itp) - 8 * 3600 - 60 - np.random.randint(0, 20) * 0.1
                sampling_rate = tr3[0].stats.sampling_rate
                if sampling_rate != 100:
                    tr3.resample(100)
                    sampling_rate = 100
                itp_point = np.array(round(sampling_rate * (UTCDateTime(row.itp) - start_time - 8 * 3600)))
                its_point = np.array(round(sampling_rate * (UTCDateTime(row.its) - start_time - 8 * 3600)))
                tr3 = tr3.trim(start_time, start_time + input_length - 0.01, pad=True, fill_value=0)
                tr3.detrend('constant')
                # tr3.filter('bandpass', freqmin=1.0, freqmax=45, corners=2, zerophase=True)
                tr3.taper(max_percentage=0.001, type='cosine', max_length=2)
                data = np.array([tr.data for tr in tr3])
                data = standardize(data)
                statime_str = f"{net_sta}_{row.dayTime}"
                if statime_str in sta_dayTime:
                    evnbasic = evn.split('.')[0] + '.' + evn.split('.')[1]
                    evnum = sta_dayTime.count(statime_str) + 1
                    evn = '{}.{:0>4}'.format(evnbasic, evnum)
                    tn = f"{net}.{sta}_{evn}.npz"
                fname.append(tn)
                sta_id.append(staid_str)
                sta_dayTime.append(statime_str)
                channels = f'{tr3[0].stats.channel}_{tr3[1].stats.channel}_{tr3[2].stats.channel}'
                t0 = start_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
                np.savez(os.path.join(output_dir, 'waveform', tn),
                         data=data.transpose(), itp=itp_point, its=its_point, channels=channels, t0=t0, sta_id=net_sta)
                trn += 1
                output_writer.writerow([tn, itp_point, its_point, channels, evn, t0, net_sta])
                # print(itp_point)
                # if itp_point<3000:
                #     breakpoint()
                csv_file.flush()
    csv_file.close()


def standardize(data):
    std_data = np.std(data, axis=1, keepdims=True)
    data -= np.mean(data, axis=1, keepdims=True)
    assert (std_data.shape[0] == data.shape[0])
    std_data[std_data == 0] = 1
    data /= std_data
    return data
