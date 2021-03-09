#!/usr/bin/env python3

import os

from aws_cdk import core as cdk, aws_ec2 as ec2

from wormhole.wormhole_stack import WormholeStack
from wormhole.vpc import VpcStack

SSH_KEY_NAME = os.environ.get('WORMHOLE_SSH_KEY_NAME', None)
VPC_ID = os.environ.get('WORMHOLE_VPC_ID', None)


app = cdk.App()

if VPC_ID is not None:
    vpc = ec2.Vpc.from_lookup(app, 'WormholeVpcExistingStack', vpc_id=VPC_ID)
else:
    vpc = VpcStack(app, 'WormholeVpcStack', cidr='192.168.0.0/16')

WormholeStack(app, 'WormholeStack', SSH_KEY_NAME, vpc)

app.synth()
