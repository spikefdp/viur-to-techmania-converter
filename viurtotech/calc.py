from viurtotech import config


def calc_pulse(measure: int, submeasure: float, bps: int) -> int:
    return round(bps * (measure+submeasure) * config.pulse_per_beat)


def calc_measure(pulse: int, bps: int, end_of_scan: bool) -> int:
    return int(pulse / bps / config.pulse_per_beat) - int(end_of_scan)


def adjust_bpm(bpm: float, targ_bps: int, orig_bps: int) -> float:
    return round((targ_bps/orig_bps) * bpm, 3)
