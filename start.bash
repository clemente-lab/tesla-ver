#!/bin/bash

# Takes redis server location, and asks user to confirm starting the server
function start_local_redis {
  if [ -f $1 ];
  then
    read -r -p "Start redis-server found at $1 [y/N] " response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
    then
        $1 --daemonize yes
        echo "Redis Server Started"
    else
        exit 1
    fi
  fi
}

# Checks if redis-server is already downloaded locally
if [ -f "./redis_dir/redis-stable/src/redis-server" ]
then
  echo "redis-server locally available"
  start_local_redis "./redis_dir/redis-stable/src/redis-server"

# Alternatively, is redis-server available in the path, if not, download and build the server/cli
elif ! redis_loc="$(type -p "redis-server")" || [[ -z /usr/local/bin/.redis-server ]];
then
  echo "Redis is not installed"
  echo "Redis uses the license at https://redis.io/topics/license"
  echo "The license may also be found at ./redis-dir/Redis-License,"
  echo "although the linked license is the current, authoritative version"
  echo "By installing, you agree to the terms of this license"
  read -r -p "Install Redis? [y/N] " response
  if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
  then
      rm -r ./redis_dir/redis-stable || true
      curl -so - http://download.redis.io/redis-stable.tar.gz | tar -C ./redis_dir -xvzf -
      make -C ./redis_dir/redis-stable
      start_local_redis "./redis_dir/redis-stable/src/redis-server"
  else
      exit 1
  fi

# Starts redis server in path
else
  redis_path = $(type -p redis-server | cut -d" " -f3)
  echo "Redis Installation Found at: $redis_path"
  type -p "redis-server"
  echo "Starting redis:"
  redis-server --daemonize yes
fi

# Function used with trap to shutdown redis server cleanly as part of exiting program
function shutdown_with_redis {
  ./redis_dir/redis-stable/src/redis-cli SHUTDOWN
  echo "Redis Server shutdown"
  echo "Thanks for using tesla-ver!"
  exit 0
}
trap "shutdown_with_redis" SIGINT

# Sources conda behavior scripts, and then generates/checks for existing tesla-ver environment,
# and then activates the tesla-ver environment
function start_conda_session {
  CONDA_PREFIX=$(find $HOME -maxdepth 1 -type d | grep -E "\w{3,4}conda")
  source $CONDA_PREFIX/etc/profile.d/conda.sh
  ENVS=$(conda env list | awk '{print $1}' )
  if [[ $ENVS = *"tesla-ver"* ]]; then
    echo "activating"
    conda activate tesla-ver
  else
    echo "creating"
    conda env create --file environment.yaml && conda activate tesla-ver
  fi
}

# Checks if conda installation is found -- if not, it offers to install it via batch silent install
if ! conda_loc="$(type -p "conda")";
then
  echo "Conda installation not found"
  echo "By installing, you agree to the conda license at https://docs.conda.io/en/latest/license.html"
  read -r -p "Install Conda for Linux? [y/N] " response
  if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
  then
      read -p "Mac or Linux (M/L)?" choice
      case "$choice" in
        m|M ) os_name="MacOSX";;
        l|L ) os_name="Linux";;
        * ) echo "invalid selection" && exit 1;;
      esac

      curl -o miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && bash miniconda.sh -b -p $HOME/miniconda && rm miniconda.sh
      start_conda_session
  else
      exit 1
  fi
# If conda installation is found, start conda session
else
  start_conda_session
fi

# Runs tesla-ver with gunicorn and 2 workers.
gunicorn --workers=2 --bind=0.0.0.0:5000 wsgi:server

