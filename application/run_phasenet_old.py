import os
import sys
import time

sys.path.append('../PhaseNet_old')
from PhaseNet_old import run

# root_path = '/home/jc/Data/GD/gd_test'
# data_root = f'{root_path}/input_unfiltered_180s'
root_path = '/home/jc/Data/GD/xfj_test'
data_root = f'{root_path}/xfj.testset'
config = {
    'data_dir': f'{data_root}/mseed',
    'data_list': f'{data_root}/fname.csv',
    'batch_size': 20,
    'tp_prob': 0.3,
    'ts_prob': 0.3,
    'result_dir': f'{root_path}/result',
    'model_dir': '../PhaseNet_old/model/model_epoch30',
    # 'model_dir': '../PhaseNet1014/model/190703-214543',
    'mode': 'pred',
    'format': 'mseed',
    'plot_figure': True
}
print('predicting...')
start = time.process_time()
os.system(f"python ../PhaseNet_old/run.py --mode=pred --model_dir={config['model_dir']}  --batch_size={config['batch_size']}"
          f" --input_mseed --ts_prob={config['ts_prob']} --tp_prob={config['tp_prob']} --data_dir={config['data_dir']}"
          f" --data_list={config['data_list']} --output_dir={config['result_dir']}")
end = time.process_time()
print(end - start)
