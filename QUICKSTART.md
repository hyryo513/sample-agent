# Quick Start Guide

## What Was Changed?

Your sample-agent workspace has been fully migrated from LangGraph to Strands SDK with AWS Lambda CI/CD pipeline support.

## Key Files to Review

1. **[IMPLEMENTATION.md](IMPLEMENTATION.md)** — Complete change summary (start here)
2. **[MIGRATION.md](MIGRATION.md)** — Architecture & deployment guide
3. **[AWS_GITHUB_SETUP.md](AWS_GITHUB_SETUP.md)** — AWS + GitHub configuration

## What You Get

### ✅ Strands-Based Agents
- `agent-alpha`: Simple Strands agent with lib1 integration
- `agent-beta`: Full-featured agent with AgentCore HTTP client
- Both validate configuration at Lambda cold start (12-factor principles)

### ✅ Lambda Deployment Packages
- Build script: `python build_lambda.py agent-alpha`
- Output: `agent-alpha-v1.0.0.zip` (ready for AWS Lambda)
- Includes bundled dependencies + lib1 shared library

### ✅ GitHub Actions CI/CD Pipeline
- Trigger: Push git tag `agent-alpha-v1.0.0`
- Pipeline: Test → Build Lambda zip → GitHub Release → S3 upload (optional)
- Per-package semantic versioning support

## Quick Commands

### Local Development
```bash
# Install dependencies
uv sync

# Build Lambda package locally
python build_lambda.py agent-alpha

# Run tests
uv run pytest -v
```

### Release & Deploy
```bash
# Tag and push for automated build
git tag agent-alpha-v1.0.0
git push origin agent-alpha-v1.0.0

# Watch workflow
# Settings → Actions → build-lambda-packages.yml

# Download artifact from GitHub Releases or S3
# Deploy to AWS Lambda (manual or automated)
```

### Deploy to AWS Lambda (CLI)
```bash
# Download artifact
aws s3 cp s3://my-bucket/agent-alpha-v1.0.0.zip ./

# Update Lambda function
aws lambda update-function-code \
  --function-name agent-alpha \
  --zip-file fileb://agent-alpha-v1.0.0.zip

# Set environment variables
aws lambda update-function-configuration \
  --function-name agent-alpha \
  --environment Variables='{
    AGENT_NAME=agent-alpha,
    AGENTCORE_ENDPOINT=https://...,
    AGENTCORE_API_KEY=...
  }'
```

## Configuration Checklist

### Before First Release

- [ ] Review agent code in `packages/agent-{alpha,beta}/src/`
- [ ] Update `pyproject.toml` version numbers (for git tags)
- [ ] Run `uv run pytest -v` locally
- [ ] Test build locally: `python build_lambda.py agent-alpha`

### Before Using GitHub Actions

- [ ] Create AWS IAM user (for S3 + Lambda access)
- [ ] Create S3 bucket for artifacts
- [ ] Add GitHub Secrets (AWS_REGION, S3_BUCKET_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
- [ ] Create Lambda functions in AWS (optional, if automated updates enabled)

See [AWS_GITHUB_SETUP.md](AWS_GITHUB_SETUP.md) for detailed steps.

## File Structure

```
sample-agent/
├── .github/
│   └── workflows/
│       └── build-lambda-packages.yml    # CI/CD pipeline
├── packages/
│   ├── agent-alpha/
│   │   ├── src/
│   │   │   ├── agent_alpha.py           # Strands agent logic
│   │   │   └── lambda_handler.py        # AWS Lambda handler
│   │   ├── tests/
│   │   └── pyproject.toml
│   ├── agent-beta/
│   │   ├── src/
│   │   │   ├── agent_beta.py            # Strands agent + AgentCore client
│   │   │   └── lambda_handler.py        # AWS Lambda handler
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── lib1/
│       ├── src/
│       │   └── lib1.py                  # Config validation (12-factor)
│       ├── tests/
│       └── pyproject.toml
├── build_lambda.py                      # Local build script
├── pyproject.toml                       # Workspace config (Python 3.12+)
├── IMPLEMENTATION.md                    # Complete change log
├── MIGRATION.md                         # Architecture guide
├── AWS_GITHUB_SETUP.md                  # AWS configuration
└── README.md
```

## Testing Locally

```bash
# Install workspace
uv sync

# Run all tests
uv run pytest -v

# Run specific package tests
uv run pytest -v packages/agent-alpha/tests/

# Build Lambda package
python build_lambda.py agent-alpha

# Inspect zip contents
unzip -l agent-alpha-v0.0.0.zip | head -20
```

## What's Different from LangGraph?

| Aspect | Before | After |
|--------|--------|-------|
| **Framework** | LangGraph | Strands SDK |
| **Config** | Dataclass | Pydantic (12-factor) |
| **Python** | 3.13+ | 3.12+ |
| **Lambda Packaging** | Manual | Automated (GitHub Actions) |
| **Validation** | Runtime | Cold-start (Lambda init) |

## Lambda Handler Signature

Both agents expose this handler for AWS Lambda:

```python
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # Input event example:
    # {"message": "test input"}
    
    # Output response:
    # {
    #   "statusCode": 200,
    #   "headers": {"Content-Type": "application/json"},
    #   "body": json.dumps({...})
    # }
```

## Environment Variables (AWS Lambda)

**Required:**
```
AGENT_NAME=agent-alpha    # Agent identifier
```

**Optional:**
```
AGENTCORE_ENDPOINT=https://...  # Platform endpoint (agent-beta)
AGENTCORE_API_KEY=<token>       # Platform auth (agent-beta)
```

## Next Steps

1. **Review Changes**: Read [IMPLEMENTATION.md](IMPLEMENTATION.md)
2. **Test Locally**: `python build_lambda.py agent-alpha`
3. **Configure AWS**: Follow [AWS_GITHUB_SETUP.md](AWS_GITHUB_SETUP.md)
4. **Push Release**: Create git tag `agent-alpha-v1.0.0`
5. **Deploy**: Download artifact and update Lambda function

## Support

For detailed information on each topic, see:
- **Architecture & Deployment**: [MIGRATION.md](MIGRATION.md)
- **AWS Configuration**: [AWS_GITHUB_SETUP.md](AWS_GITHUB_SETUP.md)
- **Complete Changes**: [IMPLEMENTATION.md](IMPLEMENTATION.md)

---

**Migration Complete** ✅ January 19, 2026
