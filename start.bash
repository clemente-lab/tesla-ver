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
  echo "please install conda :)"
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

gunicorn --workers=2 --chdir=/tesla-ver/ --bind=0.0.0.0:5000 wsgi:server

