import os
import sys
import logging

from tvpread import tvpread



if __name__ == '__main__':

    logging.basicConfig(filename = 'convert.log', filemode = 'wt', encoding = 'utf-8', level = logging.DEBUG)

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

    logging.info(notes)

    print('Done!')