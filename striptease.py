import os
import re
import sys
import subprocess


FIELD_RE = re.compile('[ \t]+')

SECTIONS = ['.pdr', '.comment', '.note']

def is_elf(filename):
    r = False
    try:
        with open(filename) as f:
            r = f.read(4) == '\x7fELF'
    except IOError:
        pass

    return r


def calc_savings_file(filename):
    if not is_elf(filename):
        return 0
    total = 0
    try:
        output = subprocess.check_output(['objdump', '-hw', filename])
        for line in output.splitlines():
            fields = FIELD_RE.split(line)
            if len(fields) > 4 and fields[2] in SECTIONS:
                total += int(fields[3], 16)
    except subprocess.CalledProcessError:
        return 0
    return total


def calc_savings(path):
    total = 0
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for f in files:
                filename = os.path.join(root, f)
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
    paths = []

    if len(sys.argv) == 1:
        paths.append('.')
    else:
        paths.extend(sys.argv[1:])

    total = 0
    for path in paths:
        total += calc_savings(path)

    print('Potential savings from stipper are %s' % human_size(total))


if __name__ == '__main__':
    main()
