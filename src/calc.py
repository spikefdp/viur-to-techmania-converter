from pathlib import Path

import yaml

from config import Config



def calc_pulse(measure: int, submeasure: float) -> int:
    print(Config.bps)
    return round(Config.bps * (measure+submeasure) * Config.pulse_per_beat)


def calc_measure(pulse: int) -> int:
    return round(pulse/Config.bps/Config.pulse_per_beat)


def adjust_bpm(bpm):
    viur_bps = int(metadata['measure']) * 4
    if Config.bps == viur_bps:
        return bpm
    else:
        return round((Config.bps/viur_bps) * bpm)
