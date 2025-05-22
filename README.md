# SQUIRE

**S**tatistical **Q**uality **U**tility for **I**deal **R**eference matrix
**E**nhancement

## Description

This is a set of python scripts that are to be used with
[HyLoRD](https://github.com/sof202/HyLoRD). The
[inputs](https://sof202.github.io/HyLoRD/inputs-outputs.html) of HyLoRD include
a reference matrix and a list of 'useful' CpGs, however the creation of these
files is not necessarily trivial. 

SQUIRE will:

- Combine bedmethyl files obtained from ONT's
[modkit](https://github.com/nanoporetech/modkit) into a reference matrix
(`--reference-matrix`).
- Apply statistical tests to each CpG site which can be used for filtering 
when creating a list of useful CpGs (`--cpg-list`).

### Why not package with HyLoRD

User's might have their own ideas on how to generate the input files for
HyLoRD. Maybe they don't have cell sorted ONT data and instead just want to
work with WGBS data (more available, but accuracy will suffer). Perhaps they
want to work with different statistical tests than the ones used by SQUIRE.

## Software Requirements

- [bash](https://www.gnu.org/software/bash/)
- [poetry](https://github.com/python-poetry/poetry)
- [git](https://git-scm.com/)

## Installation

First install the project with:

```bash
git clone https://github.com/sof202/SQUIRE.git
cd SQUIRE
# installs to ~/.local/bin
./install.sh 
```

Alternatively you can install to a user specified location with:

```bash
git clone https://github.com/sof202/SQUIRE.git
cd SQUIRE
./install.sh path/to/install/directory
```

Provided that the installation directory is on your `PATH`, you can run
SQUIRE via:

```bash
# Print help message for squire
squire --help
```

### Updating

To update SQUIRE:

```bash
cd path/to/SQUIRE
git pull
poetry update
```

## Usage

Upon [installing](#installation) SQUIRE successfully, you will have a suite of
tools avaible to you via subcommands of `squire`. Full details for which
can be found via:

```bash
squire [subcommand] --help
```

Typical usage would be:

```bash
squire create -d squire.h5 -b bedmethyl1.bed,bedmethyl2.bed,...,bedmethyln.bed
squire reference -d squire.h5 reference_matrix.bed
squire cpglist -d squire.h5 cpg_list.bed
```

Further examples can be found in `scripts/`.

### Job schedulers

It is fairly likely that SQUIRE will take some time to complete statistical
tests (especially if the number of samples is high). In the event that the user
has access to a HPC (common in bioinformatics) they may want to utilise a job
scheduler (such as SLURM, PBS or TORQUE) to run SQUIRE. Example scripts for
such uses of SQUIRE can be found in `scripts/`. These scripts are not
comprehensive, but should be a sufficient starting point.
