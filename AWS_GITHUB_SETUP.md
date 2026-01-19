# AWS & GitHub Configuration Guide

This guide helps configure GitHub Secrets and AWS resources for automated Lambda deployment pipeline.

## GitHub Secrets Setup

### Step 1: Create GitHub Secrets

Navigate to: **Settings → Secrets and variables → Actions**

Add the following secrets (required for S3 + Lambda deployment):

| Secret Name | Value | Example |
|------------|-------|---------|
| `AWS_REGION` | AWS region for S3 + Lambda | `us-east-1` |
| `S3_BUCKET_NAME` | S3 bucket for Lambda artifacts | `my-org-lambda-artifacts` |
| `AWS_ACCESS_KEY_ID` | IAM user access key | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key | (keep secure) |

### Step 2: Create IAM User for CI/CD

```bash
# Create IAM user
aws iam create-user --user-name github-actions-lambda-builder

# Create access key
aws iam create-access-key --user-name github-actions-lambda-builder
```

Save the `AccessKeyId` and `SecretAccessKey` → Add to GitHub Secrets above.

### Step 3: Attach IAM Policies

Option A: **Restrictive Policy** (Recommended)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3ArtifactsBucket",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-org-lambda-artifacts",
        "arn:aws:s3:::my-org-lambda-artifacts/*"
      ]
    },
    {
      "Sid": "LambdaFunctionUpdate",
      "Effect": "Allow",
      "Action": [
        "lambda:UpdateFunctionCode",
        "lambda:GetFunction"
      ],
      "Resource": [
        "arn:aws:lambda:us-east-1:123456789012:function:agent-alpha",
        "arn:aws:lambda:us-east-1:123456789012:function:agent-beta"
      ]
    }
  ]
}
```

Option B: **Full S3 + Lambda Access** (Less secure, easier setup)

```bash
aws iam attach-user-policy \
  --user-name github-actions-lambda-builder \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-user-policy \
  --user-name github-actions-lambda-builder \
  --policy-arn arn:aws:iam::aws:policy/AWSLambdaFullAccess
```

## S3 Bucket Setup

### Create S3 Bucket for Lambda Artifacts

```bash
# Create bucket
aws s3 mb s3://my-org-lambda-artifacts --region us-east-1

# Enable versioning (optional, for artifact history)
aws s3api put-bucket-versioning \
  --bucket my-org-lambda-artifacts \
  --versioning-configuration Status=Enabled

# Block public access (security)
aws s3api put-public-access-block \
  --bucket my-org-lambda-artifacts \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Optional: Set lifecycle rule to delete old artifacts after 90 days
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-org-lambda-artifacts \
  --lifecycle-configuration file://lifecycle.json
```

**lifecycle.json:**
```json
{
  "Rules": [
    {
      "ID": "DeleteOldArtifacts",
      "Status": "Enabled",
      "Prefix": "",
      "Expiration": {
        "Days": 90
      }
    }
  ]
}
```

## Lambda Function Setup

### Pre-Create Lambda Functions (Optional)

If using automated Lambda updates in workflow, pre-create functions:

```bash
# Create agent-alpha function
aws lambda create-function \
  --function-name agent-alpha \
  --runtime python3.12 \
  --role arn:aws:iam::123456789012:role/lambda-execution-role \
  --handler lambda_handler.lambda_handler \
  --timeout 30 \
  --memory-size 256 \
  --environment Variables='{
    AGENT_NAME=agent-alpha,
    AGENTCORE_ENDPOINT=https://agentcore.example.com/api/events,
    AGENTCORE_API_KEY=<bearer-token>
  }' \
  --zip-file fileb://agent-alpha-initial.zip

# Create agent-beta function
aws lambda create-function \
  --function-name agent-beta \
  --runtime python3.12 \
  --role arn:aws:iam::123456789012:role/lambda-execution-role \
  --handler lambda_handler.lambda_handler \
  --timeout 30 \
  --memory-size 256 \
  --environment Variables='{
    AGENT_NAME=agent-beta,
    AGENTCORE_ENDPOINT=https://agentcore.example.com/api/events,
    AGENTCORE_API_KEY=<bearer-token>
  }' \
  --zip-file fileb://agent-beta-initial.zip
```

### Create Lambda Execution IAM Role

```bash
# Create role
aws iam create-role \
  --role-name lambda-execution-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "lambda.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }'

# Attach basic execution policy
aws iam attach-role-policy \
  --role-name lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Attach CloudWatch logs policy (for logging)
aws iam attach-role-policy \
  --role-name lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess
