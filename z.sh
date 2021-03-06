#!/bin/sh
#
# at prompt:
# ./z.sh 1 | nc z 8000 | od -A x -v -w4 -tx1c
# 16:1
# 17:
# ....
# ....
#
# generate test_binary_data:
# yes 1:2 | head -n 10000 | ./z.sh >out.bin
#

printf 'tgw_l7_forward\r
Host:z.app.twsapp.com\r
%d %s\r
\r
' \
${1:-1} \
token

while read s
do
    instruction=${s%%:*}
    json_body=${s#*:}
    json_length=$((${#json_body} + 2))

    hi=$(printf "%o" $((json_length / 256)))
    lo=$(printf "%o" $((json_length % 256)))
    printf "\\$hi\\$lo"

    hi=$(printf "%o" $((instruction / 256)))
    lo=$(printf "%o" $((instruction % 256)))
    printf "\\$hi\\$lo"

    printf "${json_body}"
done

#sleep ${1:-1}

