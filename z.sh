#!/bin/bash
#
# at prompt:
# ./z.sh | nc box 8000
# 1:99
# ....
# ....
#

echo ${1:-0}

while read s
do
    instruction=${s%%:*}
    json_body=${s#*:}
    json_length=${#json_body}

    hi=$((instruction / 256))
    lo=$((instruction % 256))
    echo -ne "$(printf '\\x%x\\x%x' ${hi} ${lo})"

    hi=$((json_length / 256))
    lo=$((json_length % 256))
    echo -ne "$(printf '\\x%x\\x%x' ${hi} ${lo})"
    echo -n "${json_body}"
done

#sleep ${1:-1}

