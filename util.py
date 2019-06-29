


import sys

def log(*objects, sep=' ', end='\n', file=sys.stdout, flush=True):
    print(*objects, sep=sep, end=end, file=file, flush=flush)
