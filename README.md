<p align="center">
  <img style="border-radius:10px" src="https://github.com/user-attachments/assets/1e82a815-8bab-4f48-8f28-0960c223eb54" />
</p>

</p>
<p align="center">
    <a href="https://github.com/sof202/SQUIRE/commits/main/" alt="Commit activity">
        <img src="https://img.shields.io/github/commit-activity/m/sof202/SQUIRE?style=for-the-badge&color=green" /></a>
    <a href="https://github.com/sof202/SQUIRE/blob/main/LICENSE" alt="License">
        <img src="https://img.shields.io/github/license/sof202/SQUIRE?style=for-the-badge&color=green" /></a>
</p>

## Table of contents

* [Description](#description)
  * [Why not package with HyLoRD](#why-not-package-with-hylord)
* [Software Requirements](#software-requirements)
* [Installation](#installation)
  * [Updating](#updating)
* [Usage](#usage)
  * [Job schedulers](#job-schedulers)

## Description

SQUIRE (Statistical Quality Utility for Ideal Reference matrix Enhancement) is
a python CLI tool that can assist the usage of 
[HyLoRD](https://github.com/sof202/HyLoRD). The
[inputs](https://sof202.github.io/HyLoRD/inputs-outputs.html) of HyLoRD include
a reference matrix and a list of 'useful' CpGs, however the creation of these
files is non-trivial. 

SQUIRE will:

- Combine bedmethyl files obtained from ONT's
[modkit](https://github.com/nanoporetech/modkit) into a reference matrix
(`--reference-matrix`).
- Apply statistical tests to each CpG site which can be used for filtering 
when creating a list of useful CpGs (`--cpg-list`).
  - Increasing performance considerably

### Why not package with HyLoRD

User's might have their own ideas on how to generate the input files for
HyLoRD. Maybe they don't have cell sorted ONT data and instead just want to
work with WGBS data (more available, but accuracy will suffer). Perhaps they
want to work with different statistical tests than the ones used by SQUIRE.
For these reasons, SQUIRE has been made independent from HyLoRD as it is
completely optional.

## Software Requirements

- [git](https://git-scm.com/)
- [bash](https://www.gnu.org/software/bash/)
- [python](https://www.python.org/) [>=3.12]
- [poetry](https://github.com/python-poetry/poetry) [>=2.1.3]

## Installation

First install the project with:

```bash
git clone https://github.com/sof202/SQUIRE.git
cd SQUIRE
# Installs to ~/.local/bin
./install.sh 
```

Alternatively you can install to a user specified location with:

```bash
git clone https://github.com/sof202/SQUIRE.git
cd SQUIRE
./install.sh path/to/install/directory
```

Provided that the installation directory is on your `PATH` (the installation
script will tell you how to do this if this isn't the case), you can run SQUIRE
via:

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
tools available to you via subcommands of `squire`. Full details for which
can be found via:

```bash
squire [subcommand] --help
```

Typical (bare-bones) usage might be:

```bash
squire create -d squire.h5 -b bedmethyl1.bed,bedmethyl2.bed,...,bedmethyln.bed
squire reference -d squire.h5 reference_matrix.bed
squire cpglist -d squire.h5 cpg_list.bed
```

Further, more in-depth, examples can be found in `scripts/`.

### Job schedulers

It is fairly likely that SQUIRE will take some time to complete statistical
tests (especially if the number of samples is high). In the event that the user
has access to a HPC (common in bioinformatics) they may want to utilise a job
scheduler (such as SLURM, PBS or TORQUE *etc.*) to run SQUIRE. Example scripts
for such uses of SQUIRE can be found in `scripts/`. These scripts are not
comprehensive, but should be a sufficient starting point.
