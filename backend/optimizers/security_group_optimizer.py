from .base_optimizer import BaseOptimizer

class SecurityGroupOptimizer(BaseOptimizer):
    """Remove unused security groups"""
    
    def analyze(self):
        """Find security groups not attached to any resources"""
        try:
            ec2 = self._get_client('ec2')
            
            # Get all security groups
            response = ec2.describe_security_groups()
            
            # Get all instances to see which security groups are in use
            instances_response = ec2.describe_instances()
            used_sg_ids = set()
            for reservation in instances_response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    if instance['State']['Name'] != 'terminated':
                        for sg in instance.get('SecurityGroups', []):
                            used_sg_ids.add(sg['GroupId'])
            
            for sg in response.get('SecurityGroups', []):
                sg_id = sg['GroupId']
                sg_name = sg['GroupName']
                
                # Skip default security group
                if sg_name == 'default':
                    continue
                
                # Only flag unused security groups
                if sg_id not in used_sg_ids:
                    self.add_finding(
                        resource_id=sg_id,
                        resource_type='Security Group',
                        details={
                            'name': sg_name,
                            'group_id': sg_id,
                            'description': sg.get('Description', ''),
                            'vpc_id': sg.get('VpcId', ''),
                            'inbound_rules': len(sg.get('IpPermissions', [])),
                            'outbound_rules': len(sg.get('IpPermissionsEgress', []))
                        },
                        estimated_savings=0  # No direct cost, but cleanup
                    )
            
            return self.findings
        except Exception as e:
            return {'error': str(e)}
    
    def optimize(self, resource_ids):
        """Delete security groups"""
        try:
            ec2 = self._get_client('ec2')
            results = []
            
            for sg_id in resource_ids:
                try:
                    ec2.delete_security_group(GroupId=sg_id, DryRun=self.dry_run)
                    results.append({
                        'resource_id': sg_id,
                        'status': 'success',
                        'message': f'Deleted security group {sg_id}'
                    })
                except Exception as e:
                    results.append({
                        'resource_id': sg_id,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return results
        except Exception as e:
            return {'error': str(e)}
