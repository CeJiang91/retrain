from app_util import mseed2testset,sac2testset

root_path = '/home/jc/Data/GD/xfj_test'
config = {
    'input_dir': f'{root_path}/xfj.sac',
    'testset_dir': f'{root_path}/xfj.testset',
}
# mseed2testset(config['mseed_dir'], config['testset_dir'], sta_list=None, data_period=180)
sac2testset(config['input_dir'], config['testset_dir'], sta_list=None, data_period=6*3600)