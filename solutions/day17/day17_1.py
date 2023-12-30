from __future__ import annotations
from handy_dandy_library.file_processing import read_lines
from handy_dandy_library.string_manipulations import pad_with_horizontal_rules, make_blue

type Grid = list[list[int]]


class UnitVector:
    UNIT_VECTOR_CODENAMES = {"up": 0, "right": 1, "down": 2, "left": 3}
    UNIT_VECTOR_NAMES_FROM_VECTOR = {(1, 0): "right", (0, 1): "down", (-1, 0): "left", (0, -1): "up"}

    def __init__(self, values: tuple[int, int]):
        self.x = values[0]
        self.y = values[1]
        self.direction_name = self.UNIT_VECTOR_NAMES_FROM_VECTOR.get(values, "not_unit_vector")

    def __eq__(self, other: UnitVector) -> bool:
        return self.x == other.x and self.y == other.y

    def __repr__(self) -> str:
        return f"({self.x},{self.y})"

    @classmethod
    def UP(cls):
        return cls((0, -1))

    @classmethod
    def RIGHT(cls):
        return cls((1, 0))

    @classmethod
    def DOWN(cls):
        return cls((0, 1))

    @classmethod
    def LEFT(cls):
        return cls((-1, 0))


class Vector(UnitVector):
    def __init__(self, values: tuple[int, int]):
        super().__init__(values)

    def __add__(self, other: Vector) -> Vector:
        return Vector((self.x + other.x, self.y + other.y))

    def __sub__(self, other: Vector) -> Vector:
        return Vector((self.x - other.x, self.y - other.y))

    @classmethod
    def zero(cls):
        return cls((0, 0))

    @property
    def rotated_right(self) -> Vector:
        return Vector((self.y * -abs(self.y), self.x))

    @property
    def rotated_left(self) -> Vector:
        return Vector((self.y, self.x * -abs(self.x)))

    def manhattan_distance(self, other: Vector) -> int:
        return abs(self.x - other.x, self.y - other.y)


class Square:
    def __init__(self, coordinate: Vector, distance_to_end_node: int, heat_loss: int, parent: Square = None):
        self.coordinate = coordinate
        self.parent = parent
        self.distance_to_end_node = distance_to_end_node

        self.heat_loss = heat_loss
        self.forward_direction = Vector.zero()
        self.forwards_count = 0
        if parent is not None:
            self.heat_loss = heat_loss + parent.heat_loss
            self.forward_direction = coordinate - parent.coordinate
            if parent.forward_direction == self.forward_direction:
                self.forwards_count = self.parent.forwards_count + 1

    def __eq__(self, other: Square) -> bool:
        return self.coordinate == other.coordinate and self.forwards_count == other.forwards_count

    def __repr__(self) -> str:
        return f"{make_blue("Sqr")}({self.coordinate}, (g, h, f): ({self.heat_loss},{self.distance_to_end_node},{self.f}))"

    @property
    def f(self) -> int:
        return self.heat_loss + self.distance_to_end_node

    def path_to_root_parent(self) -> list[Vector]:
        parent = self.parent
        path = [self]
        while parent is not None:
            path.append(parent)
            parent = parent.parent
        return list(reversed(path))

    def is_valid_next(self, next_coordinate: Vector) -> bool:
        if self.parent is None:
            return True
        direction = next_coordinate - self.coordinate
        return self.forward_direction != direction or self.forwards_count != 2


