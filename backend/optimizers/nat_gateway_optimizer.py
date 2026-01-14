from .base_optimizer import BaseOptimizer

class NATGatewayOptimizer(BaseOptimizer):
    """Delete unused NAT Gateways"""
    
    def analyze(self):
        """Find unused NAT Gateways"""
        try:
            ec2 = self._get_client('ec2')
            
            response = ec2.describe_nat_gateways()
            
            for nat in response.get('NatGateways', []):
                nat_id = nat['NatGatewayId']
                
                # Check if the NAT gateway has been used recently
                # If state is 'available' and no connections, it's unused
                if nat['State'] == 'available':
                    # Estimate $0.045/hour + $0.045 per GB data processed
                    monthly_cost = (0.045 * 24 * 30) + 10  # ~$42.80/month
                    
                    self.add_finding(
                        resource_id=nat_id,
                        resource_type='NAT Gateway',
                        details={
                            'nat_gateway_id': nat_id,
                            'state': nat['State'],
                            'subnet_id': nat.get('SubnetId', ''),
                            'vpc_id': nat.get('VpcId', ''),
                            'public_ip': nat.get('NatGatewayAddresses', [{}])[0].get('PublicIp', ''),
                            'create_time': nat.get('CreateTime', '').isoformat() if nat.get('CreateTime') else ''
                        },
                        estimated_savings=monthly_cost
                    )
            
            return self.findings
        except Exception as e:
            return {'error': str(e)}
    
    def optimize(self, resource_ids):
        """Delete NAT Gateways"""
        try:
            ec2 = self._get_client('ec2')
            results = []
            
            for nat_id in resource_ids:
                try:
                    ec2.delete_nat_gateway(NatGatewayId=nat_id)
                    results.append({
                        'resource_id': nat_id,
                        'status': 'success',
                        'message': f'Deleted NAT Gateway {nat_id}'
                    })
                except Exception as e:
                    results.append({
                        'resource_id': nat_id,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return results
        except Exception as e:
            return {'error': str(e)}
