import sys
import logging
import argparse
import os
from jvd import ida_available, get_disassembler, process_folder
from jvd.installer import make
from tqdm import tqdm
from jvd.utils import grep_ext
from shutil import rmtree

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
    handlers=[
        logging.StreamHandler()
    ])

ida = ida_available
if not ida:
    logging.info('IDA is not available. Will use Ghidra instead.')


is_src_dir = os.path.exists('setup.py')


def entry_point():

    parser = argparse.ArgumentParser(
        usage='jvd <file> [options]',
    )
    parser.add_argument(
        'file',
        nargs='?',
        help='The binary file or the targeted path.'
    )
    disassember = 'ghidra' if not ida else 'ida'
    disassemblers = ['ghidra'] if not ida else ['ida', 'ghidra']
    parser.add_argument(
        '--dis',
        choices=disassemblers,
        default=disassember,
        help='The disassembler'
    )
    parser.add_argument(
        '--ext',
        default=None,
        help='If the input is a folder, the file extension to include. Default is all the files. '
        'Empty string will select files without any `.`.'
    )
    parser.add_argument(
        '--disassemble', dest='disassemble',
        action='store_true', help='Disassemble all the applicable files.')
    parser.add_argument(
        '--unpack', dest='unpack',
        action='store_true', help='Unpack before disassembling.')
    parser.add_argument(
        '--capa', dest='capa',
        action='store_true', help='Analyze by capa')
    parser.add_argument(
        '--cleanup', dest='cleanup',
        action='store_true', help='Clean up the temporary folders')
    parser.add_argument(
        '--decompile', dest='decompile',
        action='store_true',
        help='Decomiple the code (if IDA is chosen as disassembler, it will use Ghidra to decompile and merge.')
    parser.add_argument(
        '--verbose', dest='verbose',
        type=int, choices=range(-1, 3), default=-1)
    if is_src_dir:
        parser.add_argument(
            '--make', dest='make',
            action='store_true',
            help='Make the installer for offline usage.')
    flags = parser.parse_args()

    if is_src_dir and flags.make:
        make()
    elif flags.cleanup:
        folders = grep_ext(flags.file, '.tmp', type='d')
        for f in tqdm(folders):
            try:
                rmtree(f)
            except Exception as e:
                print(str(e), ':::', f)
    else:
        if flags.dis is not None:
            disassembler = flags.dis
        f = flags.file
        if not f:
            logging.error('You have to supply at least a file or a path.')
        else:
            process_folder(
                f, capa=flags.capa, decompile=flags.decompile,
                clean_up=False, ext=flags.ext, disassembler=disassembler,
                verbose=flags.verbose, disassemble=flags.disassemble,
                unpack=flags.unpack,
            )


if __name__ == "__main__":
    entry_point()
