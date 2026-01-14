from .base_optimizer import BaseOptimizer
from datetime import datetime, timedelta

class EBSOptimizer(BaseOptimizer):
    """Remove unused EBS volumes"""
    
    def analyze(self):
        """Find unattached EBS volumes"""
        try:
            ec2 = self._get_client('ec2')
            response = ec2.describe_volumes(
                Filters=[{'Name': 'status', 'Values': ['available']}]
            )
            
            for volume in response.get('Volumes', []):
                size = volume['Size']
                create_time = volume['CreateTime']
                days_old = (datetime.now(create_time.tzinfo) - create_time).days
                
                # Estimate $0.10 per GB-month
                monthly_cost = size * 0.10
                
                self.add_finding(
                    resource_id=volume['VolumeId'],
                    resource_type='EBS Volume',
                    details={
                        'size_gb': size,
                        'created': create_time.isoformat(),
                        'days_old': days_old,
                        'availability_zone': volume['AvailabilityZone'],
                        'state': volume['State']
                    },
                    estimated_savings=monthly_cost
                )
            
            return self.findings
        except Exception as e:
            return {'error': str(e)}
    
    def optimize(self, resource_ids):
        """Delete EBS volumes"""
        try:
            ec2 = self._get_client('ec2')
            results = []
            
            for volume_id in resource_ids:
                try:
                    ec2.delete_volume(
                        VolumeId=volume_id,
                        DryRun=self.dry_run
                    )
                    results.append({
                        'resource_id': volume_id,
                        'status': 'success',
                        'message': f'Deleted EBS volume {volume_id}'
                    })
                except Exception as e:
                    results.append({
                        'resource_id': volume_id,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return results
        except Exception as e:
            return {'error': str(e)}
