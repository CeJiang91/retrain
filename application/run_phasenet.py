import os
import sys
import time

sys.path.append('../PhaseNet1014/phasenet')
from PhaseNet1014.phasenet import predict

root_path = '/home/jc/Data/GD/gd_test'
data_root = f'{root_path}/input_unfiltered_180s'
config = {
    'data_dir': f'{data_root}/mseed',
    'data_list': f'{data_root}/fname.csv',
    'batch_size': 20,
    'tp_prob': 0.3,
    'ts_prob': 0.3,
    'result_dir': f'{root_path}/test',
    'model_dir': '../PhaseNet1014/model/221117-172114',
    # 'model_dir': '../PhaseNet1014/model/190703-214543',
    'mode': 'pred',
    'format': 'mseed',
    'plot_figure': True
}
print('predicting...')
start = time.process_time()
os.system(f"python ../PhaseNet1014/phasenet/predict.py --model_dir={config['model_dir']} --data_list={config['data_list']} "
          f"--data_dir={config['data_dir']} --format=mseed --result_dir={config['result_dir']} --plot_figure")
end = time.process_time()
print(end - start)
