import subprocess

import tomlkit


def main() -> None:
    git_tag = (
        subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"])
        .decode()
        .strip()
        .lstrip("v")
    )

    with open("pyproject.toml", "r+") as f:
        config = tomlkit.load(f)
        config["project"]["version"] = git_tag
        f.seek(0)
        tomlkit.dump(config, f)


if __name__ == "__main__":
    main()
