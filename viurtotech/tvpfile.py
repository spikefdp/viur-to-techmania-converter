from dataclasses import dataclass
from pathlib import Path

from viurtotech import utils
from viurtotech.data import note_data


@dataclass
class Note:
    type: str
    measure: int
    pulse: int
    lane: int
    end_of_scan: bool

    def to_hold_note(self, **kwargs):
        return HoldNote(self.type, self.measure, self.pulse,
                        self.lane, self.end_of_scan, **kwargs)

    def to_drag_note(self, **kwargs):
        return DragNote(self.type, self.measure, self.pulse,
                        self.lane, self.end_of_scan, **kwargs)


@dataclass
class HoldNote(Note):
    duration: int = 1
    holding: bool = True


@dataclass
class DragNote(Note):
    duration: int = 1
    direction: int = 0
    dragging: bool = True


class TVPFile:
    def __init__(self, path: Path) -> None:
        self.bpmevents: list[dict] = []
        self.notes: list[Note] = []
        self._metadata = {}
        self.path = path

            
    # read the file from the provided section
    def read(self, *section: str) -> None:
        with open(self.path, 'rt') as f:
            for current_pos, line in enumerate(f, start=1):
                self._current_pos = current_pos
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
            self.notes.sort(key=lambda x: x.lane)
            self.notes.sort(key=lambda x: x.pulse)


    def _read_bpm_event(self, b: str) -> None:
        logger = utils.make_logger(self.path.name, '_read_bpm_event')

        try:
            measure, bpm, timing = b.split(':')
            measure = int(measure)
            bpm = float(bpm)
            parts = len(timing) - 1
        except ValueError:
            logger.warning(f'Bad BPM change syntax at line {self._current_pos}, ignoring.')
            return

        if self.bps != self.orig_bps:
            bpm = utils.adjust_bpm(bpm, self.bps, self.orig_bps)

        for i, x in enumerate(timing):
            if x == '1':
                submeasure = i / parts
                pulse = utils.calc_pulse(measure, submeasure, self.bps)
                self.bpmevents.append(self._make_bpm_event(pulse, bpm))
        

    def _make_bpm_event(self, pulse: int, bpm: float) -> dict:
        return {
            'pulse': pulse,
            'bpm': bpm
        }


    def _read_note(self, p: str) -> None:
        logger = utils.make_logger(self.path.name, '_read_note')

        try:
            measure, lane, timing = p.split(':')
            measure = int(measure)
            lane = int(lane) - 1    # 1-indexed to 0-indexed
            parts = len(timing) - 1
        except ValueError:
            logger.warning(f'Bad note syntax at line {self._current_pos}, ignoring.')
            return

        for i, type in enumerate(timing):
            if type == '-' or type == '0':
                continue
            submeasure = i / parts
            pulse = utils.calc_pulse(measure, submeasure, self.bps)
            end_of_scan = True if submeasure == 1 else False
            self.notes.append(Note(type, measure, pulse, lane, end_of_scan))


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
            self.bpm = utils.adjust_bpm(self.bpm, self.bps, self.orig_bps)


    # convert to techmania notes
    def convert_notes(self) -> None:
        self.tech_notes: list[Note] = []
        self.tech_holds: list[HoldNote] = []
        self.tech_drags: list[DragNote] = []
        self._is_holding = [False, False, False, False]
        self._is_dragging = [False, False, False, False]

        for note in self.notes:
            match note_data[note.type]['type']:
                case a if 'hold_end' in a and self._is_holding[note.lane]:
                    self._end_hold_note(note)
                case a if 'hold' in a:
                    self._make_tech_hold_note(note)
                case a if 'tap' in a or 'repeat' in a:
                    self._make_tech_note(note)
                case a if 'chain' in a:
                    self._make_tech_chain_note(note)
                case ['drag']:
                    self._make_tech_drag_note(note)
                case ['drag_end']:
                    self._end_drag_note(note)


    def _make_tech_note(self, note: Note) -> None:
        note.type = note_data[note.type]['tech_type']
        self.tech_notes.append(note)


    def _make_tech_chain_note(self, note: Note) -> None:
        # viur put chain notes in the same lane so we have to correct the lane first
        logger = utils.make_logger(self.path.name, '_make_tech_chain_note', note.measure)

        note.lane += note_data[note.type]['offset']
        if note.lane >= 0:
            note.type = note_data[note.type]['tech_type']
            self.tech_notes.append(note)
        else:
            logger.warning('Ignoring a chain note above the top lane.')

   
    def _make_tech_hold_note(self, note: Note) -> None:
        # make a 1 pulse hold note as a placeholder
        # -> set the hold flags for the current lane
        note = note.to_hold_note()
        note.type = note_data[note.type]['tech_type']
        self.tech_holds.append(note)
        self._is_holding[note.lane] = True


    def _end_hold_note(self, end: Note) -> None:
        # check whether the current lane is holding
        # -> calculate hold duration by subtracting end pulse from head pulse 
        # -> set the hold flags back to False
        logger = utils.make_logger(self.path.name, '_end_hold_note', end.measure, end.lane)

        if not self._is_holding[end.lane]:
            logger.debug('current lane\'s _is_holding is False')
            return

        gen = (n for n in reversed(self.tech_holds) if n.lane == end.lane and n.holding)
        hold_head = next(gen, None)
        if hold_head is None:
            self.logger.debug('cannot find idx')
        else:
            hold_head.duration = end.pulse - hold_head.pulse
            hold_head.holding = False
        self._is_holding[end.lane] = False

    
    def _make_tech_drag_note(self, note: Note) -> None:
        # make a 1 pulse drag note as a placeholder
        # -> set the drag flags for the current lane
        note = note.to_drag_note()
        note.type = note_data[note.type]['tech_type']
        self.tech_drags.append(note)
        self._is_dragging[note.lane] = True

    
    def _end_drag_note(self, end: Note) -> None:
        # find the topmost lane that started dragging
        # -> calculate hold duration by subtracting end pulse from head pulse
        # -> calculate direction by subtraction end lane from head lane
        # -> set the hold flags back to False
        logger = utils.make_logger(self.path.name, '_end_drag_note', end.measure, end.lane)

        if True not in self._is_dragging:
            logger.debug('No dragging lane found.')
            return
        start_lane = self._is_dragging.index(True)

        gen = (n for n in reversed(self.tech_drags) if n.lane == start_lane and n.dragging)
        drag_head = next(gen, None)
        if drag_head is None:
            logger.debug('Cannot find drag head.')
        else:
            drag_head.duration = end.pulse - drag_head.pulse
            drag_head.direction = end.lane - start_lane
            drag_head.dragging = False
        self._is_dragging[start_lane] = False
