#!/usr/bin/env bash

set +x

if [ $# -lt 1 ]; then
  echo "Missing directory argument, exiting..." >&2
  exit 1
fi

config_dir=$1

if [ ! -d $config_dir ]; then
  echo "Directory (${config_dir}) does not exist, exiting..."
  exit 1
fi

for src in $config_dir/*; do
  src_base=$(basename $src)
  for trg in config sample; do
    full_trg=./$trg/$src_base
    if [ -f $full_trg ] || [ -f $full_trg.dist ] ; then
      set -x
      cp $src $full_trg
      set +x
    fi
  done
done
