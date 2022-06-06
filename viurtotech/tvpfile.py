import logging
from os import PathLike

from viurtotech import calc
from viurtotech.data import note_data


logger = logging.getLogger(__name__)

class TVPFile:
    def __init__(self, path: str | PathLike) -> None:
        self.bpmevents = []
        self.notes = []
        self._metadata = {}
        self.path = path
            

    # read the file from the provided section
    def read(self, *section: tuple[str]) -> None:
        with open(self.path, 'rt') as f:
            for current_pos, line in enumerate(f, start=1):
                self.current_pos = current_pos
                line = line.strip('\n;').split(':', 1)
                if line[0] == '#b' and 'bpm' in section:
                    self._read_bpm_event(line[1])
                elif line[0] == '#p' and 'note' in section:
                    self._read_note(line[1])
                elif (line[0].startswith('#') and line[0] not in ('#b', '#p')
                    and 'metadata' in section):
                    key = line[0].strip('#')
                    self._metadata[key] = line[1]

        if 'metadata' in section:
            self._prepare_metadata()
        if 'bpm' in section:
            self.bpmevents.sort(key=lambda x: x['pulse'])
            self._adjust_bpm()
        if 'note' in section:
            self.notes.sort(key=lambda x: x['pulse'])


    def _read_bpm_event(self, b: str) -> None:
        try:
            measure, bpm, timing = b.split(':')
            measure = int(measure)
            bpm = float(bpm)
            parts = len(timing) - 1
        except ValueError:
            logger.warning(f'Bad BPM change syntax at line {self.current_pos}, ignoring.')
            return

        if self.bps != self.orig_bps:
            bpm = calc.adjust_bpm(bpm, self.bps, self.orig_bps)

        for i, x in enumerate(timing):
            if x == '1':
                submeasure = i / parts
                pulse = calc.calc_pulse(measure, submeasure, self.bps)
                self.bpmevents.append(self._make_bpm_event(pulse, bpm))
        

    def _make_bpm_event(self, pulse: int, bpm: float) -> dict:
        return {
            'pulse': pulse,
            'bpm': bpm
        }


    def _read_note(self, p: str) -> None:
        try:
            measure, lane, timing = p.split(':')
            measure = int(measure)
            lane = int(lane) - 1    # 1-indexed to 0-indexed
            parts = len(timing) - 1
        except ValueError:
            logger.warning(f'Bad note syntax at line {self.current_pos}, ignoring.')
            return

        for i, type in enumerate(timing):
            if type == '-' or type == '0':
                continue

            submeasure = i / parts
            pulse = calc.calc_pulse(measure, submeasure, self.bps)
            end_of_scan = True if submeasure == 1 else False
            self.notes.append(self._make_note(type, pulse, lane, end_of_scan))


    def _make_note(self, type: str, pulse: int, lane: int, end_of_scan: bool) -> dict:
        return {
            'type': type,
            'pulse': pulse,
            'lane': lane,
            'end_of_scan': end_of_scan
        }


    def _prepare_metadata(self) -> None:
        self.title = self._metadata['title']
        self.artist = self._metadata['artist']
        self.genre = self._metadata['genre']
        self.creator = self._metadata['creator']
        self.pattern = self._metadata['pattern']
        self.measure = int(self._metadata['measure'])
        self.orig_bps = int(self._metadata['measure']) * 4
        self.bps = None
        self.level = int(self._metadata['level'])
        self.bpm = float(self._metadata['bpm'])


    def _adjust_bpm(self) -> None:
        if self.bps != self.orig_bps:
            self.bpm = calc.adjust_bpm(self.bpm, self.bps, self.orig_bps)



    # convert to techmania notes
    def convert_notes(self) -> None:
        self.tech_notes = []
        self.tech_holds = []
        self.tech_drags = []
        self._is_holding = [False, False, False, False]

        for note in self.notes:
            match note_data[note['type']]['type']:
                case a if 'hold_end' in a and self._is_holding[note['lane']]:
                    print('yo')
                    self._end_hold_note(note)
                case ['hold']:
                    self._make_tech_hold_note(note)
                case ['repeat', 'hold']:
                    pass
                case ['tap'] | ['repeat']:
                    self._make_tech_note(note)
                case ['chain'] | ['chain', 'end']:
                    self._make_tech_chain_note(note)
                case ['drag']:
                    pass
                case ['drag_end']:
                    pass


    def _make_tech_note(self, note: dict) -> None:
        note['type'] = note_data[note['type']]['tech_type']
        self.tech_notes.append(note)


    def _make_tech_chain_note(self, note: dict) -> None:
        # viur put chain notes in the same lane so we have to correct the lane first
        note['lane'] += note_data[note['type']]['offset']
        if note['lane'] >= 0:
            note['type'] = note_data[note['type']]['tech_type']
            self.tech_notes.append(note)
        else:
            measure = calc.calc_measure(note['pulse'], self.bps, note['end_of_scan'])
            logger.warning(f'Ignoring a chain note above lane 1 at measure {measure}.')

   
    def _make_tech_hold_note(self, note: dict) -> None:
        # make a 1 pulse hold note as a placeholder
        note['type'] = note_data[note['type']]['tech_type']
        note['duration'] = 1
        note['holding'] = True
        self.tech_holds.append(note)
        self._is_holding[note['lane']] = True


    def _end_hold_note(self, end: dict) -> None:
        if not self._is_holding[end['lane']]:
            logger.debug('_end_hold_note: _is_holding is False')
            return

        idx = None
        for i, note in enumerate(reversed(self.tech_holds)):
            if note['lane'] == end['lane'] and note['holding']:
                idx = -(i + 1)
                break
        if idx is None:
            logger.debug('_end_hold_note: cannot find idx')
        else:
            self.tech_holds[idx]['duration'] = end['pulse'] - self.tech_holds[idx]['pulse']
            self.tech_holds[idx]['holding'] = False
        self._is_holding[end['lane']] = False
