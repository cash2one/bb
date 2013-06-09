#!/bin/sh
while read s
do
    instruction=${s%% *}
    json_body=${s#* }
    json_length=${#json_body}

    hi=$((instruction / 256))
    lo=$((instruction % 256))
    echo -ne "\x$(printf %x ${hi})\x$(printf %x ${lo})"

    hi=$((json_length / 256))
    lo=$((json_length % 256))
    echo -ne "\x$(printf %x ${hi})\x$(printf %x ${lo})"
    echo -n "${json_body}"
done

