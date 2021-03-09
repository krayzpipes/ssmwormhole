"""CDK Stack to deploy a VPC."""
from aws_cdk import core as cdk
from aws_cdk.aws_ec2 import Vpc


class VpcStack(cdk.Stack):
    """Build a VPC for wormhole.

    This stack uses the built-in cdk VPC construct, which has several
    defaults such as Internet Gateway, NAT Gateway per public subnet,
    public and private subnets spanning all Availability Zones, etc."""

    def __init__(self, scope: cdk.Construct, id: str, cidr=None, **kwargs):
        super().__init__(scope, id)
        self.cidr = cidr or "10.0.0.0/16"
        self.vpc = Vpc(
            self, f"{id}Vpc",
            cidr=self.cidr,
            **kwargs,
        )
