from app_util import bulletins2picks, mseed2trainset

root_path = '/home/jc/Data/GD/gd_train'
config = {
    'bulletins_dir': f'{root_path}/bulletins',
    'mseed_dir': f'{root_path}/gd.seed',
    'npz_dir': f'{root_path}/gd.npz_phasenet',
    'picks': f'{root_path}/others/manual_picks.csv'
}
# bulletins2picks(config['bulletins_dir'], config['picks'])
mseed2trainset(input_dir=config['mseed_dir'], output_dir=config['npz_dir'], picks_file=config['picks'])
