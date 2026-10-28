# AWS deployment direction (not yet automated)

This starter runs locally with Docker Compose. A sensible next AWS deployment is:

- Next.js: AWS Amplify **or** an ECS Fargate service behind an Application Load Balancer.
- FastAPI: ECS Fargate service in private subnets.
- PostgreSQL: Amazon RDS for PostgreSQL in private subnets, no public access.
- Private files: S3 bucket with Block Public Access enabled and short-lived pre-signed URLs.
- Background work: SQS queue + ECS worker service; add a dead-letter queue.
- Secrets: AWS Secrets Manager, referenced by ECS task definitions.
- Images: Amazon ECR.
- Monitoring: CloudWatch logs, metrics, alarms and dashboards.
- CI/CD: GitHub Actions using AWS OIDC federation instead of long-lived AWS access keys.

## Safe order
1. Create a dedicated AWS account/environment for the project and enable MFA.
2. Set an AWS Budget and billing alerts before provisioning anything.
3. Build and scan containers locally; never commit `.env` or credentials.
4. Deploy RDS in private subnets and require TLS; restrict security groups to the API service.
5. Deploy API and frontend; configure exact CORS origins and HTTPS.
6. Put secrets in Secrets Manager and use least-privilege IAM task roles.
7. Enable backups, logs, alarms, and test restoring a backup.
8. Keep payment integrations in sandbox mode until provider approval and security/legal reviews are complete.

Costs vary by region, uptime, database sizing, networking and traffic. NAT gateways, managed databases and always-on tasks can create meaningful recurring costs. Estimate costs in the AWS Pricing Calculator and set a budget first.
