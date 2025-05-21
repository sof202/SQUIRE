from pathlib import Path


def read_file_of_files(path: Path):
    file_list = []
    with open(path, mode="r") as fof:
        for file in fof:
            file_list.append(Path(file))
    return file_list


def make_parents(path: Path):
    parent_dir = path.parent
    if not parent_dir.exists():
        parent_dir.mkdir(parents=True, exist_ok=True)


def make_viable_path(path: Path, exists_ok=True):
    try:
        if (not exists_ok) and (path.exists()):
            raise FileExistsError(
                f"{path} already exists, if this is expected rerun with -o/--overwrite"
            )
        make_parents(path)
    except PermissionError:
        raise PermissionError(f"You do not have permissions to create {path}.")
