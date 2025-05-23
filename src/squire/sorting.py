def chromosome_sorter(chromosome: str) -> tuple[int, int] | tuple[int, str]:
    if chromosome.startswith("chr"):
        num_part = chromosome[3:]
        if num_part.isdigit():
            return (0, int(num_part))
        else:
            return (1, num_part)
    else:
        return (2, chromosome)
