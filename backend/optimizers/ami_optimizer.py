from .base_optimizer import BaseOptimizer
from datetime import datetime, timedelta

class AMIOptimizer(BaseOptimizer):
    """Delete old/unused AMIs"""
    
    def analyze(self):
        """Find old AMIs not being used"""
        try:
            ec2 = self._get_client('ec2')
            
            # Get all AMIs owned by account
            response = ec2.describe_images(Owners=['self'])
            
            # Get all instances to see which AMIs are in use
            instances_response = ec2.describe_instances()
            used_ami_ids = set()
            for reservation in instances_response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    if instance['State']['Name'] != 'terminated':
                        used_ami_ids.add(instance.get('ImageId'))
            
            for ami in response.get('Images', []):
                ami_id = ami['ImageId']
                
                # Only flag old AMIs not used by instances
                if ami_id not in used_ami_ids:
                    creation_time = datetime.fromisoformat(ami['CreationDate'].replace('Z', '+00:00'))
                    days_old = (datetime.now(creation_time.tzinfo) - creation_time).days
                    
                    # Only flag if older than 30 days
                    if days_old > 30:
                        # Estimate $1 per snapshot + storage
                        monthly_cost = 1.0
                        
                        self.add_finding(
                            resource_id=ami_id,
                            resource_type='AMI',
                            details={
                                'name': ami.get('Name', ''),
                                'ami_id': ami_id,
                                'created': creation_time.isoformat(),
                                'days_old': days_old,
                                'architecture': ami.get('Architecture', ''),
                                'root_device_type': ami.get('RootDeviceType', ''),
                                'state': ami.get('State', '')
                            },
                            estimated_savings=monthly_cost
                        )
            
            return self.findings
        except Exception as e:
            return {'error': str(e)}
    
    def optimize(self, resource_ids):
        """Delete AMIs"""
        try:
            ec2 = self._get_client('ec2')
            results = []
            
            for ami_id in resource_ids:
                try:
                    # Deregister AMI
                    ec2.deregister_image(ImageId=ami_id, DryRun=self.dry_run)
                    
                    results.append({
                        'resource_id': ami_id,
                        'status': 'success',
                        'message': f'Deleted AMI {ami_id}'
                    })
                except Exception as e:
                    results.append({
                        'resource_id': ami_id,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return results
        except Exception as e:
            return {'error': str(e)}
