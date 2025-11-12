```markdown
# infra/ — CloudFormation stacks for RAG-CHATBOT

Recommended layout (repo root):
- infra/
  - network/network-stack.yaml        # VPC, subnets, IGW, NATs, EC2 SG (exports)
  - efs/efs-stack.yaml                # EFS FS, mount targets, EFS SG (imports network exports)
  - compute/compute-stack.yaml        # EC2 instance, IAM role, user-data mounts EFS & starts Weaviate
  - scripts/deploy.sh                 # Deployment helper script (make executable)
  - README.md                         # This file

Before you start (local machine):
1. Install AWS CLI v2 (https://aws.amazon.com/cli/) and configure a profile:
   - aws configure --profile my-profile
     (Enter AWS Access Key ID, Secret, region, output format)
2. Ensure you have an EC2 KeyPair in the target region (for SSH). Create one in the console if needed.
3. Optionally install jq (useful): apt/yum/brew install jq
4. Ensure you have permission to create CloudFormation stacks, IAM instance profiles, EFS, EC2, CloudWatch resources.

Basic deployment steps (quick):
1. Make the script executable:
   chmod +x infra/scripts/deploy.sh
2. Deploy stacks:
   infra/scripts/deploy.sh dev my-key 203.0.113.4/32 my-profile us-east-1 true

That command will:
- Deploy network stack (exports VPC, subnet IDs, EC2 SG)
- Deploy EFS stack (imports VPC/subnet/SG exports, creates EFS)
- Deploy compute stack (imports EFS FileSystemId & SG, creates EC2, mounts EFS, starts Weaviate container)

Verification checklist (after compute stack completes):
- Get outputs printed by the script (InstanceId, PublicIp).
- Connect via SSM (preferred) or SSH:
  - SSM: aws ssm start-session --target <InstanceId> --profile my-profile --region us-east-1
  - SSH: ssh -i ~/.ssh/my-key.pem ec2-user@<PublicIp>
- On instance:
  - df -h | grep /mnt/efs
  - ls -l /mnt/efs/weaviate_data
  - docker ps
  - docker-compose -f /var/lib/weaviate/docker-compose.yml ps
  - curl http://localhost:8080/v1/.well-known/ready

If you set EnableCloudWatch=true:
- Container logs: CloudWatch → Log groups → /<env>/weaviate/logs
- Host metrics: CloudWatch metrics (mem, cpu) reported by CloudWatch Agent

Stack update & delete:
- Update: run the deploy script again with updated templates/parameters.
- Delete: delete compute, efs, then network stacks (reverse order). Example:
  aws cloudformation delete-stack --stack-name dev-chatbot-compute --profile my-profile --region us-east-1

Troubleshooting common problems:
- ImportValue not found: confirm same EnvName across stacks and that exports exist (check CloudFormation outputs/exports).
- CAPABILITY_NAMED_IAM error: include --capabilities CAPABILITY_NAMED_IAM when deploying.
- Missing KeyPair: create or specify a KeyPair name in the same region.
- EFS mount failing: verify security groups allow port 2049 between EC2 SG and EFS SG; check EFS mount targets exist in same subnets/AZs.
- SSM not working: ensure instance role includes AmazonSSMManagedInstanceCore and instance has internet access (NAT/IGW) or uses SSM VPC endpoints.

Advanced: run stacks individually with explicit commands:
- Validate template:
  aws cloudformation validate-template --template-body file://infra/network/network-stack.yaml
- Deploy a single stack:
  aws cloudformation deploy --stack-name dev-chatbot-network --template-file infra/network/network-stack.yaml --parameter-overrides EnvName=dev AdminCidr=203.0.113.4/32 EnableNat=true --capabilities CAPABILITY_NAMED_IAM --profile my-profile --region us-east-1

Cleanup:
- Delete compute then efs then network stacks:
  aws cloudformation delete-stack --stack-name dev-chatbot-compute --profile my-profile --region us-east-1
  aws cloudformation wait stack-delete-complete --stack-name dev-chatbot-compute --profile my-profile --region us-east-1
  (repeat for other stacks)
```