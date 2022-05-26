from pathlib import Path

import yaml


class Config:
    @staticmethod
    def load():
        file = Path('config.yaml')
        with file.open('rt') as f:
            Config.conf = yaml.safe_load(f)

        Config.bps = Config.conf['bps']
        Config.pulse_per_beat = Config.conf['pulse_per_beat']