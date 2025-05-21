import argparse
from importlib.metadata import version


class SquireMainHelpFormatter(argparse.HelpFormatter):
    def _format_action(self, action):
        if isinstance(action, argparse._SubParsersAction):
            parts = []
            for subaction in action._get_subactions():
                parts.append(self._format_action(subaction))
            return "".join(parts)
        return super()._format_action(action)


class SquireSubparserHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings:
            (metavar,) = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            return ", ".join(action.option_strings)

    def _format_action(self, action):
        if action.required:
            action.help = "[REQUIRED] " + (action.help or "")
        return super()._format_action(action)

    def _get_help_string(self, action):
        help = action.help or ""
        if (
            action.default is not argparse.SUPPRESS
            and action.default is not None  # (default: None) is unhelpful
            and "%(default)" not in help
        ):
            help += "\n(default: %(default)s)"
        return help

    def _split_lines(self, text, width):
        lines = []
        for line in text.split("\n"):
            if not line:
                lines.append(line)
                continue
            lines.extend(super()._split_lines(line, width))
        return lines


def file_list(string):
    return [file for file in string.casefold().split(",")]


def main():
    parser = argparse.ArgumentParser(
        prog="squire",
        description="A utility to generate inputs for HyLoRD",
        formatter_class=SquireMainHelpFormatter,
    )
    parser.add_argument("-v", "--version", action="version", version=version("squire"))
    shared_parser = argparse.ArgumentParser(
        add_help=False, formatter_class=SquireSubparserHelpFormatter
    )
    shared_parser.add_argument("-d", "--hdf5", required=True, help="Path to hdf5 file")

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title="Available commands",
    )

    # -------------
    # CREATE
    # -------------
    parser_create = subparsers.add_parser(
        "create",
        help="Initialise the hdf5 file containing all data.",
        parents=[shared_parser],
        formatter_class=SquireSubparserHelpFormatter,
    )
    input_group = parser_create.add_argument_group(
        "input options (use one of)",
        description="Specify input files using either --bedmethyl-list OR --file",
    )
    bedmethyl_parse_group = input_group.add_mutually_exclusive_group(required=True)

    bedmethyl_parse_group.add_argument(
        "-b",
        "--bedmethyl-list",
        help="Comma separated list of paths to bedmethyl files",
        type=file_list,
    )
    bedmethyl_parse_group.add_argument(
        "-f",
        "--file",
        help="Path to a file containing newline-separated list of bedmethyl files",
    )

    # -------------
    # REFERENCE
    # -------------
    parser_reference = subparsers.add_parser(
        "reference",
        help="Generate the reference matrix from existing hdf5 file",
        parents=[shared_parser],
        formatter_class=SquireSubparserHelpFormatter,
    )
    parser_reference.add_argument(
        "out_path", help="File path to write the reference matrix to"
    )

    # -------------
    # CPGLIST
    # -------------
    parser_cpglist = subparsers.add_parser(
        "cpglist",
        help=(
            "Generate a CpG list containing only CpGs that are significantly "
            "different between cell types"
        ),
        parents=[shared_parser],
        formatter_class=SquireSubparserHelpFormatter,
    )
    parser_cpglist.add_argument("out_path", help="File path to write the CpG list to")
    parser_cpglist.add_argument(
        "-t", "--threshold", help="The threshold to use when filtering", default=1e-10
    )

    # -------------
    # REPORT
    # -------------
    parser_report = subparsers.add_parser(
        "report",
        help="Reports CpG list length for different threshold values",
        parents=[shared_parser],
        formatter_class=SquireSubparserHelpFormatter,
    )
    parser_report.add_argument(
        "-t",
        "--thresholds",
        help="A list of thresholds to report on",
        default=[1e-1, 1e-2, 1e-5, 1e-10, 1e-20],
    )
    args = parser.parse_args()
