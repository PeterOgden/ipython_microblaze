#!/bin/bash
set -e

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
current_dir=$PWD
hdf_file="$(cd "$(dirname "$1")" && pwd)/$(basename $1)"
bsp_dir="$current_dir/bsp"
tmp_dir="/tmp/bsp_workspace"

if [ -e $tmp_dir ]; then
  echo "Working directory $tmp_dir exists, please remove"
  exit 1
fi

mkdir $tmp_dir

function delete_tmp() {
  rm -rf $tmp_dir
}

# trap delete_tmp EXIT

echo "Writing BSPs from HDF $hdf_file to $bsp_dir"

(cd $script_dir && xsct build.tcl $tmp_dir $hdf_file)

echo "Assembling BSPs"

for f in $tmp_dir/*_bsp
do
  bsp_name=$(basename -s _bsp $f)
  if [ -e $bsp_dir/$bsp_name ]; then
    echo "Skipping $bsp_name as one already exists"
    continue
  fi
  mkdir -p $bsp_dir/$bsp_name
  cp -r $f/$bsp_name/{include,lib} $bsp_dir/$bsp_name
  cp $script_dir/lscript.ld $bsp_dir/$bsp_name
  if [ -e $bsp_dir/$bsp_name/lib/libgloss.a ]; then
    rm $bsp_dir/$bsp_name/lib/libgloss.a
  fi
done

echo "Generation Complete!!"
