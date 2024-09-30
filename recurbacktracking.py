import random
import numpy as np

class Maze:
    def __init__(self, width, height):
        self.width = width // 2 * 2 + 1
        self.height = height // 2 * 2 + 1
        self.cells = np.full((self.height, self.width), True, dtype=bool)

    def set_path(self, x, y):
        self.cells[y][x] = False

    def set_wall(self, x, y):
        self.cells[y][x] = True

def create_maze(width, height, start_point, end_point, seed=None):
    start_x, start_y = round(start_point[0]), round(start_point[1])
    end_x, end_y = round(end_point[0]), round(end_point[1])
    width = (width // 2) * 2 + 1
    height = (height // 2) * 2 + 1

    if seed is not None:
        np.random.seed(seed)

    maze = Maze(width, height)
    # Set maze borders
    maze.set_wall(0, 0)
    maze.set_wall(width - 1, height - 1)

    # Recursive backtracking
    def visit(x, y):
        maze.set_path(x, y)
        directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < width and 0 < ny < height and maze.cells[ny][nx]:
                maze.set_wall((x + nx) // 2, (y + ny) // 2)
                visit(nx, ny)

    visit(1, 1)

    # Ensure the end point is accessible
    # maze.set_path(end_x, end_y)

    return maze

# Example usage with custom start and end points
start = [3, 1]
end = [2, 6]
my_custom_maze = create_maze(width=7, height=7,start_point=start, end_point=end)
print(my_custom_maze.cells)  # Display the custom maze (True: wall, False: path)
