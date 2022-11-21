import sys
import time
import os

sys.path.append('../PhaseNet_old')
from PhaseNet_old import run

root_path = '/home/jc/Data/GD/gd_train'
config = {
    'train_dir': f'{root_path}/gd.npz_phasenet/waveform',
    'train_list': f'{root_path}/gd.npz_phasenet/waveform.csv',
    'batch_size': 20,
    'epochs': 10
}
print('old PhaseNet training..')
start = time.process_time()
os.system(f'python ../PhaseNet_old/run.py --mode=train --train_list={config["train_list"]} '
          f'--train_dir={config["train_dir"]} --epochs={config["epochs"]} --batch_size={config["batch_size"]}')
end = time.process_time()
print(end - start)

# args = run.read_args()
# run.main(args)
