#!/usr/bin/env bash

set -e

MSG="[WORMHOLE]"
COMMAND=$1
USAGE="wormhole [ssh|socks]"
PROXY_COMMAND="sh -c 'aws ssm start-session --target %h --document-name AWS-StartSSHSession --parameters portNumber=%p --region $AWS_REGION'"
WORMHOLE_PORT=8888

instance_id() {
  echo "$MSG Finding instance id..."
  INSTANCE_ID=$(aws ec2 describe-instances --query 'Reservations[*].Instances[?State.Name==`running`].InstanceId' --filter "Name=tag:ec2:purpose,Values=wormhole" --output text "$AWS_REGION" | head -n 1)
  if [[ -z $INSTANCE_ID ]]; then
    echo "$MSG ERROR when trying to find EC2 instance for wormhole to use"
    exit 1
  fi
}

socks_healthcheck() {
  while :
  do
      CURL_CODE=0
      CURL_CALL="curl -m 10 -x socks5h://127.0.0.1:8888 https://google.com"
      $CURL_CALL > /dev/null 2>&1 || CURL_CODE=$?
      if [[ ${CURL_CODE} -ne 0 ]]; then
        echo "$MSG Connection to wormhole socks proxy not available. exiting..."
        exit 1
      fi
      sleep 30
  done
}

case $COMMAND in
  ssh)
    echo "$MSG setting up terminal session with EC2 instance"
    instance_id
    aws ssm start-session --target $INSTANCE_ID
    ;;
  socks)
    echo "$MSG setting up socks proxy with EC2 instance"
    instance_id
    ssh -4 -i "/home/wormhole/.ssh/WormholeKey.pem" -D "0.0.0.0:8888" -o ProxyCommand="$PROXY_COMMAND" -o "StrictHostKeyChecking no" -C -N -f ec2-user@$INSTANCE_ID
    socks_healthcheck
    ;;
  *)
    echo "Unrecognized command. Usage: $USAGE"
esac
