#!/bin/sh

sleep_counter() {
    for i in 1 2 3; do
        echo "Sleeping $i"
        sleep 1
    done
}

IP_ADDRESS=$(curl https://ifconfig.me)

ABS_PATH="/home/moojig/scripts/cloudflare-dns-checker"

$ABS_PATH/check_zone.py update-all --zone-name='chimid.rocks' --comment location:home --ip-address $IP_ADDRESS
curl https://hc-ping.com/c75c0653-9f32-4b6a-997d-7c113dfe96f3/$?

sleep_counter

$ABS_PATH/check_zone.py update-all --zone-name='intellidnd.com' --ip-address $IP_ADDRESS
curl https://hc-ping.com/c75c0653-9f32-4b6a-997d-7c113dfe96f3/$?

echo "All zones checked."
