from .base_optimizer import BaseOptimizer
from datetime import datetime, timedelta

class RDSSnapshotOptimizer(BaseOptimizer):
    """Remove unused RDS snapshots"""
    
    def analyze(self):
        """Find old RDS snapshots"""
        try:
            rds = self._get_client('rds')
            
            response = rds.describe_db_snapshots()
            
            for snapshot in response.get('DBSnapshots', []):
                snapshot_id = snapshot['DBSnapshotIdentifier']
                create_time = snapshot['SnapshotCreateTime']
                days_old = (datetime.now(create_time.tzinfo) - create_time).days
                
                # Only flag old snapshots (> 30 days)
                if days_old > 30:
                    size = snapshot.get('AllocatedStorage', 0)
                    # Estimate $0.095 per GB-month for RDS snapshots
                    monthly_cost = size * 0.095
                    
                    self.add_finding(
                        resource_id=snapshot_id,
                        resource_type='RDS Snapshot',
                        details={
                            'snapshot_id': snapshot_id,
                            'db_instance': snapshot.get('DBInstanceIdentifier', ''),
                            'created': create_time.isoformat(),
                            'days_old': days_old,
                            'size_gb': size,
                            'status': snapshot.get('Status', ''),
                            'engine': snapshot.get('Engine', '')
                        },
                        estimated_savings=monthly_cost
                    )
            
            return self.findings
        except Exception as e:
            return {'error': str(e)}
    
    def optimize(self, resource_ids):
        """Delete RDS snapshots"""
        try:
            rds = self._get_client('rds')
            results = []
            
            for snapshot_id in resource_ids:
                try:
                    rds.delete_db_snapshot(DBSnapshotIdentifier=snapshot_id)
                    results.append({
                        'resource_id': snapshot_id,
                        'status': 'success',
                        'message': f'Deleted RDS snapshot {snapshot_id}'
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
