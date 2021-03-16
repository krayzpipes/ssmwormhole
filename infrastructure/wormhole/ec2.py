"""CDK Stack to deploy wormhole EC2 server in an autoscaling group."""

from aws_cdk import core as cdk
from aws_cdk import aws_autoscaling as asg, aws_ec2 as ec2, aws_iam as iam


class Ec2Stack(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, id: str, ssh_key_name: str, vpc: ec2.IVpc
    ) -> None:

        super().__init__(scope=scope, id=id)

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

        # Launch template that the AutoScaling Group will use to
        # spin up new/replacement instances.
        launch_template = ec2.LaunchTemplate(
            self,
            f'{id}LaunchTemplate',
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            instance_type=ec2.InstanceType("t3a.micro"),
            key_name=ssh_key_name,
            role=self.iam_role,
            instance_initiated_shutdown_behavior=ec2.InstanceInitiatedShutdownBehavior.TERMINATE,
            security_group=ec2.SecurityGroup(
                self, f'{id}SG', vpc=vpc, allow_all_outbound=True
            )
        )

        # The AutoScaling Group configuration.
        self.asg_ = asg.CfnAutoScalingGroup(
            self,
            f'{id}Asg',
            min_size="1",
            max_size="2",
            desired_capacity="1",
            launch_template=asg.CfnAutoScalingGroup.LaunchTemplateSpecificationProperty(
                version=launch_template.latest_version_number,
                launch_template_id=launch_template.launch_template_id,
                launch_template_name=launch_template.launch_template_name,
            ),
            # This tag will be used to find the running instance
            # that can be used for ssm wormhole.
            tags=[
                asg.CfnAutoScalingGroup.TagPropertyProperty(
                    key="ec2:purpose", propagate_at_launch=True, value="wormhole"
                )
            ],
            vpc_zone_identifier=[subnet.subnet_id for subnet in vpc.private_subnets],
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
