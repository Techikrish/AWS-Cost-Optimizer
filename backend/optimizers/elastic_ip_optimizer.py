from .base_optimizer import BaseOptimizer

class ElasticIPOptimizer(BaseOptimizer):
    """Delete unattached Elastic IPs"""
    
    def analyze(self):
        """Find unattached Elastic IPs"""
        try:
            ec2 = self._get_client('ec2')
            response = ec2.describe_addresses()
            
            for address in response.get('Addresses', []):
                # Only flag Elastic IPs that are not associated
                if 'InstanceId' not in address or not address['InstanceId']:
                    # Estimate $0.005 per hour = ~$3.65/month for unused EIP
                    monthly_cost = 0.005 * 24 * 30
                    
                    self.add_finding(
                        resource_id=address['PublicIp'],
                        resource_type='Elastic IP',
                        details={
                            'public_ip': address['PublicIp'],
                            'allocation_id': address.get('AllocationId', ''),
                            'domain': address.get('Domain', ''),
                            'associated': 'InstanceId' in address and bool(address.get('InstanceId')),
                            'allocation_time': address.get('AllocatedTime', '').isoformat() if address.get('AllocatedTime') else ''
                        },
                        estimated_savings=monthly_cost
                    )
            
            return self.findings
        except Exception as e:
            return {'error': str(e)}
    
    def optimize(self, resource_ids):
        """Release Elastic IPs"""
        try:
            ec2 = self._get_client('ec2')
            results = []
            
            for public_ip in resource_ids:
                try:
                    # Get allocation ID
                    response = ec2.describe_addresses(PublicIps=[public_ip])
                    if response['Addresses']:
                        allocation_id = response['Addresses'][0].get('AllocationId')
                        
                        ec2.release_address(
                            AllocationId=allocation_id,
                            DryRun=self.dry_run
                        )
                        results.append({
                            'resource_id': public_ip,
                            'status': 'success',
                            'message': f'Released Elastic IP {public_ip}'
                        })
                except Exception as e:
                    results.append({
                        'resource_id': public_ip,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return results
        except Exception as e:
            return {'error': str(e)}
