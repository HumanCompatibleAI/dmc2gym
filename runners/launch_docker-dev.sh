#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.
set -x # echo on

__usage="launch_docker-dev.sh - Launching kmdanielduan/dmc2gym:dev
Usage: launch_docker-dev.sh [options]
options:
  -h, --help                show this help message and exit
  -r, --remove_custom       remove customized config mounts for tmux and wandb
Note: You can specify LOCAL_MNT environment variables to mount local repository
  and output directory respectively.
"

REMOVE_CUSTOM=0

while test $# -gt 0; do
  case "$1" in
  -h | --help)
    echo "${__usage}"
    exit 0
    ;;
  -r | --remove_custom)
    REMOVE_CUSTOM=1
    shift
    ;;
  *)
    echo "Unrecognized flag $1" >&2
    exit 1
    ;;
  esac
done

##################
## Docker Image ##
##################

DOCKER_IMAGE="kmdanielduan/dmc2gym:dev"
if [[ ${LOCAL_MNT} == "" ]]; then
  LOCAL_MNT="${HOME}"
fi

###########
## Flags ##
###########


# if port is changed here, it should also be changed in scripts/launch_jupyter.sh
# FLAGS+="--gpus all "  # Use all GPUs
FLAGS+="-p 9988:9988 "  # ports

FLAGS+="-v ${LOCAL_MNT}/dmc2gym:/dmc2gym "  # mounting local dmc2gym repo

if [[ $REMOVE_CUSTOM == 0 ]]; then
  # flags for easy development
  FLAGS+="-v ${LOCAL_MNT}/custom_configs/.netrc:/root/.netrc "  # mounting local .netrc for wandb login
  FLAGS+="-v ${LOCAL_MNT}/custom_configs/.tmux.conf:/root/.tmux.conf "  # mounting local .tmux.conf for custom tmux configs
fi

# FLAGS+="--env MUJOCO_GL=egl "  # setting egl backend, required by dm_control. https://github.com/deepmind/dm_control#rendering
# FLAGS+="--env MNT_ROOT=/mnt "  # setting output directory environment variable

##############
## Commands ##
##############

CMD+="pip3 install -e .[test] "

# Using jupyter lab for easy development
if [[ $1 == "jupyter" ]]; then
  CMD+="&& scripts/launch_jupyter.sh "
fi

###################
## Run Container ##
###################

docker run -it --rm --init --name d2g \
       ${FLAGS} \
       ${DOCKER_IMAGE} \
       /bin/bash -c "exec bash"
      #  /bin/bash -c "${CMD} && exec bash"