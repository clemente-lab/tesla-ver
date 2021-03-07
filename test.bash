#!/bin/bash

# Starts conda session
function start_conda_session {
  CONDA_PREFIX=$(find $HOME -maxdepth 1 -type d | grep -E "\w{3,4}conda")
  source $CONDA_PREFIX/etc/profile.d/conda.sh
  ENVS=$(conda env list | awk '{print $1}' )
  if [[ $ENVS = *"tesla-ver"* ]]; then
    echo "Activating tesla-ver environment"
    conda activate tesla-ver-test
  else
    echo "Creating and activating tesla-ver environment"
    conda env create --file environment_test.yaml && conda activate tesla-ver-test
  fi
}


# Checks if conda installation is found -- if not, it offers to install it via batch silent install
if [[ ! conda_loc="$(type -p "conda")" ]] || [[ ! -f $(find $HOME -maxdepth 1 -type d | grep -E "\w{3,4}conda")/etc/profile.d/conda.sh ]];
then
  echo "Conda installation not found"
  echo "By installing, you agree to the conda license at https://docs.conda.io/en/latest/license.html"
  read -r -p "Install Conda? [y/N] " response
  if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
  then
      read -p "Mac or Linux (M/L)? " choice
      case "$choice" in
        m|M|mac|macOSX|Mac|MacOSX ) os_name="MacOSX";;
        l|L|linux|Linux ) os_name="Linux";;
        * ) echo "invalid selection" && exit 1;;
      esac

      curl -o miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && bash miniconda.sh -b -p $HOME/miniconda && rm miniconda.sh
      start_conda_session
  else
      exit 1
  fi

else

  # If conda installation is found, start conda session
  start_conda_session

  # Install playwright for testing
  playwright install

  # Run tests
  pytest --base-url localhost:5000
fi
