#!/usr/bin/env python3

import os

from aws_cdk import core as cdk, aws_ec2 as ec2

from wormhole.ec2 import Ec2Stack
from wormhole.vpc import VpcStack

SSH_KEY_NAME = os.environ.get('WORMHOLE_SSH_KEY_NAME', None)
VPC_ID = os.environ.get('WORMHOLE_VPC_ID', None)


app = cdk.App()

if VPC_ID is not None:
    vpc = ec2.Vpc.from_lookup(app, 'WormholeNetwork', vpc_id=VPC_ID)
else:
    vpc_stack = VpcStack(app, 'WormholeNetworkStack', cidr='192.168.0.0/16')
    vpc = vpc_stack.vpc

wormhole = Ec2Stack(app, 'WormholeEc2Stack', SSH_KEY_NAME, vpc)
if VPC_ID is None:
    wormhole.add_dependency(vpc_stack)

app.synth()
