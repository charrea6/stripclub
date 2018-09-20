import argparse
import os
import re
import subprocess


FIELD_RE = re.compile('[ \t]+')

SECTIONS = ['.pdr', '.comment', '.note']

verbosity = 0


def print_v(v, str, *args):
    if verbosity >= v:
        print(str % args)


def is_elf(filename):
    r = False
    try:
        with open(filename, 'rb') as f:
            r = f.read(4) == b'\x7fELF'
    except IOError:
        pass

    return r


def calc_savings_file(filename):
    if not is_elf(filename):
        return 0
    total = 0
    try:
        output = subprocess.check_output(['objdump', '-hw', filename]).decode('utf8')
        for line in output.splitlines():
            fields = FIELD_RE.split(line)
            if len(fields) > 4 and fields[2] in SECTIONS:
                section_size = int(fields[3], 16)
                print_v(2, '%s section %s size %d bytes', filename, fields[2], section_size)
                total += section_size
    except subprocess.CalledProcessError:
        return 0
    print_v(1, '%s savings %d bytes', filename, total)
    return total


def calc_savings(path):
    total = 0
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for f in files:
                filename = os.path.join(root, f)
                if not os.path.islink(filename):
                    total += calc_savings_file(filename)
    elif os.path.isfile(path):
        total = calc_savings_file(path)
    return total


def human_size(s):
    unit = [(0, 'bytes'), (1024, 'KiB'), (1024*1024, 'MiB'), (1024*1024*1024, 'GiB'), (1024*1024*1024*1024, 'TiB')]
    selected = None
    for u in unit:
        if s < u[0]:
            break
        selected = u

    if selected[0]:
        m = '%.1f' % (s / float(selected[0]))
        if m.endswith('.0'):
            m = m[:-2]
        return '%s %s (%d bytes)' % (m, selected[1], s)
    return '%d bytes' % s


def main():
    global verbosity
    paths = []

    parser = argparse.ArgumentParser(description='''Simple tool to show you potential file size savings if ELF sections, 
    not used during the running of a program, are removed''')
    parser.add_argument('paths', metavar='path', type=str, nargs='*', help="Directory or file to scan for savings")
    parser.add_argument('--verbose','-v', action='count', help='increase the verbosity of the program')

    args = parser.parse_args()
    verbosity = args.verbose
    if len(args.paths) == 0:
        paths.append('.')
    else:
        paths.extend(args.paths)

    total = 0
    for path in paths:
        total += calc_savings(path)

    print('Potential savings from stipper are %s' % human_size(total))


if __name__ == '__main__':
    main()
