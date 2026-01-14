from flask import Blueprint, request, jsonify
from app.credential_manager import CredentialManager
from optimizers.ebs_optimizer import EBSOptimizer
from optimizers.ec2_snapshot_optimizer import EC2SnapshotOptimizer
from optimizers.ec2_instance_optimizer import EC2InstanceOptimizer
from optimizers.elastic_ip_optimizer import ElasticIPOptimizer
from optimizers.load_balancer_optimizer import LoadBalancerOptimizer
from optimizers.ami_optimizer import AMIOptimizer
from optimizers.security_group_optimizer import SecurityGroupOptimizer
from optimizers.nat_gateway_optimizer import NATGatewayOptimizer
from optimizers.rds_snapshot_optimizer import RDSSnapshotOptimizer
from optimizers.efs_optimizer import EFSOptimizer
from optimizers.cloudwatch_logs_optimizer import CloudWatchLogsOptimizer
from optimizers.s3_bucket_optimizer import S3BucketOptimizer
from optimizers.elastic_beanstalk_optimizer import ElasticBeanstalkOptimizer
from optimizers.vpc_endpoint_optimizer import VPCEndpointOptimizer
from optimizers.ecs_task_definition_optimizer import ECSTaskDefinitionOptimizer

api_bp = Blueprint('api', __name__, url_prefix='/api')
cred_manager = CredentialManager()

# Map of optimizer names to classes
OPTIMIZERS = {
    'ebs': EBSOptimizer,
    'ec2-snapshots': EC2SnapshotOptimizer,
    'ec2-instances': EC2InstanceOptimizer,
    'elastic-ip': ElasticIPOptimizer,
    'load-balancers': LoadBalancerOptimizer,
    'amis': AMIOptimizer,
    'security-groups': SecurityGroupOptimizer,
    'nat-gateways': NATGatewayOptimizer,
    'rds-snapshots': RDSSnapshotOptimizer,
    'efs': EFSOptimizer,
    'cloudwatch-logs': CloudWatchLogsOptimizer,
    's3-buckets': S3BucketOptimizer,
    'elastic-beanstalk': ElasticBeanstalkOptimizer,
    'vpc-endpoints': VPCEndpointOptimizer,
    'ecs-task-definitions': ECSTaskDefinitionOptimizer,
}

@api_bp.route('/credentials/validate', methods=['POST'])
def validate_credentials():
    """Validate AWS credentials"""
    data = request.get_json()
    access_key = data.get('access_key')
    secret_key = data.get('secret_key')
    region = data.get('region', 'us-east-1')
    
    if not access_key or not secret_key:
        return jsonify({'error': 'Missing credentials'}), 400
    
    # Validate
    result = cred_manager.validate_credentials(access_key, secret_key)
    
    if result.get('valid'):
        # Save credentials
        cred_manager.save_credentials(access_key, secret_key, region)
        return jsonify(result), 200
    else:
        return jsonify(result), 401

@api_bp.route('/credentials/check', methods=['GET'])
def check_credentials():
    """Check if credentials are saved and valid"""
    creds = cred_manager.load_credentials()
    if creds:
        result = cred_manager.validate_credentials(creds['access_key'], creds['secret_key'])
        return jsonify(result), 200
    else:
        return jsonify({'valid': False, 'error': 'No credentials saved'}), 404

@api_bp.route('/credentials/clear', methods=['POST'])
def clear_credentials():
    """Clear saved credentials"""
    cred_manager.clear_credentials()
    return jsonify({'status': 'success', 'message': 'Credentials cleared'}), 200

