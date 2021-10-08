#!/bin/sh

wondershaper $NET_INTERFACE $INGRESS_KBS $EGRESS_KBS



# if [ "$1" == "hping3" ]; then
#     eval "$@ $SERVER"
# done

if [ "$TIMEOUT_CMD" -gt 0 ]; then
    CMD="$@ $SERVER"
    echo "$CMD"
    timeout $TIMEOUT_CMD $CMD
    tail -f /dev/null
else
    eval "$@ $SERVER"
fi




# hping3 --rand-source -I net1 --flood -p 80 10.1.1.102
# t50 $SERVER --flood --turbo --protocol $PROTOCOL -s $(hostname -i)
