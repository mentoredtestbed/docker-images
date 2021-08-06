#!/bin/sh

#ip=`hostname -i`
#t50 10.200.72.12 --flood --turbo -s $(hostname -i)
wondershaper net1 1024 1024
t50 $SERVER --flood --turbo --protocol $PROTOCOL -s $(hostname -i)
#t50 $1 --flood --turbo --protocol UDP
#t50 $1 --flood --turbo
