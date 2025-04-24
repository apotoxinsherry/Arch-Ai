from langchain_experimental.utilities import PythonREPL


# Create a diagram
python_repl = PythonREPL()
a="""
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.network import ELB
from diagrams.aws.database import RDS
from diagrams.onprem.client import User

with Diagram("Simple Web Service Architecture", filename="/home/anirudh/diag/web_architecture", outformat="png"):
    user = User("User")

    # Load balancer
    lb = ELB("Load Balancer")

    # Web servers
    web1 = EC2("Web Server 1")
    web2 = EC2("Web Server 2")

    # Database
    db = RDS("Database")

    # Connect the nodes
    user >> lb >> [web1, web2]
    web1 >> db
    web2 >> db
"""

python_repl.run(a)
