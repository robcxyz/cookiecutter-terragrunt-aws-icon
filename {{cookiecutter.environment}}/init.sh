#!/usr/bin/env bash
ACCOUNT_ID=$1
REMOTE_STATE_REGION=$2
LOCAL_KEY_FILE=$3
ROOT_DOMAIN_NAME=$5
CORPORATE_IP=$6
cat<<EOF > ./account.tfvars
account_id = "$ACCOUNT_ID"
aws_allowed_account_ids = ["$ACCOUNT_ID"]
terraform_state_region = "$REMOTE_STATE_REGION"
terraform_state_bucket = "terraform-states-$ACCOUNT_ID"
local_public_key = "$LOCAL_KEY_FILE.pub"
local_private_key = "$LOCAL_KEY_FILE"
local_key_file = "$LOCAL_KEY_FILE"
root_domain_name = "$ROOT_DOMAIN_NAME"
corporate_ip = "$CORPORATE_IP"
EOF
