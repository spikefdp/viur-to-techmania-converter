from uuid import uuid4

from viurtotech.tvpfile import DragNote, HoldNote, Note, TVPFile


class TechFile:
    def __init__(self, tvpfile: TVPFile) -> None:
        self.version = '3'
        self.trackMetadata = {
        'guid': str(uuid4()),
        'title': tvpfile.title,
        'artist': tvpfile.artist,
        'genre': tvpfile.genre,
        'additionalCredits': '',
        'eyecatchImage': '',
        'previewTrack': '',
        'previewStartTime': 0.0,
        'previewEndTime': 0.0,
        'autoOrderPatterns': True
        }
        self.patterns: list[dict] = []


    def add_pattern(self, tvpfile: TVPFile) -> None:
        patternMetadata = {
            'guid': str(uuid4()),
            'patternName': tvpfile.pattern,
            'level': tvpfile.level,
            'controlScheme': 0,
            'playableLanes': 4,
            'author': tvpfile.creator,
            'backingTrack': '',
            'backImage': '',
            'bga': '',
            'bgaOffset': '',
            'waitForEndOfBga': True,
            'playBgaOnLoop': False,
            'firstBeatOffset': 0.0,
            'initBpm': tvpfile.bpm,
            'bps': tvpfile.bps
        }
        legacyRulesetOverride = {
            'timeWindows': [],
            'hpDeltaBasic': [],
            'hpDeltaChain': [],
            'hpDeltaHold': [],
            'hpDeltaDrag': [],
            'hpDeltaRepeat': [],
            'hpDeltaBasicDuringFever': [],
            'hpDeltaChainDuringFever': [],
            'hpDeltaHoldDuringFever': [],
            'hpDeltaDragDuringFever': [],
            'hpDeltaRepeatDuringFever': []
        }

        pattern = {
            'patternMetadata': patternMetadata,
            'legacyRulesetOverride': legacyRulesetOverride,
            'bpmEvents': tvpfile.bpmevents,
            'timeStops': [],
            'packedNotes': [self._pack_note(x) for x in tvpfile.tech_notes],
            'packedHoldNotes': [self._pack_note(x) for x in tvpfile.tech_holds],
            'packedDragNotes': [self._pack_note(x) for x in tvpfile.tech_drags]
        }
        self.patterns.append(pattern)


    def _pack_note(self, note: type[Note]) -> str | dict[str, str | list[str]]:
        # type, pulse lane
        values = [str(x) for x in (note.type, note.pulse, note.lane)]

        # duration
        if type(note) is HoldNote:
            values.append(str(note.duration))

        # extended format: volume, pan, end_of_scan
        if note.end_of_scan:
            values.insert(0, 'E')
            values.extend(('100', '0', '1'))

        # keysound
        values.append('')
        
        packedNote = '|'.join(values)

        if type(note) is DragNote:
            packedNodes = [
                '0|0|0|0|0|0',
                f'{note.duration}|{note.direction}|0|0|0|0'
            ]
            return {'packedNote': packedNote, 'packedNodes': packedNodes}
        else:
            return packedNote