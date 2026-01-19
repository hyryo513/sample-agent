# Strands-Based Agents with AWS Lambda Deployment

This repository contains Strands SDK-based AI agents designed for AWS Lambda deployment with AgentCore platform integration. The project uses a monorepo structure with per-package semantic versioning and automated CI/CD pipeline via GitHub Actions.

## Project Structure

```
sample-agent/
├── packages/
│   ├── agent-alpha/          # Simple Strands agent
│   │   ├── src/
│   │   │   ├── agent_alpha.py      # Agent logic (Strands-based)
│   │   │   └── lambda_handler.py   # AWS Lambda handler
│   │   └── tests/
│   │       └── test_agent_alpha.py
│   ├── agent-beta/           # Full-featured Strands agent with AgentCore
│   │   ├── src/
│   │   │   ├── agent_beta.py       # Agent logic + AgentCore client
│   │   │   └── lambda_handler.py   # AWS Lambda handler
│   │   └── tests/
│   │       └── test_runner.py
│   └── lib1/                 # Shared utilities (config validation)
│       ├── src/
│       │   └── lib1.py       # Pydantic models for 12-factor config
│       └── tests/
│           └── test_lib1.py
├── .github/workflows/
│   └── build-lambda-packages.yml  # CI/CD pipeline
├── build_lambda.py           # Lambda packaging build script
├── pyproject.toml            # Workspace config (Python 3.12+)
└── README.md
```

## Architecture Overview

### Agents

Both agents follow a Strands SDK-based architecture with:

- **Cold-start validation**: Environment variables validated at Lambda initialization (12-factor principles)
- **AgentCore integration**: HTTP client for posting agent responses
- **Lambda-ready handlers**: AWS Lambda entry points with JSON request/response handling
- **Shared config**: Pydantic models from `lib1` for environment validation

```
┌──────────────┐
│ Lambda Event │
└──────┬───────┘
       │
       ▼
┌─────────────────────────┐
│ lambda_handler.py       │
│ (cold-start validation) │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐      ┌──────────────────┐
│ Strands Agent           │      │ AgentCore Client │
│ (invoke logic)          │──────►(HTTP POST)       │
└─────────────────────────┘      └──────────────────┘
```

### Configuration (12-Factor)

All configuration is environment-driven:

```
AGENT_NAME               # Agent identifier (default: package name)
AGENTCORE_ENDPOINT       # HTTP endpoint for posting responses
AGENTCORE_API_KEY        # Bearer token for API authentication
```

Validation occurs at Lambda cold start using `lib1.AgentConfig` pydantic model.

## Migration from LangGraph to Strands

### Key Changes

| Aspect | LangGraph | Strands |
|--------|-----------|---------|
| **Agent Framework** | `langgraph.Agent` | `strands-sdk` |
| **Configuration** | Dataclass | Pydantic `BaseModel` |
| **Dependencies** | `langgraph>=0.0.1` | `strands-sdk>=0.1.0` |
| **Python** | >=3.13 | >=3.12 |

### Agent API Changes

**Before (LangGraph):**
```python
from agent_beta import run

out = run()
```

**After (Strands):**
```python
from lib1 import AgentConfig
from agent_beta import create_agent_components, run_once

config = AgentConfig.from_env()
comps = create_agent_components(config)
result = run_once(comps, message="hello")
```

## Building Lambda Packages

### Using Python Script (Local)

```bash
# Build agent-alpha Lambda package
python build_lambda.py agent-alpha

# Build with explicit version
python build_lambda.py agent-alpha 1.0.0

# Output: agent-alpha-v1.0.0.zip (ready for AWS Lambda)
```

### Using GitHub Actions (Recommended)

**Tag and push per-package semantic version:**

```bash
git tag agent-alpha-v1.0.0
git push origin agent-alpha-v1.0.0
```

**Triggers:**
- Runs pytest across all packages
- Builds `agent-alpha-v1.0.0.zip`
- Uploads to GitHub Releases
- Optional: Uploads to S3 (if AWS credentials configured)

## GitHub Actions CI/CD Pipeline

### Workflow: `build-lambda-packages.yml`

**Triggers:**
- Git tags matching pattern: `agent-{alpha|beta}-v{semver}`
- Manual workflow dispatch

**Steps:**

1. **Parse Tag** — Extract package name and version from git tag
2. **Test** — Run pytest on all packages
3. **Build Agent** — Create Lambda deployment zip with bundled dependencies
4. **Upload Artifact** — Store zip in GitHub Actions artifacts
5. **Create Release** — Publish zip to GitHub Releases (git tag builds only)
6. **S3 Upload** — Optional: Upload to S3 bucket (if AWS credentials configured)
7. **Lambda Update** — Optional: Automated Lambda function update (disabled by default)

### Configuration

**GitHub Secrets Required:**

```
AWS_REGION              # e.g., us-east-1
S3_BUCKET_NAME          # e.g., my-lambda-artifacts-bucket
AWS_ACCESS_KEY_ID       # IAM user credentials
AWS_SECRET_ACCESS_KEY   # IAM user credentials
```

Optional for S3 + Lambda updates. Workflow still succeeds without them (artifacts available in GitHub Releases).

## Deployment to AWS Lambda

### Option 1: Manual Deployment (via AWS Console)

