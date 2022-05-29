from typing import Dict, Tuple

from click import secho

from viurtotech import calc


class TVPFile:
    def __init__(self, path):
        self.bpmevents = []
        self.notes = []
        self._metadata = {}
        self.path = path
            

    # read the file from the provided section
    def read(self, *section: Tuple[str]):
        with open(self.path, 'rt') as f:
            for current_pos, line in enumerate(f, start=1):
                self.current_pos = current_pos
                line = line.strip('\n;').split(':', 1)
                if line[0] == '#b' and 'bpm' in section:
                    self.read_bpm_event(line[1])
                elif line[0] == '#p' and 'note' in section:
                    self.read_note(line[1])
                elif (line[0].startswith('#') and line[0] not in ('#b', '#p')
                    and 'metadata' in section):
                    key = line[0].strip('#')
                    self._metadata[key] = line[1]

        if 'metadata' in section:
            self.prepare_metadata()
        if 'bpm' in section:
            self.bpmevents.sort(key=lambda x: x['pulse'])
            self.adjust_bpm()
        if 'note' in section:
            self.notes.sort(key=lambda x: x['pulse'])


    def read_bpm_event(self, b: str):
        try:
            measure, bpm, timing = b.split(':')
            measure = int(measure)
            bpm = float(bpm)
            parts = len(timing) - 1
        except ValueError:
            secho(f'Bad BPM change syntax at line {self.current_pos}, ignoring.',
                err=True, fg='yellow')
            return

        if self.targ_bps != self.orig_bps:
            bpm = calc.adjust_bpm(bpm, self.targ_bps, self.orig_bps)

        for i, x in enumerate(timing):
            if x == '1':
                submeasure = i / parts
                pulse = calc.calc_pulse(measure, submeasure, self.targ_bps)
                self.bpmevents.append(self.make_bpm_event(pulse, bpm))
        

    def make_bpm_event(self, pulse: int, bpm: float) -> Dict:
        return {
            'pulse': pulse,
            'bpm': bpm
        }


    def read_note(self, p: str):
        try:
            measure, lane, timing = p.split(':')
            measure = int(measure)
            lane = int(lane) - 1    # 1-indexed to 0-indexed
            parts = len(timing) - 1
        except ValueError:
            secho(f'Bad note syntax at line {self.current_pos}, ignoring.',
                err=True, fg='yellow')
            return

        for i, type in enumerate(timing):
            if type == '-' or type == '0':
                continue

            submeasure = i / parts
            pulse = calc.calc_pulse(measure, submeasure, self.targ_bps)
            end_of_scan = True if submeasure == 1 else False
            self.notes.append(self.make_note(type, pulse, lane, end_of_scan))


    def make_note(self, type: str, pulse: int, lane: int, end_of_scan: bool) -> Dict:
        return {
            'type': type,
            'pulse': pulse,
            'lane': lane,
            'end_of_scan': end_of_scan
        }


    def prepare_metadata(self):
        self.title = self._metadata['title']
        self.artist = self._metadata['artist']
        self.genre = self._metadata['genre']
        self.creator = self._metadata['creator']
        self.pattern = self._metadata['pattern']
        self.measure = int(self._metadata['measure'])
        self.orig_bps = int(self._metadata['measure']) * 4
        self.targ_bps = None
        self.level = int(self._metadata['level'])
        self.bpm = float(self._metadata['bpm'])


    def adjust_bpm(self):
        if self.targ_bps != self.orig_bps:
            self.bpm = calc.adjust_bpm(self.bpm, self.targ_bps, self.orig_bps)



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
