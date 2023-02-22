import os
import sys
import time

sys.path.append('../PhaseNet1014/phasenet')

# root_path = '/home/jc/Data/GD/gd_test'
# data_root = f'{root_path}/input_unfiltered_180s'
root_path = '/home/jc/Data/GD/xfj_test'
data_root = f'{root_path}/xfj.testset'
config = {
    'data_dir': f'{data_root}/mseed',
    'data_list': f'{data_root}/fname.csv',
    'batch_size': 40,
    'tp_prob': 0.3,
    'ts_prob': 0.3,
    'result_dir': f'{root_path}/result',
    'model_dir': '../PhaseNet_old/model/model_epoch30',
    'mode': 'pred',
    'format': 'mseed',
    'plot_figure': False
}
print('predicting...')
start = time.process_time()
os.system(f"python ../PhaseNet1014/phasenet/predict.py --model_dir={config['model_dir']} "
          f"--data_list={config['data_list']} --data_dir={config['data_dir']} --format=mseed "
          f"--result_dir={config['result_dir']}")
end = time.process_time()
print(end - start)