1. Download agent zip from GitHub Releases
2. Create Lambda function (Python 3.12 runtime)
3. Upload zip as function code
4. Set handler: `lambda_handler.lambda_handler`
5. Configure environment variables:
   ```
   AGENT_NAME=agent-alpha
   AGENTCORE_ENDPOINT=https://agentcore.example.com/api/events
   AGENTCORE_API_KEY=<bearer-token>
   ```

### Option 2: AWS CLI

```bash
# Download artifact
aws s3 cp s3://my-bucket/agent-alpha-v1.0.0.zip ./

# Create function
aws lambda create-function \
  --function-name agent-alpha \
  --runtime python3.12 \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://agent-alpha-v1.0.0.zip \
  --environment Variables="{AGENT_NAME=agent-alpha,AGENTCORE_ENDPOINT=https://...}"

# Update function code
aws lambda update-function-code \
  --function-name agent-alpha \
  --zip-file fileb://agent-alpha-v1.0.1.zip
```

### Option 3: Automated CI/CD (GitHub Actions)

Configure in workflow:
```yaml
AWS_ACCOUNT_ID=123456789012
AWS_REGION=us-east-1
S3_BUCKET_NAME=lambda-artifacts
AWS_ACCESS_KEY_ID=<from secrets>
AWS_SECRET_ACCESS_KEY=<from secrets>
```

Workflow automatically:
- Uploads zip to S3
- Can update Lambda function (uncomment step in workflow)

## Testing

Run all tests:

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest -v

# Test specific package
uv run pytest -v packages/agent-alpha/tests/
```

## Development

### Add New Agent

1. Create new package:
   ```bash
   mkdir -p packages/agent-gamma/src packages/agent-gamma/tests
   ```

2. Create `pyproject.toml`:
   ```toml
   [project]
   name = "agent-gamma"
   version = "0.0.0"
   requires-python = ">=3.12"
   dependencies = ["strands-sdk>=0.1.0", "pydantic>=2.0", "lib1>=0.0.0"]
   ```

3. Implement agent in `src/agent_gamma.py` and `src/lambda_handler.py`

4. Add to workspace `pyproject.toml`:
   ```toml
   [tool.uv.workspace]
   members = ["packages/*"]  # Already configured
   ```

### Local Build & Test

```bash
# Install workspace
uv sync

# Build specific agent
python build_lambda.py agent-gamma 0.1.0

# Test before tagging
uv run pytest -v packages/agent-gamma/tests/
```

## Artifact Outputs

### Lambda Zip Contents

```
agent-alpha-v1.0.0.zip
├── agent_alpha.py
├── lambda_handler.py
├── lib1.py                      # Bundled shared library
├── pydantic/                    # Dependencies
├── strands/
├── boto3/
└── ...
```

**Size:** Typically 5-20 MB (depends on Strands SDK + dependencies)

**Handler:** `lambda_handler.lambda_handler`

**Timeout:** Recommended 30s+ (for HTTP calls to AgentCore)

**Memory:** Recommended 256+ MB

## Advanced Configuration

### Custom Lambda Layer (Instead of Bundling)

To reduce zip size, package lib1 and common dependencies as Lambda Layer:

```bash
pip install -t python/lib strands-sdk pydantic requests

zip -r lib1-layer.zip python/

aws lambda publish-layer-version \
  --layer-name agent-common \
  --zip-file fileb://lib1-layer.zip \
  --compatible-runtimes python3.12
```

Then reference in Lambda function (AWS Console or CloudFormation).

### Environment Variable Validation Errors

If Lambda cold-start fails:

1. Check CloudWatch Logs for validation errors
2. Ensure `AGENT_NAME` is set and non-empty
3. Validate `AGENTCORE_ENDPOINT` format (if used)
4. Verify IAM role has required permissions (if posting to AgentCore)

## Monitoring & Debugging

### CloudWatch Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/agent-alpha --follow

# View specific request
aws logs filter-log-events \
  --log-group-name /aws/lambda/agent-alpha \
  --filter-pattern "ERROR"
```

### Local Testing

```python
# Simulate Lambda invocation locally
from lambda_handler import lambda_handler

event = {"message": "test"}
context = type('obj', (object,), {'function_name': 'agent-alpha'})()

response = lambda_handler(event, context)
print(response)
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cold-start initialization failed" | Check env vars (AGENT_NAME required) |
| "AgentCore send failed" | Verify AGENTCORE_ENDPOINT + AGENTCORE_API_KEY |
| "Module not found: lib1" | Ensure lib1 bundled in zip (check build script) |
| "Lambda timeout" | Increase timeout (AgentCore HTTP calls may be slow) |
| "Strands SDK not available" | Verify pip install in Lambda zip |

## Future Enhancements

- [ ] Strands workflow orchestration at agent level (currently platform-owned)
- [ ] CloudFormation templates for Lambda + IAM setup
- [ ] Lambda layer support for lib1 + dependencies
- [ ] GitOps deployment via ArgoCD or Flux
- [ ] Metrics export to CloudWatch (agent invocation counts, latency)

## References

- [Strands SDK Documentation](https://strands.com/docs)
- [AWS Lambda Python Runtime](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html)
- [12-Factor App Config](https://12factor.net/config)
- [Pydantic Documentation](https://docs.pydantic.dev)

## License

(Add your license here)
