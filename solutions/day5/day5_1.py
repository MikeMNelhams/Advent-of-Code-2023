from handy_dandy_library.file_processing import read_lines


class Map:
    def __init__(self, map_ranges: tuple[int]):
        self.interval_mappings = self.__get_interval_mappings(map_ranges)

    def __getitem__(self, item: int):
        return self.interval_mappings[item]

    @staticmethod
    def __get_interval_mappings(map_ranges: list[int]) -> tuple[int]:
        start = map_ranges[1]
        end = start + map_ranges[2] - 1
        addition_coefficient = map_ranges[0] - start
        return start, end, addition_coefficient

    def overlaps(self, other) -> bool:
        first_overlap_check = self.interval_mappings[1] > other.interval_mappings[0]
        return first_overlap_check or other.interval_mappings[1] > self.interval_mappings[0]

    def is_within_mapping(self, source: int) -> bool:
        return self.interval_mappings[0] <= source <= self.interval_mappings[1]

    def destination_assuming_valid(self, source: int) -> int:
        return source + self.interval_mappings[2]

    def __repr__(self) -> str:
        return f"Map{self.interval_mappings}"


class FarmingDataReader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.__lines = read_lines(file_path)
        self.__start_index = 0
        self.n = len(self.__lines)

    def lines(self, end_index: int) -> list[str]:
        start_index = self.start_index
        return self.__lines[start_index:start_index + end_index]

    @property
    def start_index(self) -> int:
        return self.__start_index

    def parse_seed_numbers(self) -> list[int]:
        seeds_phrase = None

        for i, line in enumerate(self.__lines):
            if line == '':
                seeds_phrase = ''.join(self.lines(i))
                self.__start_index = i + 1
                break

        seed_numbers = [int(seed) for seed in seeds_phrase[6:].split(' ') if seed != '']
        return seed_numbers

    def parse_next_source_to_destination_map(self) -> list[Map]:
        map_numbers_phrase = None

        for i, line in enumerate(self.__lines[self.__start_index:]):
            if self.start_index + i == self.n - 1:
                self.__start_index += 1
                map_numbers_phrase = self.lines(i + 1)
                break

            if line == '':
                self.__start_index += 1
                map_numbers_phrase = self.lines(i - 1)
                self.__start_index += i
                break

        map_numbers = [Map(tuple(int(number) for number in line.split(' '))) for line in map_numbers_phrase]
        return map_numbers


def lowest_location(seeds: list[int], maps: list[Map]) -> int:
    seeds_copy = seeds.copy()
    for mappings in maps:
        print(mappings)
        seeds_copy = destination(seeds_copy, mappings)
    return min(seeds_copy)


def destination(seeds: list[int], maps: list[Map]) -> list[int]:
    next_seeds = seeds.copy()
    for i, seed in enumerate(seeds):
        for mapping in maps:
            if mapping.is_within_mapping(seed):
                next_seeds[i] = mapping.destination_assuming_valid(seed)
                break
    return next_seeds


def lowest_location_from_reader(farming_data_reader: FarmingDataReader) -> int:
    seeds = farming_data_reader.parse_seed_numbers()
    maps = [farming_data_reader.parse_next_source_to_destination_map() for _ in range(7)]
    return lowest_location(seeds, maps)


def tests():
    farming_data_reader = FarmingDataReader("day_5_1_test_input.txt")
    assert lowest_location_from_reader(farming_data_reader) == 35


def main():
    tests()

    # farming_data_reader = FarmingDataReader("day_5_1_input.txt")
    # t = lowest_location_from_reader(farming_data_reader)
    # print(t)


if __name__ == "__main__":
    main()
