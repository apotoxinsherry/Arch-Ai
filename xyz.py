from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.network import ELB
from diagrams.aws.database import RDS
from diagrams.aws.storage import S3

# Define the diagram
with Diagram("Simple Web Application Architecture", filename="architecture_diagram", show=False):
    # Define the components
    load_balancer = ELB("Load Balancer")
    web_server = EC2("Web Server")
    database = RDS("Database")
    cache = S3("Cache")

    # Define connections
    load_balancer >> web_server
    load_balancer >> database
    load_balancer >> cache
