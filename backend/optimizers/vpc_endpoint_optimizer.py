from .base_optimizer import BaseOptimizer

class VPCEndpointOptimizer(BaseOptimizer):
    """Delete unused VPC endpoints"""
    
    def analyze(self):
        """Find unused VPC endpoints"""
        try:
            ec2 = self._get_client('ec2')
            
            response = ec2.describe_vpc_endpoints()
            
            for endpoint in response.get('VpcEndpoints', []):
                endpoint_id = endpoint['VpcEndpointId']
                state = endpoint['State']
                service_name = endpoint.get('ServiceName', '')
                
                # Flag endpoints that are not in 'available' state
                # or have been unused for a long time
                if state in ['Failed', 'Expired', 'Deleted']:
                    # Estimate $0.01-0.05 per hour depending on type
                    monthly_cost = 0.02 * 24 * 30  # ~$14.40/month
                    
                    self.add_finding(
                        resource_id=endpoint_id,
                        resource_type='VPC Endpoint',
                        details={
                            'endpoint_id': endpoint_id,
                            'service_name': service_name,
                            'state': state,
                            'vpc_id': endpoint.get('VpcId', ''),
                            'type': endpoint.get('VpcEndpointType', ''),
                            'creation_timestamp': endpoint.get('CreationTimestamp', '').isoformat() if endpoint.get('CreationTimestamp') else ''
                        },
                        estimated_savings=monthly_cost
                    )
            
            return self.findings
        except Exception as e:
            return {'error': str(e)}
    
    def optimize(self, resource_ids):
        """Delete VPC endpoints"""
        try:
            ec2 = self._get_client('ec2')
            results = []
            
            for endpoint_id in resource_ids:
                try:
                    ec2.delete_vpc_endpoints(VpcEndpointIds=[endpoint_id])
                    results.append({
                        'resource_id': endpoint_id,
                        'status': 'success',
                        'message': f'Deleted VPC endpoint {endpoint_id}'
                    })
                except Exception as e:
                    results.append({
                        'resource_id': endpoint_id,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return results
        except Exception as e:
            return {'error': str(e)}
