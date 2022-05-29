from viurtotech import config


def calc_pulse(measure, submeasure, targ_bps):
    return round(targ_bps * (measure+submeasure) * config.pulse_per_beat)


def calc_measure(pulse, targ_bps):
    return round(pulse / targ_bps / config.pulse_per_beat)


def adjust_bpm(bpm, targ_bps, orig_bps):
    if targ_bps == orig_bps:
        return bpm
    else:
        return round((targ_bps/orig_bps) * bpm, 3)
