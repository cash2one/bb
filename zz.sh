#!/bin/sh
#
# ./z.sh | nc z 2000

while read s
do
    length=${#s}
    hi=$(printf "%o" $((length / 256)))
    lo=$(printf "%o" $((length % 256)))
    printf "\\$hi\\$lo"
    printf "$s"
done

