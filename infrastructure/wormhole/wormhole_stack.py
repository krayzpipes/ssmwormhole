"""CDK Stack to deploy wormhole EC2 server in an autoscaling group."""

from aws_cdk import core as cdk
from aws_cdk import aws_autoscaling as asg, aws_ec2 as ec2, aws_iam as iam


class WormholeStack(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, id: str, ssh_key_name: str, vpc: ec2.IVpc
    ) -> None:

        super().__init__(scope, id)

        # Role used for EC2 Instance Profile to connect to SSM
        self.iam_role = iam.Role(
            scope=self,
            id=f"{id}Ec2Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            description="Role assumed by wormhole ec2 instance",
        )

        # IAM policy for sending messages to SSM
        self.iam_policy = self._create_iam_policy(self, id)
        self.iam_policy.attach_to_role(self.iam_role)

        # Autoscaling group so that if the server dies, another one
        # will automatically replace it. Note that it is being placed
        # in private subnets, so you will need a NAT gateway for
        # internet access.
        self.asg = asg.AutoScalingGroup(
            self,
            f"{id}ASG",
            vpc=vpc,
            instance_type=ec2.InstanceType("t3a.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            allow_all_outbound=True,  # Allows all outbound, including to SSM service
            role=self.iam_role,
            key_name=ssh_key_name,
            min_capacity=1,
            max_capacity=2,
            desired_capacity=1,
        )

    @staticmethod
    def _create_iam_policy(scope: cdk.Construct, id: str) -> iam.IPolicy:
        iam_policy_doc = iam.PolicyDocument()
        iam_policy_doc.add_statements(
            iam.PolicyStatement(
                actions=[
                    "ssm:UpdateInstanceInformation",
                    "ssmmessages:CreateControlChannel",
                    "ssmmessages:CreateDataChannel",
                    "ssmmessages:OpenControlChannel",
                    "ssmmessages:OpenDataChannel",
                ],
                resources=["*"],
                effect=iam.Effect.ALLOW,
            ),
            iam.PolicyStatement(
                actions=["s3:GetEncryptionConfiguration"],
                resources=["*"],
                effect=iam.Effect.ALLOW,
            ),
        )
        policy = iam.Policy(scope=scope, id=f"{id}Policy", document=iam_policy_doc)
        return policy
