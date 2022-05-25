import sys
import os
import logging
import yaml



# load config
with open('config.yaml', 'rt') as c:
    config = yaml.safe_load(c)



def tvpread(filename):
    bpm_events = []
    notes = []
    metadata = {}

    with open(filename, 'rt') as f:
        for line in f:
            line = line.strip('\n;')
            match line.split(':', 1):
                case ['#b', value]:
                    bpm_events += to_bpm_event(value)
                case ['#p', value]:
                    notes += to_note(value)
                case [key, value] if key.startswith('#'):
                    key = key.strip('#')
                    metadata[key] = value

    bpm_events.sort(key=lambda x: x['bpm'])
    notes.sort(key=lambda x: x['pulse'])
    return bpm_events, notes, metadata



def calc_pulse(measure, submeasure):
    return round(config['bps'] * (measure + submeasure) * config['pulse_per_beat'])


def calc_measure(pulse):
    return round(pulse / config['bps'] / config['pulse_per_beat'])


def adjust_bpm(bpm):
    viur_bps = int(metadata['measure']) * 4
    if config['bps'] == viur_bps:
        return bpm
    else:
        return round((config['bps'] / viur_bps) * bpm)



def to_bpm_event(b):
    measure, bpm, timing = b.split(':')
    measure = int(measure)
    bpm = float(bpm)
    parts = len(timing) - 1

    result = []
    for i, x in enumerate(timing):
        if x == '1':
            submeasure = i / parts
            pulse = calc_pulse(measure, submeasure)
            result.append(make_bpm_event(pulse, bpm))
    return result


def make_bpm_event(pulse, bpm):
    return {
        'pulse': pulse,
        'bpm': bpm
    }



def to_note(p):
    measure, lane, timing = p.split(':')
    measure = int(measure)
    lane = int(lane) - 1    # 1-indexed to 0-indexed
    parts = len(timing) - 1

    result = []
    for i, type in enumerate(timing):
        if type == '-' or type == '0':
            continue

        submeasure = i / parts
        pulse = calc_pulse(measure, submeasure)
        end_of_scan = True if submeasure == 1 else False
        result.append(make_note(type, pulse, lane, end_of_scan))
    return result


def make_note(type, pulse, lane, end_of_scan):
    return {
        'type': type,
        'pulse': pulse,
        'lane': lane,
        'end_of_scan': end_of_scan
    }




#         match note_data[type]['type']:
#             case a if 'hold_end' in a:
#                 pass
#             case ['hold']:
#                 pass
#             case ['repeat', 'hold']:
#                 pass
#             case ['tap'] | ['repeat']:
#                 notes.append(to_note(type, pulse, lane, end_of_scan))
#             case ['chain'] | ['chain', 'end']:
#                 notes.append(to_chain_note(type, pulse, lane, end_of_scan))
#             case ['drag']:
#                 pass
#             case ['drag_end']:
#                 pass



# def make_note(type, pulse, lane, end_of_scan):
#     tech_type = note_data[type]['tech_type']
#     return {
#         'type': tech_type,
#         'pulse': pulse,
#         'lane': lane,
#         'end_of_scan': end_of_scan
#     }


# def to_note(type, pulse, lane, end_of_scan):
#     return make_note(type, pulse, lane, end_of_scan)


# def to_chain_note(type, pulse, lane, end_of_scan):
#     # viur put chain notes in the same lane so we have to correct the lane first
#     lane += note_data[type]['offset']
#     if lane < 0:
#         measure = calc_measure(pulse) - 1 if end_of_scan else calc_measure(pulse)
#         logging.warning(f'Ignoring a chain note above lane 1 at measure {measure}.')
#     return make_note(type, pulse, lane, end_of_scan)


# def to_hold_note(type, pulse, lane, end_of_scan):
#     count_hold('start')


# def count_hold(action):
    

    
    



if __name__ == '__main__':

    logging.basicConfig(filename='convert.log', filemode='wt', encoding='utf-8', level=logging.DEBUG)

    match len(sys.argv):
        case 2:
            pass
        case 3:
            pass
        case _:
            print('Usage:')

    listdir = os.listdir('.')
    tvp_files = [x for x in listdir if os.path.splitext(x)[1] == '.tvp']

    input_filename = tvp_files[0]

    bpm_events, notes, metadata = tvpread(input_filename)

    notes.sort(key=lambda x: x['pulse'])

    logging.info(notes)

    print('Done!')