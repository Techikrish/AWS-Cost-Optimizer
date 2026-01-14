# AWS Cost Optimizer 💰

A powerful full-stack application that helps optimize AWS costs using 15 advanced cost-reduction techniques. Built with Python/Flask backend and React frontend.

## Features ✨

### 🔐 Security & Credential Management
- **Encrypted Local Storage** - AWS credentials are encrypted using Fernet encryption
- **Secure Validation** - Validates credentials before saving
- **Safe by Default** - Dry-run mode enabled by default for all operations
- **No Remote Storage** - Credentials never leave your machine

### 📊 Analysis & Reporting
- **15 Optimization Techniques** - Comprehensive cost-saving strategies
- **Visual Analytics** - Interactive charts and detailed breakdowns
- **Real-time Progress** - See analysis progress as it happens
- **Export Reports** - Download findings as JSON or CSV

### 🛡️ Safe Operations
- **Confirmation Dialogs** - Review resource details before deletion
- **Dry-Run Mode** - Preview changes before executing
- **Resource Details** - View complete information before any action
- **Detailed Error Messages** - Know exactly what went wrong

## 15 Optimization Techniques

1. **Remove Unused EBS Volumes** - Deletes unattached EBS volumes (~$0.10/GB-month)
2. **Remove Unused EC2 Snapshots** - Cleans up old snapshots not associated with AMIs (~$0.05/GB-month)
3. **Terminate Stopped EC2 Instances** - Removes instances stopped for extended periods (~$0.05/hour average)
4. **Delete Unattached Elastic IPs** - Releases unused Elastic IPs (~$3.65/month each)
5. **Remove Unused Load Balancers** - Deletes load balancers with no active targets (~$22.86-32.40/month)
6. **Delete Old/Unused AMIs** - Removes AMI images not in use (~$1.00/month per snapshot)
7. **Remove Unused Security Groups** - Cleans up unused security groups (no direct cost)
8. **Delete Unused NAT Gateways** - Removes NAT Gateways not being used (~$42.80/month)
9. **Remove Unused RDS Snapshots** - Deletes old RDS snapshots (~$0.095/GB-month)
10. **Delete Unused EFS** - Removes EFS with no mount targets (~$0.30/GB-month)
11. **Remove Unused CloudWatch Log Groups** - Cleans up inactive log groups (~$0.50/GB-month)
12. **Delete Empty S3 Buckets** - Removes empty S3 buckets (minimal storage cost)
13. **Terminate Unused Elastic Beanstalk Environments** - Cleans up terminated environments (~$20/month)
14. **Remove Unused VPC Endpoints** - Deletes unused VPC endpoints (~$14.40/month)
15. **Delete Unused ECS Task Definitions** - Removes inactive task definitions (no direct cost)

## Project Structure

```
aws-cost-optimizer/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── credential_manager.py
│   │   └── routes.py
│   ├── optimizers/
│   │   ├── base_optimizer.py
│   │   ├── ebs_optimizer.py
│   │   ├── ec2_snapshot_optimizer.py
│   │   ├── ec2_instance_optimizer.py
│   │   ├── elastic_ip_optimizer.py
│   │   ├── load_balancer_optimizer.py
│   │   ├── ami_optimizer.py
│   │   ├── security_group_optimizer.py
│   │   ├── nat_gateway_optimizer.py
│   │   ├── rds_snapshot_optimizer.py
│   │   ├── efs_optimizer.py
│   │   ├── cloudwatch_logs_optimizer.py
│   │   ├── s3_bucket_optimizer.py
│   │   ├── elastic_beanstalk_optimizer.py
│   │   ├── vpc_endpoint_optimizer.py
│   │   └── ecs_task_definition_optimizer.py
│   ├── main.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Header.jsx
    │   │   ├── CredentialForm.jsx
    │   │   ├── TechniqueCard.jsx
    │   │   ├── AnalysisResults.jsx
    │   │   └── ResourceList.jsx
    │   ├── App.jsx
    │   ├── App.css
    │   ├── index.css
    │   └── main.jsx
    ├── index.html
    ├── vite.config.js
    └── package.json
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- AWS Account with IAM credentials
- pip and npm/yarn

### Backend Setup

1. **Install Python dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Create a Python virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Run the Flask backend:**
```bash
python main.py
```
The backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Install Node dependencies:**
```bash
cd frontend
npm install
```

2. **Start the development server:**
```bash
npm run dev
```
The frontend will automatically open at `http://localhost:3000`

## AWS Credentials Setup

### Create IAM User (Recommended)
For security, create a dedicated IAM user with minimal required permissions:

