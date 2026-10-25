"""The native feature registry uses String.Split(','); it is not RFC CSV."""
import csv, io

WIDTH = 16

def repair(text):
    lines, changes = [], []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith(('#', 'ContainerId,')):
            lines.append(line)
            continue
        row = next(csv.reader([line]))
        assert 2 <= len(row) <= WIDTH, ('registry width', row[0], len(row))
        for i, value in enumerate(row):
            assert '\n' not in value and '\r' not in value
            if ',' in value:
                # Display descriptions are the only fields requiring repair.
                # Never silently rewrite resource names, IDs or expressions.
                assert i == 11, ('unsafe structural field', row[0], i)
                changes.append(dict(container=row[0], column=i,
                                    before=value, after=value.replace(',', ';')))
                row[i] = value.replace(',', ';')
        for value in row:
            assert '"' not in value, ('unsupported registry quote', row[0])
        fixed = ','.join(row)
        assert fixed.split(',') == row
        lines.append(fixed)
    return '\n'.join(lines), changes

def native_rows(text):
    return [line.strip().split(',') for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith(('#', 'ContainerId,'))]
