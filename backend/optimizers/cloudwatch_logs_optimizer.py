from .base_optimizer import BaseOptimizer
from datetime import datetime, timedelta

class CloudWatchLogsOptimizer(BaseOptimizer):
    """Remove CloudWatch log groups with no recent activity"""
    
    def analyze(self):
        """Find inactive CloudWatch log groups"""
        try:
            logs = self._get_client('logs')
            
            response = logs.describe_log_groups()
            
            for log_group in response.get('logGroups', []):
                lg_name = log_group['logGroupName']
                creation_time = log_group.get('creationTime', 0)
                creation_dt = datetime.fromtimestamp(creation_time / 1000)
                last_event_time = log_group.get('lastEventTimestamp', 0)
                
                days_since_activity = (datetime.now() - datetime.fromtimestamp(last_event_time / 1000)).days if last_event_time else 999
                
                # Only flag log groups with no activity for > 30 days
                if days_since_activity > 30:
                    size = log_group.get('storedBytes', 0)
                    # Estimate $0.50 per GB-month for CloudWatch Logs
                    monthly_cost = (size / (1024**3)) * 0.50
                    
                    self.add_finding(
                        resource_id=lg_name,
                        resource_type='CloudWatch Log Group',
                        details={
                            'log_group_name': lg_name,
                            'created': creation_dt.isoformat(),
                            'days_since_activity': days_since_activity,
                            'stored_bytes': size,
                            'stored_gb': round(size / (1024**3), 2),
                            'retention_days': log_group.get('retentionInDays', 'Never Expire')
                        },
                        estimated_savings=monthly_cost
                    )
            
            return self.findings
        except Exception as e:
            return {'error': str(e)}
    
    def optimize(self, resource_ids):
        """Delete CloudWatch log groups"""
        try:
            logs = self._get_client('logs')
            results = []
            
            for log_group_name in resource_ids:
                try:
                    logs.delete_log_group(logGroupName=log_group_name)
                    results.append({
                        'resource_id': log_group_name,
                        'status': 'success',
                        'message': f'Deleted log group {log_group_name}'
                    })
                except Exception as e:
                    results.append({
                        'resource_id': log_group_name,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return results
        except Exception as e:
            return {'error': str(e)}
