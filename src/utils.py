def load_sql(fname):
    with open(fname, 'r') as sql_f:
        lines = [l.rstrip() for l in sql_f.readlines()]

    res = {}
    name = ''
    for line in lines:
        if line.startswith('@'):
            name = line[1:]
            query = []
        elif line.endswith(';'):
            query.append(line)
            res[name] = '\n'.join(query)
        else:
            query.append(line)
    return res
