from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import APIGateway, VPC
from diagrams.aws.compute import Lambda, EC2
from diagrams.aws.integration import SQS, Eventbridge
from diagrams.aws.management import Cloudwatch
from diagrams.aws.storage import SimpleStorageServiceS3
from diagrams.custom import Custom

with Diagram(outformat="png", filename="improved_github_runner_aws"):
    # init custom logos
    cc_github_app = Custom("Github App", "assets/github-logo.jpeg")

    # init webhook components
    gw = APIGateway("API Gateway")
    webhook_validator = Lambda("Webhook Validator")
    sqs = SQS("Webhook Queue")
    dead_letter_queue = SQS("DLQ")
    sqs >> dead_letter_queue

    with Cluster("VPC"):
        with Cluster("Auto Scaling"):
            asg = [EC2("Runner 1"),
                   EC2("Runner 2"),
                   EC2("Runner 3")]

        binary_updater = Lambda("Update Binary")
        scale_down = Lambda("Scale Down")

        s3 = SimpleStorageServiceS3("Runners Binaries")
        binary_updater >> s3
        scale_down >> Edge(label="Evaluates") >> asg[0]

    event_bridge = Eventbridge("EventBridge")
    event_bridge >> scale_down
    event_bridge >> binary_updater

    cloudwatch = Cloudwatch("CloudWatch Logs & Alarms")
    webhook_validator >> cloudwatch
    binary_updater >> cloudwatch
    scale_down >> cloudwatch

    # Event flow
    cc_github_app >> Edge(label="Webhook", color="black") >> gw >> webhook_validator
    webhook_validator >> Edge(label="Valid Events") >> sqs
    sqs >> Edge(label="Trigger Scaling") >> asg[1]