@api_bp.route('/analyze/<technique>', methods=['POST'])
def analyze(technique):
    """Analyze resources using specific technique"""
    if technique not in OPTIMIZERS:
        return jsonify({'error': f'Unknown technique: {technique}'}), 400
    
    try:
        creds = cred_manager.load_credentials()
        if not creds:
            return jsonify({'error': 'No credentials saved'}), 401
        
        region = request.get_json().get('region', 'us-east-1') if request.get_json() else 'us-east-1'
        
        optimizer = OPTIMIZERS[technique](
            creds['access_key'],
            creds['secret_key'],
            region
        )
        
        findings = optimizer.analyze()
        
        total_savings = sum(f.get('estimated_savings', 0) for f in findings if isinstance(findings, list))
        
        return jsonify({
            'technique': technique,
            'findings': findings,
            'count': len(findings) if isinstance(findings, list) else 0,
            'total_monthly_savings': round(total_savings, 2)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/optimize/<technique>', methods=['POST'])
def optimize(technique):
    """Execute optimization"""
    if technique not in OPTIMIZERS:
        return jsonify({'error': f'Unknown technique: {technique}'}), 400
    
    try:
        data = request.get_json()
        resource_ids = data.get('resource_ids', [])
        dry_run = data.get('dry_run', True)
        
        creds = cred_manager.load_credentials()
        if not creds:
            return jsonify({'error': 'No credentials saved'}), 401
        
        region = data.get('region', 'us-east-1')
        
        optimizer = OPTIMIZERS[technique](
            creds['access_key'],
            creds['secret_key'],
            region
        )
        optimizer.dry_run = dry_run
        
        results = optimizer.optimize(resource_ids)
        
        success_count = sum(1 for r in results if r.get('status') == 'success')
        failed_count = sum(1 for r in results if r.get('status') == 'failed')
        
        return jsonify({
            'technique': technique,
            'dry_run': dry_run,
            'results': results,
            'summary': {
                'total': len(results),
                'success': success_count,
                'failed': failed_count
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/techniques', methods=['GET'])
def get_techniques():
    """Get list of available optimization techniques"""
    techniques = [
        {
            'id': 'ebs',
            'name': 'Remove Unused EBS Volumes',
            'description': 'Deletes unattached EBS volumes',
            'icon': '💾'
        },
        {
            'id': 'ec2-snapshots',
            'name': 'Remove Unused EC2 Snapshots',
            'description': 'Cleans up old snapshots not associated with AMIs',
            'icon': '📸'
        },
        {
            'id': 'ec2-instances',
            'name': 'Terminate Stopped EC2 Instances',
            'description': 'Removes instances that have been stopped for extended periods',
            'icon': '🖥️'
        },
        {
            'id': 'elastic-ip',
            'name': 'Delete Unattached Elastic IPs',
            'description': 'Releases Elastic IPs not associated with resources',
            'icon': '🌐'
        },
        {
            'id': 'load-balancers',
            'name': 'Remove Unused Load Balancers',
            'description': 'Deletes load balancers with no active targets',
            'icon': '⚖️'
        },
        {
            'id': 'amis',
            'name': 'Delete Old/Unused AMIs',
            'description': 'Removes AMI images that are no longer in use',
            'icon': '🖼️'
        },
        {
            'id': 'security-groups',
            'name': 'Remove Unused Security Groups',
            'description': 'Cleans up security groups not attached to any resources',
            'icon': '🔐'
        },
        {
            'id': 'nat-gateways',
            'name': 'Delete Unused NAT Gateways',
            'description': 'Removes NAT Gateways not being used',
            'icon': '🚪'
        },
        {
            'id': 'rds-snapshots',
            'name': 'Remove Unused RDS Snapshots',
            'description': 'Deletes old RDS database snapshots',
            'icon': '🗄️'
        },
        {
            'id': 'efs',
            'name': 'Delete Unused Elastic File Systems (EFS)',
            'description': 'Removes EFS with no mount targets',
            'icon': '📁'
        },
        {
            'id': 'cloudwatch-logs',
            'name': 'Remove Unused CloudWatch Log Groups',
            'description': 'Cleans up log groups with no recent activity',
            'icon': '📋'
        },
        {
            'id': 's3-buckets',
            'name': 'Delete Empty/Unused S3 Buckets',
            'description': 'Removes empty S3 buckets',
            'icon': '🪣'
        },
        {
            'id': 'elastic-beanstalk',
            'name': 'Terminate Unused Elastic Beanstalk Environments',
            'description': 'Cleans up terminated environments',
            'icon': '🌱'
        },
        {
            'id': 'vpc-endpoints',
            'name': 'Remove Unused VPC Endpoints',
            'description': 'Deletes unused VPC endpoints',
            'icon': '🔗'
        },
        {
            'id': 'ecs-task-definitions',
            'name': 'Delete Unused ECS Task Definitions',
            'description': 'Removes task definitions not in use',
            'icon': '📦'
        }
    ]
    return jsonify(techniques), 200

@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200
