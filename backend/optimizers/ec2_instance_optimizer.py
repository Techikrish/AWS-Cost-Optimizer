from .base_optimizer import BaseOptimizer
from datetime import datetime, timedelta

class EC2InstanceOptimizer(BaseOptimizer):
    """Terminate stopped EC2 instances"""
    
    def analyze(self):
        """Find stopped instances"""
        try:
            ec2 = self._get_client('ec2')
            response = ec2.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}]
            )
            
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    state_transition_reason = instance.get('StateTransitionReason', '')
                    state_change_time = instance.get('StateTransitionTime', datetime.now())
                    
                    days_stopped = (datetime.now(state_change_time.tzinfo) - state_change_time).days
                    
                    # Estimate based on instance type (average $0.05/hour for t2.micro)
                    monthly_cost = 0.05 * 24 * 30
                    
                    if days_stopped > 7:  # Only flag if stopped for > 7 days
                        self.add_finding(
                            resource_id=instance['InstanceId'],
                            resource_type='EC2 Instance',
                            details={
                                'instance_type': instance.get('InstanceType', 'Unknown'),
                                'state': instance['State']['Name'],
                                'stopped_time': state_change_time.isoformat(),
                                'days_stopped': days_stopped,
                                'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])},
                                'launch_time': instance.get('LaunchTime', '').isoformat() if instance.get('LaunchTime') else ''
                            },
                            estimated_savings=monthly_cost
                        )
            
            return self.findings
        except Exception as e:
            return {'error': str(e)}
    
    def optimize(self, resource_ids):
        """Terminate EC2 instances"""
        try:
            ec2 = self._get_client('ec2')
            results = []
            
            for instance_id in resource_ids:
                try:
                    ec2.terminate_instances(
                        InstanceIds=[instance_id],
                        DryRun=self.dry_run
                    )
                    results.append({
                        'resource_id': instance_id,
                        'status': 'success',
                        'message': f'Terminated instance {instance_id}'
                    })
                except Exception as e:
                    results.append({
                        'resource_id': instance_id,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return results
        except Exception as e:
            return {'error': str(e)}
