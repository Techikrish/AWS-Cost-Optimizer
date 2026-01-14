from .base_optimizer import BaseOptimizer

class LoadBalancerOptimizer(BaseOptimizer):
    """Remove unused load balancers"""
    
    def analyze(self):
        """Find load balancers with no active targets"""
        try:
            elb = self._get_client('elbv2')
            
            # Get all load balancers
            response = elb.describe_load_balancers()
            
            for lb in response.get('LoadBalancers', []):
                lb_arn = lb['LoadBalancerArn']
                lb_name = lb['LoadBalancerName']
                lb_type = lb['Type']
                
                # Get target groups
                tg_response = elb.describe_target_groups(LoadBalancerArn=lb_arn)
                
                has_active_targets = False
                for tg in tg_response.get('TargetGroups', []):
                    health_response = elb.describe_target_health(TargetGroupArn=tg['TargetGroupArn'])
                    if health_response.get('TargetHealthDescriptions'):
                        has_active_targets = True
                        break
                
                # Estimate cost: ALB ~$22.86/month, NLB ~$32.40/month
                monthly_cost = 32.40 if lb_type == 'network' else 22.86
                
                if not has_active_targets:
                    self.add_finding(
                        resource_id=lb_name,
                        resource_type='Load Balancer',
                        details={
                            'name': lb_name,
                            'type': lb_type,
                            'arn': lb_arn,
                            'scheme': lb.get('Scheme', ''),
                            'vpc_id': lb.get('VpcId', ''),
                            'created_time': lb.get('CreatedTime', '').isoformat() if lb.get('CreatedTime') else '',
                            'target_groups': len(tg_response.get('TargetGroups', []))
                        },
                        estimated_savings=monthly_cost
                    )
            
            return self.findings
        except Exception as e:
            return {'error': str(e)}
    
    def optimize(self, resource_ids):
        """Delete load balancers"""
        try:
            elb = self._get_client('elbv2')
            results = []
            
            # Get all load balancers to find ARNs
            response = elb.describe_load_balancers()
            lb_map = {lb['LoadBalancerName']: lb['LoadBalancerArn'] for lb in response.get('LoadBalancers', [])}
            
            for lb_name in resource_ids:
                try:
                    if lb_name in lb_map:
                        elb.delete_load_balancer(LoadBalancerArn=lb_map[lb_name])
                        results.append({
                            'resource_id': lb_name,
                            'status': 'success',
                            'message': f'Deleted load balancer {lb_name}'
                        })
                except Exception as e:
                    results.append({
                        'resource_id': lb_name,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return results
        except Exception as e:
            return {'error': str(e)}