class LavaGrid:
    def __init__(self, grid: Grid):
        self.grid = grid

        self.n = len(grid)
        self.m = len(grid[0])
        print(f"Grid size: ({self.m}, {self.n})")
        self.distances_to_end_node = self.__distances_to_end_node(grid)

    def __edge_checks(self, coordinate: Vector) -> (bool, bool, bool, bool):
        return coordinate.x > 0, coordinate.y > 0, coordinate.y < self.m - 1, coordinate.x < self.n - 1

    def __repr__(self) -> str:
        lines = '\n'.join(['\t' + ''.join(str(char) for char in line) for line in self.grid])
        return pad_with_horizontal_rules(lines)

    @staticmethod
    def __distances_to_end_node(grid) -> list[list[int]]:
        m = len(grid[0])
        n = len(grid)
        return [[m - j + n - i - 2 for j in range(m)] for i in range(n)]

    @classmethod
    def from_lines(cls, lines: list[str]):
        grid = [[int(char) for char in line] for line in lines]
        return cls(grid)

    def is_inside_bounds(self, coordinate: Vector) -> bool:
        return 0 <= coordinate.x <= self.n and 0 <= coordinate.y <= self.m

    def potential_squares(self, square: Square) -> list[Square]:
        previous_square_coordinate = Vector((-1, -1))  # Will never be equal to any coordinate within the grid
        previous_square = square.parent
        if previous_square is not None:
            previous_square_coordinate = previous_square.coordinate
        coordinate = square.coordinate
        coordinate_indices_to_check = ((coordinate.x - 1, coordinate.y),
                                       (coordinate.x, coordinate.y - 1),
                                       (coordinate.x, coordinate.y + 1),
                                       (coordinate.x + 1, coordinate.y))
        edge_checks = self.__edge_checks(coordinate)
        squares = []
        for edge_check, coordinate_indices in zip(edge_checks, coordinate_indices_to_check):
            potential_coordinate = Vector(coordinate_indices)
            if potential_coordinate != previous_square_coordinate and edge_check:
                next_square = self.square_from_grid(potential_coordinate, parent=square)
                if square.is_valid_next(potential_coordinate):
                    squares.append(next_square)
        return squares

    def square_from_grid(self, coordinate: Vector, parent: Square) -> Square:
        try:
            _square = Square(coordinate,
                             self.distances_to_end_node[coordinate.x][coordinate.y],
                             self.grid[coordinate.x][coordinate.y],
                             parent=parent)
        except IndexError as e:
            print(f"Bad coordinate: {coordinate}")
            print(f"Grid size: ({self.n},{self.m})")
            raise e
        return _square

    def minimal_route_heat_loss(self) -> (int, list[Vector]):
        # Definitely a pathfinding problem.
        start_square = self.square_from_grid(Vector((0, 0)), parent=None)
        start_square.heat_loss = 0  # We don't include the starting heat loss

        open_squares = [start_square]
        final_coordinate = Vector((self.n - 1, self.m - 1))

        checked_grid = [[False for _ in range(self.m)] for _ in range(self.n)]

        while open_squares:
            # TODO better data structure for popping from the open_squares? PriorityQueue/BinaryTree Heap?
            square = open_squares[0]
            pop_index = 0

            for i, element in enumerate(open_squares):
                if element.f < square.f:
                    pop_index = i
                    square = element

            square = open_squares.pop(pop_index)
            if square.coordinate == final_coordinate:
                return square.heat_loss, square.path_to_root_parent()

            checked_grid[square.coordinate.x][square.coordinate.y] = 1

            potential_next_squares = self.potential_squares(square)
            for potential_next_square in potential_next_squares:
                next_square_coord = potential_next_square.coordinate
                if checked_grid[next_square_coord.x][next_square_coord.y]:
                    continue

                for open_square in open_squares:
                    if potential_next_square.coordinate == open_square.coordinate and potential_next_square.heat_loss > open_square.heat_loss:
                        continue

                open_squares.append(potential_next_square)


def tests1():
    lava_grid = LavaGrid.from_lines(read_lines("day_17_1_test_input.txt"))
    print(lava_grid)
    e, path = lava_grid.minimal_route_heat_loss()
    assert e == 102


def tests2():
    lava_grid = LavaGrid.from_lines(read_lines("day_17_1_test_input2.txt"))

    e, path = lava_grid.minimal_route_heat_loss()
    assert e == 493


def main():
    tests1()
    tests2()

    # lava_grid = LavaGrid.from_lines(read_lines("day_17_1_input.txt"))
    # print(lava_grid)
    #
    # e, path = lava_grid.minimal_route_heat_loss()
    # print(e)


if __name__ == "__main__":
    main()