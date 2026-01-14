from .base_optimizer import BaseOptimizer
from datetime import datetime, timedelta

class EC2SnapshotOptimizer(BaseOptimizer):
    """Remove unused EC2 snapshots"""
    
    def analyze(self):
        """Find snapshots not associated with AMIs"""
        try:
            ec2 = self._get_client('ec2')
            
            # Get all snapshots owned by account
            response = ec2.describe_snapshots(OwnerIds=['self'])
            
            # Get all AMIs to check which snapshots are in use
            amis_response = ec2.describe_images(Owners=['self'])
            used_snapshot_ids = set()
            for ami in amis_response.get('Images', []):
                for mapping in ami.get('BlockDeviceMappings', []):
                    if 'Ebs' in mapping:
                        used_snapshot_ids.add(mapping['Ebs'].get('SnapshotId'))
            
            for snapshot in response.get('Snapshots', []):
                snapshot_id = snapshot['SnapshotId']
                
                # Only flag snapshots not used by AMIs
                if snapshot_id not in used_snapshot_ids:
                    start_time = snapshot['StartTime']
                    days_old = (datetime.now(start_time.tzinfo) - start_time).days
                    
                    # Estimate $0.05 per GB-month
                    size = snapshot['VolumeSize']
                    monthly_cost = size * 0.05
                    
                    # Prioritize old snapshots over 30 days
                    if days_old > 30:
                        self.add_finding(
                            resource_id=snapshot_id,
                            resource_type='EC2 Snapshot',
                            details={
                                'size_gb': size,
                                'created': start_time.isoformat(),
                                'days_old': days_old,
                                'description': snapshot.get('Description', ''),
                                'state': snapshot['State']
                            },
                            estimated_savings=monthly_cost
                        )
            
            return self.findings
        except Exception as e:
            return {'error': str(e)}
    
    def optimize(self, resource_ids):
        """Delete EC2 snapshots"""
        try:
            ec2 = self._get_client('ec2')
            results = []
            
            for snapshot_id in resource_ids:
                try:
                    ec2.delete_snapshot(
                        SnapshotId=snapshot_id,
                        DryRun=self.dry_run
                    )
                    results.append({
                        'resource_id': snapshot_id,
                        'status': 'success',
                        'message': f'Deleted snapshot {snapshot_id}'
                    })
                except Exception as e:
                    results.append({
                        'resource_id': snapshot_id,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return results
        except Exception as e:
            return {'error': str(e)}
