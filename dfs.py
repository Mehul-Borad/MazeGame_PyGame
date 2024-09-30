import random
import time
import numpy as np

def get_neighbours(p : np.ndarray, maze : np.ndarray):
        points = []
        keys = []
        if maze[p[0], p[1] + 1]:
            points.append([p[0], p[1] + 1])
            keys.append('R')
        if maze[p[0], p[1] - 1]:
            points.append([p[0], p[1] - 1])
            keys.append('L')
        if maze[p[0]  + 1, p[1]]:
            points.append([p[0] + 1, p[1]])
            keys.append('D')
        if maze[p[0] - 1, p[1]]:
            points.append([p[0]- 1, p[1] ])
            keys.append('U')
        return zip(np.array(points), np.array(keys))

def pointin(p : np.ndarray, points : np.ndarray):
        return (points == p).all(1).any(0)

def dfs_solve(start : np.ndarray, end : np.ndarray, maze, seqp, seqk):
    if (start == end).all():
        return seqp, seqk
    for p, key in (get_neighbours(start, maze)):
        if not pointin(p, seqp):
            newseq = list(seqp)
            newseq.append(p)
            newseqk = list(seqk)
            newseqk.append(key)
            res = dfs_solve(p, end, maze, np.array(newseq), np.array(newseqk))
            if res is not None:
                return res
    return None
        