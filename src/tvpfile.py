import calc


class TVPFile:
    def __init__(self, path):
        self.bpmevents = []
        self.notes = []
        self.metadata = {}
        self.path = path
            

    # read the file, calculate pulse from the tvp format, prepare metadata
    def read(self):
        with open(self.path, 'rt') as f:
            for current_pos, line in enumerate(f, start=1):
                self.current_pos = current_pos
                line = line.strip('\n;')
                match line.split(':', 1):
                    case ['#b', value]:
                        self.read_bpm_event(value)
                    case ['#p', value]:
                        self.read_note(value)
                    case [key, value] if key.startswith('#'):
                        key = key.strip('#')
                        self.metadata[key] = value

        self.prepare_metadata()
        self.bpmevents.sort(key=lambda x: x['pulse'])
        self.notes.sort(key=lambda x: x['pulse'])


    def read_bpm_event(self, b):
        try:
            measure, bpm, timing = b.split(':')
        except:
            print(f'Bad BPM change syntax at line {self.current_pos}, ignoring.')
            return

        measure = int(measure)
        bpm = float(bpm)
        parts = len(timing) - 1

        for i, x in enumerate(timing):
            if x == '1':
                submeasure = i / parts
                pulse = calc.calc_pulse(measure, submeasure)
                self.bpmevents.append(self.make_bpm_event(pulse, bpm))
        

    def make_bpm_event(self, pulse, bpm):
        return {
            'pulse': pulse,
            'bpm': bpm
        }


    def read_note(self, p):
        try:
            measure, lane, timing = p.split(':')
        except:
            print(f'Bad note syntax at line {self.current_pos}, ignoring.')
            return

        measure = int(measure)
        lane = int(lane) - 1    # 1-indexed to 0-indexed
        parts = len(timing) - 1

        for i, type in enumerate(timing):
            if type == '-' or type == '0':
                continue

            submeasure = i / parts
            pulse = calc.calc_pulse(measure, submeasure)
            end_of_scan = True if submeasure == 1 else False
            self.notes.append(self.make_note(type, pulse, lane, end_of_scan))


    def make_note(self, type, pulse, lane, end_of_scan):
        return {
            'type': type,
            'pulse': pulse,
            'lane': lane,
            'end_of_scan': end_of_scan
        }

    def prepare_metadata(self):
        self.title = self.metadata['title']
        self.artist = self.metadata['artist']
        self.genre = self.metadata['genre']
        self.creator = self.metadata['creator']
        self.pattern = self.metadata['pattern']
        self.measure = int(self.metadata['measure'])
        self.bps = int(self.metadata['measure']) * 4
        self.level = int(self.metadata['level'])
        self.bpm = float(self.metadata['bpm'])



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
