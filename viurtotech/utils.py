from logging import Logger, getLogger

from viurtotech.config import pulse_per_beat


def calc_pulse(measure: int, submeasure: float, bps: int) -> int:
    return round(bps * (measure+submeasure) * pulse_per_beat)


def calc_measure(pulse: int, bps: int, end_of_scan: bool) -> int:
    return int(pulse / bps / pulse_per_beat) - int(end_of_scan)


def adjust_bpm(bpm: float, targ_bps: int, orig_bps: int) -> float:
    return round((targ_bps/orig_bps) * bpm, 3)


def make_logger(*args) -> Logger:
    return getLogger(':'.join(str(a) for a in args))