```

## GitHub Actions Workflow Configuration

### Minimal Configuration (GitHub Releases only)

No secrets needed. Workflow will:
- Run tests
- Build Lambda zips
- Upload to GitHub Releases (git tag builds)

Artifacts available for manual download and deployment.

### Production Configuration (GitHub Releases + S3 + Lambda)

Add all secrets from Step 1 above. Workflow will additionally:
- Upload artifacts to S3
- Optionally update Lambda functions (uncomment step in workflow)

## Testing the Pipeline

### Local Test (Build Only)

```bash
# Build agent-alpha locally
python build_lambda.py agent-alpha 0.1.0

# Verify zip was created
ls -lh agent-alpha-v0.1.0.zip
```

### GitHub Actions Test (Minimal)

```bash
# Push a test tag (no S3/Lambda setup required)
git tag agent-alpha-v0.1.0
git push origin agent-alpha-v0.1.0

# Watch workflow run
# Settings → Actions → build-lambda-packages.yml
# Download artifact from run summary
```

### Full Pipeline Test (With AWS)

```bash
# Configure GitHub Secrets (Step 1 above)
# Create S3 bucket (S3 Bucket Setup above)

# Push tag to trigger workflow
git tag agent-alpha-v0.2.0
git push origin agent-alpha-v0.2.0

# Verify artifact uploaded to S3
aws s3 ls s3://my-org-lambda-artifacts/ --recursive
```

## Environment Variables for Lambda Functions

### Required

Set these in Lambda function configuration:

```
AGENT_NAME=agent-alpha                    # Agent identifier
AGENTCORE_ENDPOINT=https://...            # Platform endpoint
AGENTCORE_API_KEY=<bearer-token>          # Platform auth (optional)
```

### Optional

```
AWS_REGION=us-east-1                      # For boto3 calls (if needed)
LOG_LEVEL=INFO                            # For logging (DEBUG, INFO, WARN, ERROR)
```

## Troubleshooting

### Workflow Fails: "Secrets not found"

**Cause**: GitHub Secrets not configured
**Solution**: Add `AWS_REGION` and `S3_BUCKET_NAME` to Settings → Secrets

### Workflow Fails: "Access Denied" to S3

**Cause**: IAM policy too restrictive or credentials invalid
**Solution**: 
1. Verify `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in Secrets
2. Attach appropriate IAM policy to user (see IAM Policies above)
3. Verify user has S3 access: `aws s3 ls --profile github-actions`

### Lambda Fails at Cold Start: "Agent initialization failed"

**Cause**: Missing or invalid environment variables
**Solution**:
1. Check CloudWatch logs: `aws logs tail /aws/lambda/agent-alpha --follow`
2. Verify `AGENT_NAME` is set (required, non-empty)
3. Verify `AGENTCORE_ENDPOINT` format if used

### S3 Upload Works but Lambda Update Fails

**Cause**: IAM policy missing `lambda:UpdateFunctionCode`
**Solution**: Attach Lambda policy to IAM user (see IAM Policies above)

## Security Best Practices

1. **Rotate IAM Keys Regularly**
   ```bash
   # Generate new key pair every 90 days
   aws iam create-access-key --user-name github-actions-lambda-builder
   aws iam delete-access-key --user-name github-actions-lambda-builder --access-key-id AKIA...
   ```

2. **Restrict IAM Policy to Specific S3 Bucket + Lambda Functions**
   - Use Resource ARNs to limit scope (see Restrictive Policy above)

3. **Enable S3 Bucket Versioning + Encryption**
   ```bash
   aws s3api put-bucket-encryption \
     --bucket my-org-lambda-artifacts \
     --server-side-encryption-configuration '{
       "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
     }'
   ```

4. **Monitor IAM User Activity**
   ```bash
   # View access key usage
   aws iam get-access-key-last-used --access-key-id AKIA...
   ```

5. **Rotate GitHub Secrets if Exposed**
   - Delete old IAM access key
   - Create new key pair
   - Update GitHub Secrets

## Cost Estimation

**AWS Resource Costs (per month, US East 1):**

| Resource | Usage | Cost |
|----------|-------|------|
| S3 | 100 artifacts × 10MB | $0.50 |
| Lambda | 1000 invocations × 1s | $0.21 |
| CloudWatch Logs | 100GB | $5.00 |
| **Total** | Minimal | **~$6/month** |

Note: Agent artifacts (10-20MB) cost ~$0.01/month in S3. Lambda execution costs depend on actual invocations.

## CI/CD Pipeline Status Checks

Configure branch protection rules to require workflow success:

1. **Settings → Branches → Add rule**
2. **Branch name pattern**: `main` (or your default branch)
3. **Require status checks to pass before merging**:
   - ✓ build-lambda-packages / test
   - ✓ (optional) build-lambda-packages / build-agent

This ensures tests pass before merging code changes.

---

**Last Updated**: January 19, 2026
