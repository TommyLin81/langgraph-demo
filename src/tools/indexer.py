from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from rich.progress import Progress

urls = [
  ## 1. AWS core concepts
  "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/introduction.html",
  "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/compute-services.html",
  "https://docs.aws.amazon.com/whitepapers/latest/introduction-devops-aws/infrastructure-as-code.html",
  "https://docs.aws.amazon.com/pricing-calculator/latest/userguide/getting-started.html",
  "https://docs.aws.amazon.com/awssupport/latest/user/getting-started.html",
  "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started.html",

  ## 2. Amazon EC2
  "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-types.html",
  "https://docs.aws.amazon.com/ec2/latest/instancetypes/instance-types.html",
  "https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-instance-type-specifications.html",
  "https://docs.aws.amazon.com/autoscaling/ec2/userguide/allocation-strategies.html",
  "https://docs.aws.amazon.com/compute-optimizer/latest/ug/view-ec2-recommendations.html",

  ## 3. AWS Lambda
  "https://docs.aws.amazon.com/lambda/latest/dg/welcome.html",
  "https://docs.aws.amazon.com/lambda/latest/dg/concepts-basics.html",
  "https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html",
  "https://docs.aws.amazon.com/lambda/latest/dg/testing-functions.html",
  "https://docs.aws.amazon.com/lambda/latest/dg/lambda-typescript.html",
  "https://docs.aws.amazon.com/serverless/latest/devguide/welcome.html",
  "https://docs.aws.amazon.com/whitepapers/latest/serverless-multi-tier-architectures-api-gateway-lambda/microservices-with-lambda.html",
  "https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-debugging.html",

  ## 4. Amazon S3
  "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html",
  "https://docs.aws.amazon.com/AmazonS3/latest/userguide/GetStartedWithS3.html",
  "https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html",
  "https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingBucket.html",
  "https://docs.aws.amazon.com/AmazonS3/latest/userguide/creating-buckets-s3.html",
  "https://docs.aws.amazon.com/AmazonS3/latest/userguide/sc-howtoset.html",
  "https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html",
  "https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-encryption.html",
  "https://docs.aws.amazon.com/solutions/latest/data-transfer-from-amazon-s3-glacier-vaults-to-amazon-s3/amazon-s3-storage-class-considerations.html",

  ## 5. Amazon RDS
  "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.DBInstance.html",
  "https://docs.aws.amazon.com/AmazonRDS/latest/gettingstartedguide/choosing-engine.html",
  "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIOPS.StorageTypes.html",
  "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html",
  "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_UpgradeDBInstance.PostgreSQL.html",
  "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_LogAccess.Concepts.PostgreSQL.html",
  "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/custom-oracle.db-architecture.html",
  "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStartedDynamoDB.html",
  "https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_DatabaseInsights.Engines.html",

  ## 6. Amazon VPC & Security Groups
  "https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Security.html",
  "https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-best-practices.html",
  "https://docs.aws.amazon.com/vpc/latest/peering/vpc-peering-security-groups.html",
  "https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-cwl.html",
  "https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/vpc.html",
  "https://docs.aws.amazon.com/eks/latest/userguide/security-groups-for-pods.html",
  "https://docs.aws.amazon.com/quicksight/latest/user/vpc-security-groups.html",
  "https://docs.aws.amazon.com/eks/latest/userguide/sec-group-reqs.html",
  "https://docs.aws.amazon.com/eks/latest/userguide/auto-networking.html",
  "https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/GettingStarted.html",

  ## 7. AWS IAM
  "https://docs.aws.amazon.com/IAM/latest/UserGuide/id.html",
  "https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html",
  "https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html",
  "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html",
  "https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_examples.html",
  "https://docs.aws.amazon.com/rolesanywhere/latest/userguide/security-iam-awsmanpol.html",
  "https://docs.aws.amazon.com/cognito/latest/developerguide/iam-roles.html",
  "https://docs.aws.amazon.com/wickr/latest/adminguide/security_iam_authentication-iamrole.html",

  ## 8. Amazon CloudWatch
  "https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html",
  "https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Install-CloudWatch-Agent.html",
  "https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CloudWatch-Logs-Monitoring-CloudWatch-Metrics.html",
  "https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/MonitoringLogData.html",
  "https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Container-Insights-setup-logs-FluentBit.html",
  "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/monitoring-cloudwatch.html",
  "https://docs.aws.amazon.com/emr/latest/ManagementGuide/enhanced-custom-metrics.html",

  ## 9. AWS CloudFormation
  "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html",
  "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/GettingStarted.html",
  "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html",
  "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-guide.html",
  "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/infrastructure-composer-for-cloudformation.html",
  "https://docs.aws.amazon.com/infrastructure-composer/latest/dg/using-composer-console-cfn-mode.html",
  "https://docs.aws.amazon.com/infrastructure-composer/latest/dg/setting-up-composer-cfn-mode.html",
  "https://docs.aws.amazon.com/solutions/latest/centralized-network-inspection-on-aws/aws-cloudformation-template.html",

  ## 10. Other
  "https://docs.aws.amazon.com/iot/latest/developerguide/iot-gs.html",
  "https://docs.aws.amazon.com/personalize/latest/dg/getting-started.html"
]

docs = []
with Progress() as progress:
    load_task = progress.add_task("Loading documents from URLs...", total=len(urls))
    
    for url in urls:
        loader = WebBaseLoader(url)
        docs.append(loader.load())
        progress.update(load_task, advance=1)

docs_list = [item for sublist in docs for item in sublist]

splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            model_name="gpt-4o-mini",
            chunk_size=1200,
            chunk_overlap=200,
            add_start_index=True,
)

doc_splits = splitter.split_documents(docs_list)

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = Chroma(
    collection_name="rag-chroma",
    embedding_function=embedding_model,
    persist_directory="./data/chromadb"
)

with Progress() as progress:
    task = progress.add_task("Adding documents to vector store...", total=len(doc_splits))
    
    batch_size = 10
    for i in range(0, len(doc_splits), batch_size):
        batch = doc_splits[i:i+batch_size]
        vector_store.add_documents(batch)
        progress.update(task, advance=len(batch))
