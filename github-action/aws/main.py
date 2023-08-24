from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import APIGateway
from diagrams.aws.compute import Lambda, EC2
from diagrams.aws.integration import SimpleQueueServiceSqsQueue
from diagrams.aws.management import CloudwatchEventTimeBased
from diagrams.aws.storage import SimpleStorageServiceS3
from diagrams.custom import Custom

with Diagram(outformat="png", filename="github_runner_aws"):
    # init custom logos
    cc_github_app = Custom("Github App", "assets/github-logo.jpeg")

    # init scale up components
    gw = APIGateway("API Gateway")
    webhook = Lambda("Webhook")
    sqs = SimpleQueueServiceSqsQueue("Webhook Queue")
    runner_up = Lambda("Scale Runners up")

    with Cluster("Runners"):
        servers = [
            EC2("Runner 1"),
            EC2("Runner 2"),
            EC2("Runner 3"),
        ]

    # scale up runners
    cc_github_app >> \
    Edge(label="Webhook", color="black") >> gw >> \
    Edge(label="Post Event", color="black") >> webhook >> \
    Edge(label="Request run event") >> sqs >> \
    Edge(label="Send scale up event") >> runner_up >> \
    Edge(label="Creates", color="black") >> servers[2]

    # init scale down components
    runner_down = Lambda("Scale Runners down")
    update_binary = Lambda("Update Binary")
    scheduler = CloudwatchEventTimeBased("Scheduler")
    s3 = SimpleStorageServiceS3("Action Runners Binaries")

    # scale down runners
    runner_down >> Edge(label="Terminates", color="black") >> servers[1]
    scheduler >> runner_down
    servers[2] >> Edge(label="Download Binary", color="black") >> s3
    scheduler >> update_binary >> s3
