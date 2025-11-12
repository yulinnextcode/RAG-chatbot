#!/usr/bin/env bash
# Usage:
#   infra/scripts/deploy.sh <env> <keypair-name> <admin-cidr> <aws-profile> <region> <enable-cloudwatch>
# Example:
#   infra/scripts/deploy.sh dev my-key 203.0.113.4/32 default us-east-1 true

set -euo pipefail

if [ "$#" -lt 6 ]; then
  echo "Usage: $0 <env> <keypair-name> <admin-cidr> <aws-profile> <region> <enable-cloudwatch>"
  exit 2
fi

ENV_NAME="$1"
KEY_NAME="$2"
ADMIN_CIDR="$3"
AWS_PROFILE="$4"
AWS_REGION="$5"
ENABLE_CW="$6"   # "true" or "false"

STACK_PREFIX="${ENV_NAME}-chatbot"

NETWORK_STACK_NAME="${STACK_PREFIX}-network"
EFS_STACK_NAME="${STACK_PREFIX}-efs"
COMPUTE_STACK_NAME="${STACK_PREFIX}-compute"

TEMPLATE_DIR="$(dirname "$0")/.."
NETWORK_TEMPLATE="${TEMPLATE_DIR}/network/network-stack.yaml"
EFS_TEMPLATE="${TEMPLATE_DIR}/efs/efs-stack.yaml"
COMPUTE_TEMPLATE="${TEMPLATE_DIR}/compute/compute-stack.yaml"

echo "Deploying network stack: ${NETWORK_STACK_NAME}"
aws cloudformation deploy \
  --profile "${AWS_PROFILE}" \
  --region "${AWS_REGION}" \
  --stack-name "${NETWORK_STACK_NAME}" \
  --template-file "${NETWORK_TEMPLATE}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides EnvName="${ENV_NAME}" AdminCidr="${ADMIN_CIDR}" EnableNat=true

echo "Deploying EFS stack: ${EFS_STACK_NAME}"
aws cloudformation deploy \
  --profile "${AWS_PROFILE}" \
  --region "${AWS_REGION}" \
  --stack-name "${EFS_STACK_NAME}" \
  --template-file "${EFS_TEMPLATE}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides EnvName="${ENV_NAME}" EfsKmsKeyId=""

echo "Deploying compute stack: ${COMPUTE_STACK_NAME}"
aws cloudformation deploy \
  --profile "${AWS_PROFILE}" \
  --region "${AWS_REGION}" \
  --stack-name "${COMPUTE_STACK_NAME}" \
  --template-file "${COMPUTE_TEMPLATE}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides EnvName="${ENV_NAME}" KeyName="${KEY_NAME}" EnableCloudWatch="${ENABLE_CW}"

echo "Fetching outputs..."
aws cloudformation describe-stacks \
  --profile "${AWS_PROFILE}" \
  --region "${AWS_REGION}" \
  --stack-name "${COMPUTE_STACK_NAME}" \
  --query "Stacks[0].Outputs" --output json

echo "Done. Recommended next steps:"
echo "- If you used 'true' for EnableCloudWatch, visit CloudWatch -> Log groups and search for /${ENV_NAME}/weaviate/logs"
echo "- SSH: ssh -i <path-to-${KEY_NAME}.pem> ec2-user@<PublicIp-from-outputs>"
echo "- Or use: aws ssm start-session --target <InstanceId> --profile ${AWS_PROFILE} --region ${AWS_REGION}"