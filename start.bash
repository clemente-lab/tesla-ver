#!/bin/bash

function start_local_redis {
  if [ -f $1 ];
  then
    read -r -p "Start redis-server found at $1 [y/N] " response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
    then
        $1 &
    else
        exit 1
    fi
  fi
}

if [ -f "./redis_dir/redis-stable/src/redis-server" ]
then
  echo "redis-server locally available"
  start_local_redis "./redis_dir/redis-stable/src/redis-server"
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
else
  echo "Redis Installation Found at:"
  type -p "redis-server"
  echo "Starting redis:"
  redis-server
fi
function shutdown_with_redis {
  ./redis_dir/redis-stable/src/redis-cli SHUTDOWN
  echo "Redis Server shutdown"
  echo "Thanks for using tesla-ver!"
  exit 0
}
trap "shutdown_with_redis" SIGINT

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
      curl -so - "https://repo.anaconda.com/miniconda/Miniconda3-latest-$os_name-x86_64.sh" | bash - -b -p $HOME/miniconda
  else
      exit 1
  fi
else
  CONDA_PREFIX=$(conda info | grep -i "base environment" | grep -oEe "\w{3,4}conda3")
  source ~/$CONDA_PREFIX/etc/profile.d/conda.sh
  ENVS=$(conda env list | awk '{print $1}' )
  if [[ $ENVS = *"tesla-ver"* ]]; then
    echo "activating"
    find ./ -type f -maxdepth 1
    conda activate tesla-ver
  else
    echo "creating"
    find ./ -type f -maxdepth 1
    conda env create --file environment.yaml && conda activate tesla-ver
  fi
fi

gunicorn --workers=2 --bind=0.0.0.0:5000 wsgi:server

