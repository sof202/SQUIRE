class SquireError(Exception):
    """Base exception class for SQUIRE-based errors"""

    pass


class HDFReadError(SquireError):
    """Exception for non-viable hdf5 files being supplied"""

    pass


class BedMethylReadError(SquireError):
    """Exception for non-viable bedmethyl files being supplied"""

    pass
