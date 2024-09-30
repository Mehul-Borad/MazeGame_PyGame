
import numpy as np

class Ray:
    walls = []
    def __init__(self, interval : int = 10):
        self.interval = interval
        pass
    def go(self, pos, dir, player, length = None):
        if length is None:
            length = np.linalg.norm(dir)
        self.player = player
        self.dir = dir/np.linalg.norm(dir)
        self.pos = np.array(pos)
        player_collision = False
        func = np.vectorize(lambda x, y : self.player.rect.collidepoint(x, y))
        poses = self.pos[np.newaxis, :] + np.arange(0, length, self.interval)[:, np.newaxis]*self.dir[np.newaxis, :]
        if poses.size == 0:
            return True, player, 1
        player_collision = np.any(func(poses[:, 0], poses[:, 1]))
        func = np.vectorize(lambda s, x, y : s.rect.collidepoint(x, y))
        if player_collision:
            for sprite in Ray.walls:
                if np.any(func(sprite, poses[:, 0], poses[:, 1])):
                    return True, sprite, 0
            return True, player, 1
        return False, None, None