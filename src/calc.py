from config import Config


def calc_pulse(measure: int, submeasure: float) -> int:
    return round(Config.bps * (measure+submeasure) * Config.pulse_per_beat)


def calc_measure(pulse: int) -> int:
    return round(pulse/Config.bps/Config.pulse_per_beat)


def adjust_bpm(bpm: float, measure: int) -> float:
    viur_bps = measure * 4
    if Config.bps == viur_bps:
        return bpm
    else:
        return round((Config.bps/viur_bps) * bpm, 3)
