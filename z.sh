#!/bin/sh
#
# at prompt:
# ./z.sh | nc box 8000
# 1:99
# ....
# ....
#
# generate test_binary_data:
# yes 1:2 | head -n 10000 | ./z.sh >out.bin
#

echo ${1:-0}

while read s
do
    instruction=${s%%:*}
    json_body=${s#*:}
    json_length=${#json_body}

    hi=$(printf "%o" $((instruction / 256)))
    lo=$(printf "%o" $((instruction % 256)))
    printf "\\$hi\\$lo"

    hi=$(printf "%o" $((json_length / 256)))
    lo=$(printf "%o" $((json_length % 256)))
    printf "\\$hi\\$lo"

    printf "${json_body}"
done

#sleep ${1:-1}

