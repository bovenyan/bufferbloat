#!/bin/bash
echo "start cs144 buffer bloat experiment"
python bufferbloat.py --bw-host 1000 \
                --bw-net 10 \
                --delay 10 \
                --dir ./ \
                --nflows 1 \
                --maxq 1000 \
                -n 2 \

echo "end"
