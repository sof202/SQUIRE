import argparse
import sys
from importlib.metadata import version

from squire.main import (
    create_hdf,
    print_threshold_analysis,
    write_cpg_list,
    write_reference_matrix,
)
from squire.squire_exceptions import SquireError


class SquireMainHelpFormatter(argparse.HelpFormatter):
    """Formatter for squire -h

    Format streamlines the available commands by removing the duplicated
    {command 1, command 2, command 3} string
    """

    def _format_action(self, action):
        if isinstance(action, argparse._SubParsersAction):
            parts = []
            for subaction in action._get_subactions():
                parts.append(self._format_action(subaction))
            return "".join(parts)
        return super()._format_action(action)


class SquireSubparserHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    """Formatter for squire subcommand -h

    - Removes the metavariables from short/long options (declutter)
    - Adds [REQUIRED] before required options
    - Places default lists on a new line for each option
    """

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
    """Convert a comma separated string into a list of file paths"""
    return [file for file in string.split(",")]


def float_list(string):
    """Convert a comma separated string into a list of floats"""
    try:
        return [float(number) for number in string.split(",")]
    except ValueError as e:
        raise ValueError(
            "Thresholds must be comma separated list of floats"
        ) from e


def main():
    """Main entry point for squire

    Handles argument parsing for the main parser and all subparsers
    (subcommands)
    """
    parser = argparse.ArgumentParser(
        prog="squire",
        description="A utility to generate inputs for HyLoRD",
        formatter_class=SquireMainHelpFormatter,
    )
    parser.add_argument(
        "-v", "--version", action="version", version=version("squire")
    )
    shared_parser = argparse.ArgumentParser(
        add_help=False, formatter_class=SquireSubparserHelpFormatter
    )
    shared_parser.add_argument(
        "-d",
        "--hdf5",
        required=True,
        help="Path to hdf5 file (e.g. ./squire.h5)",
    )
    shared_parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="If this flag is set, output files can be overwritten",
    )

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
        help="Initialise the hdf5 file containing all data",
        parents=[shared_parser],
        formatter_class=SquireSubparserHelpFormatter,
    )
    input_group = parser_create.add_argument_group(
        "input options (use one of)",
        description=(
            "Specify input files using either --bedmethyl-list OR --file"
        ),
    )
    bedmethyl_parse_group = input_group.add_mutually_exclusive_group(
        required=True
    )

    bedmethyl_parse_group.add_argument(
        "-b",
        "--bedmethyl-list",
        help=(
            "Comma separated list of paths to bedmethyl files "
            "(e.g. neuron.bed,glia.bed,astrocyte.bed)"
        ),
        type=file_list,
    )
    bedmethyl_parse_group.add_argument(
        "-f",
        "--file",
        help=(
            "Path to a file containing newline-separated list of "
            "bedmethyl files"
        ),
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
        "out_path",
        help=(
            "File path to write the reference matrix to "
            "(e.g. ./reference_matrix.bed)"
        ),
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
    parser_cpglist.add_argument(
        "out_path",
        help="File path to write the CpG list to (e.g. ./cpg_list.bed)",
    )
    parser_cpglist.add_argument(
        "-t",
        "--threshold",
        help="The threshold to use when filtering",
        default=1e-10,
        type=float,
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
        help=(
            "A comma separated list of thresholds to report on "
            "(e.g. 0.1,0.001,0.0001,1e-10)"
        ),
        default=[1e-1, 1e-2, 1e-5, 1e-10, 1e-20],
        type=float_list,
    )
    args = parser.parse_args()

    run_squire(args)


COMMAND_MAP = {
    "create": create_hdf,
    "reference": write_reference_matrix,
    "cpglist": write_cpg_list,
    "report": print_threshold_analysis,
}


def run_squire(args):
    """Runs functions to execute squire subcommands"""
    try:
        command = COMMAND_MAP.get(args.command)
        if command is None:
            raise SquireError(
                f"{args.command} is not a valid squire command. "
                "Run squire -h to view available commands"
            )
        command(args)
    except SquireError as e:
        print(f"Squire error: {e}", file=sys.stderr)
        if e.__cause__:
            print(f"Details: {e.__cause__}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Uncaught error: {e}", file=sys.stderr)
        if e.__cause__:
            print(f"Details: {e.__cause__}", file=sys.stderr)
        sys.exit(1)
