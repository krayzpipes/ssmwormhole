#!/usr/bin/env bash

set -e

KEY_PAIR=$(aws ec2 create-key-pair --key-name WormholeKey)
KEY_LOCATION="$(pwd)/docker/wormhole/.ssh/WormholeKey.pem"

echo $KEY_PAIR | jq -r '.KeyMaterial' > $KEY_LOCATION
KEY_NAME=$(echo $KEY_PAIR | jq -r '.KeyName')

chmod 400 $KEY_LOCATION

echo "Key location: $KEY_LOCATION"
echo "Key name: $KEY_NAME"
