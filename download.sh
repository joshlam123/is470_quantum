#!/usr/bin/env bash

echo cd $(dirname $0)
cd $(dirname $0)
echo syncing with $1:$2

# downlading results
rsync -av $1:$2/. ./ --progress