1. Go to AWS IAM Console
2. Create a new IAM user
3. Attach this policy (modify as needed for your use case):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "ec2:DeleteVolume",
        "ec2:DeleteSnapshot",
        "ec2:TerminateInstances",
        "ec2:ReleaseAddress",
        "ec2:DeleteSecurityGroup",
        "elasticloadbalancing:Describe*",
        "elasticloadbalancing:DeleteLoadBalancer",
        "rds:Describe*",
        "rds:DeleteDBSnapshot",
        "efs:Describe*",
        "efs:DeleteFileSystem",
        "logs:Describe*",
        "logs:DeleteLogGroup",
        "s3:ListBucket",
        "s3:DeleteBucket",
        "sts:GetCallerIdentity",
        "elasticbeanstalk:Describe*",
        "elasticbeanstalk:TerminateEnvironment",
        "ecs:List*",
        "ecs:Describe*",
        "ecs:DeregisterTaskDefinition"
      ],
      "Resource": "*"
    }
  ]
}
```

4. Generate Access Key and Secret Key
5. Use these credentials in the application

## Usage Guide

### Step 1: Connect AWS Account
1. Launch the application
2. Enter your AWS Access Key ID and Secret Key
3. Select your AWS region
4. Click "Connect AWS Account"

### Step 2: Select Optimization Technique
1. View all 15 available optimization techniques
2. Click "Analyze" on the technique you want to analyze
3. Wait for analysis to complete

### Step 3: Review Findings
1. Browse through identified resources
2. See estimated monthly savings for each resource
3. View detailed resource information

### Step 4: Execute Optimization
1. **Dry-Run Mode (Default)**
   - Preview changes without executing
   - Recommended for first-time users
   
2. **Live Mode**
   - Check the "Execute Changes" checkbox to enable
   - Carefully review resources before proceeding
   - Execute optimization on selected resources

### Step 5: Export Reports
- Download findings as **JSON** for programmatic use
- Export as **CSV** for spreadsheet analysis

## 📸 Screenshots & Demo

See the application in action:

### 1. Login Screen
![Login Page](test/Screenshot%20from%202026-01-14%2012-46-25.png)
*User enters AWS credentials and selects region*

### 2. Mode Selection
![Mode Selection Modal](test/Screenshot%20from%202026-01-14%2012-49-02.png)
*Choose between Safe Dry-Run mode or Live mode for analysis*

### 3. Optimization Techniques
![Techniques Grid](test/Screenshot%20from%202026-01-14%2012-52-25.png)
*Beautiful grid showing all 15 optimization techniques ready to analyze*

### 4. Analysis Results - Resource List
![Analysis Results Part 1](test/Screenshot%20from%202026-01-14%2014-34-01.png)
*Detailed findings showing identified resources and potential savings*

### 5. Confirmation Dialog
![Confirmation Dialog](test/Screenshot%20from%202026-01-14%2014-36-45.png)
*Safe confirmation before optimization with service name verification*

### 6. Optimization in Progress
![Optimization Progress](test/Screenshot%20from%202026-01-14%2014-37-03.png)
*Real-time progress showing optimization execution*

### 7. Final Results
![Optimization Results](test/Screenshot%20from%202026-01-14%2014-37-21.png)
*Summary showing successful optimizations and cost savings*

## API Endpoints

### Authentication
- `POST /api/credentials/validate` - Validate AWS credentials
- `GET /api/credentials/check` - Check saved credentials
- `POST /api/credentials/clear` - Clear saved credentials

### Analysis & Optimization
- `GET /api/techniques` - List all optimization techniques
- `POST /api/analyze/<technique>` - Analyze specific technique
- `POST /api/optimize/<technique>` - Execute optimization
- `GET /api/health` - Health check

## Security Considerations

### Best Practices
1. ✅ Use IAM users, not root credentials
2. ✅ Apply principle of least privilege
3. ✅ Rotate credentials regularly
4. ✅ Use dry-run mode before executing changes
5. ✅ Review all resources before deletion
6. ✅ Keep credentials file secure
7. ✅ Never share access keys

### Encryption
- Credentials are encrypted using Fernet (symmetric encryption)
- Encryption key is stored separately in `~/.aws_optimizer/.key`
- Encrypted credentials stored in `~/.aws_optimizer/credentials.enc`

## Cost Savings Example

With all 15 techniques optimized:
- **EBS Volumes**: 10 unused volumes × $1/month = $10
- **EC2 Snapshots**: 20 old snapshots × $0.50/month = $10
- **Elastic IPs**: 5 unused × $3.65 = $18.25
- **Load Balancers**: 2 unused × $22.86 = $45.72
- **NAT Gateways**: 1 unused × $42.80 = $42.80
- **RDS Snapshots**: 15 old × $0.50/month = $7.50
- **CloudWatch Logs**: 5 GB × $0.50 = $2.50
- **Elastic Beanstalk**: 2 environments × $20 = $40
- **VPC Endpoints**: 2 unused × $14.40 = $28.80
- **Total**: ~$205/month or $2,460/year! 🎉

## Troubleshooting

### "Invalid access key ID"
- Verify your AWS Access Key ID is correct
- Ensure the key hasn't been rotated
- Check that the user has necessary permissions

### "AccessDenied" errors
- Ensure IAM user has required permissions
- Review attached policies
- Consider creating a new policy with needed actions

### No resources found
- Region might not have resources
- Try different regions
- Verify credentials have correct permissions

### CORS errors
- Ensure backend is running on port 5000
- Check that frontend has correct API URL
- Clear browser cache and reload

## Performance Tips

1. **Region Selection**: Analyze one region at a time for faster results
2. **Batch Operations**: Use dry-run mode first, then batch optimize
3. **Caching**: Clear old analysis results before new analysis
4. **Background Jobs**: For large AWS accounts, consider running analysis during off-hours

## Development

### Backend Stack
- **Framework**: Flask
- **AWS SDK**: boto3
- **Encryption**: cryptography
- **CORS**: flask-cors

### Frontend Stack
- **Framework**: React 18
- **Build Tool**: Vite
- **HTTP Client**: Axios
- **Styling**: CSS3

### Adding New Optimizers

1. Create a new file in `backend/optimizers/`
2. Inherit from `BaseOptimizer`
3. Implement `analyze()` and `optimize()` methods
4. Register in `app/routes.py` OPTIMIZERS dictionary
5. Add to techniques list in `/api/techniques` endpoint

## Contributing

Contributions are welcome! Areas for improvement:
- More optimization techniques
- Enhanced analytics and visualizations
- Cost calculation improvements
- Multi-account support
- Scheduled analysis

## License

MIT License - Free for personal and commercial use

## Support

For issues, questions, or feature requests:
1. Check the troubleshooting section
2. Review AWS IAM permissions
3. Check application logs in backend console

---

**Made with ❤️ to help you save on AWS costs!**

*Remember: Always use dry-run mode first and carefully review resources before deletion!*
