#!/bin/bash
set -e

DEFAULT_INSTALL_DIR="${HOME}/.local/bin"

usage() {
cat << EOF
================================================
$(basename "$0")
================================================
Purpose: Install SQUIRE into the given directory
Args:
    \$1 -> Installation directory 
           (default: ${DEFAULT_INSTALL_DIR})
================================================
EOF
exit 0
}

while getopts h OPT; do
    case "$OPT" in
        h ) usage ;;
        \? ) usage ;;
    esac
done

shift $((OPTIND-1))

# -----------------
# Install directory
# -----------------

install_dir="${1:-$DEFAULT_INSTALL_DIR}"

echo "Installing SQUIRE into: ${install_dir}"
echo "Is this ok? (y/n) "
read -r response

if [[ "${response}" != "y" ]]; then 
    usage
fi

mkdir -p "${install_dir}"

# -------------------
# Poetry Installation
# -------------------

cd "$(dirname "$0")" || exit 1
poetry install

# ---------------
# Create launcher
# ---------------

cat > "${install_dir}/squire" << EOF
#!${SHELL}
. "$(poetry env info --path)/bin/activate"
exec squire "\$@"
EOF
chmod +x "${install_dir}/squire"

# ------------------
# PATH message setup
# ------------------

get_shell_rc() {
case "$(basename "${SHELL:-}")" in
    bash)
        if [[ -f "${HOME}/.bash_profile" ]]; then 
            echo "${HOME}/.bash_profile"
        else 
            echo "${HOME}/.bashrc"
        fi  ;;
    zsh)
        if [[ -f "${HOME}/.zprofile" ]]; then 
            echo "${HOME}/.zprofile"
        else 
            echo "${HOME}/.zshrc"
        fi  ;;
    fish)
        echo "${HOME}/.config/fish/config.fish" ;;
    *)
        echo "${HOME}/.profile" ;;
esac
}

rc_file=$(get_shell_rc)

path_instructions="echo 'export PATH=\"${install_dir}:\$PATH\"' >> \"${rc_file}\""
if [[ "$(basename "${SHELL:-}")" == "fish" ]]; then
    path_instructions="echo 'set -gx PATH \"${install_dir}\" \$PATH' >> \"${rc_file}\""
fi

# ------------
# PATH message
# ------------

GREEN='[0;32m'
YELLOW='[0;33m'
NO_COLOUR='[0m'

if echo "${PATH}" | grep -q "${install_dir}"; then
cat << EOF
${GREEN}Installed squire successfully at ${install_dir}. 
EOF
else
cat << EOF
${GREEN}Installed squire successfully at ${install_dir}. 
${YELLOW}
WARNING: ${install_dir} is not on your PATH please add it by running:
    ${NO_COLOUR}${path_instructions}
${YELLOW}
Then restart your shell or run:
    ${NO_COLOUR}source "${rc_file}"
    (or . "${rc_file}" for POSIX sh)
EOF
fi
