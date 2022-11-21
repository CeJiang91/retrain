import sys
import time
import os

sys.path.append('../PhaseNet1014/phasenet')
from PhaseNet1014.phasenet import train

root_path = '/home/jc/Data/GD/gd_train'
config = {
    'train_dir': f'{root_path}/gd.npz_phasenet/waveform',
    'train_list': f'{root_path}/gd.npz_phasenet/waveform_new.csv',
    'batch_size': 200,
    'epochs': 10
}
print('training..')
start = time.process_time()
os.system(f'python ../PhaseNet1014/phasenet/train.py --mode=train --train_list={config["train_list"]} '
          f'--train_dir={config["train_dir"]} --epochs={config["epochs"]} --batch_size={config["batch_size"]}')
end = time.process_time()
print(end - start)
