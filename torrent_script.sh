#!/bin/sh

fromdirectory=$1
title=$2
label=$3
kind=$4
name=$5
hash=$6

cdir="$( cd "$( dirname "$BASH_SOURCE[0]}" )" && pwd)"

echo "Handling torrent " >> $cdir/logs/handled_torrents.log
echo "Directory: " $fromdirectory >> $cdir/logs/handled_torrents.log
echo "Title: " $title >> $cdir/logs/handled_torrents.log

$cdir/env/bin/python $cdir/torrent_script.py --title "$title" --label "$label" --dir "$fromdir" --name "$name" --kind "$kind" --info_hash "$hash"


