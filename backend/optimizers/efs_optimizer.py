from .base_optimizer import BaseOptimizer

class EFSOptimizer(BaseOptimizer):
    """Delete unused Elastic File Systems"""
    
    def analyze(self):
        """Find EFS with no mount targets"""
        try:
            efs = self._get_client('efs')
            
            response = efs.describe_file_systems()
            
            for fs in response.get('FileSystems', []):
                fs_id = fs['FileSystemId']
                
                # Get mount targets
                mounts_response = efs.describe_mount_targets(FileSystemId=fs_id)
                mount_targets = mounts_response.get('MountTargets', [])
                
                if not mount_targets:
                    size = fs.get('SizeInBytes', {}).get('Value', 0)
                    # Estimate $0.30 per GB-month for Standard
                    monthly_cost = (size / (1024**3)) * 0.30
                    
                    self.add_finding(
                        resource_id=fs_id,
                        resource_type='EFS',
                        details={
                            'filesystem_id': fs_id,
                            'name': fs.get('Name', ''),
                            'size_bytes': size,
                            'performance_mode': fs.get('PerformanceMode', ''),
                            'throughput_mode': fs.get('ThroughputMode', ''),
                            'mount_targets': len(mount_targets)
                        },
                        estimated_savings=monthly_cost
                    )
            
            return self.findings
        except Exception as e:
            return {'error': str(e)}
    
    def optimize(self, resource_ids):
        """Delete EFS"""
        try:
            efs = self._get_client('efs')
            results = []
            
            for fs_id in resource_ids:
                try:
                    efs.delete_file_system(FileSystemId=fs_id)
                    results.append({
                        'resource_id': fs_id,
                        'status': 'success',
                        'message': f'Deleted EFS {fs_id}'
                    })
                except Exception as e:
                    results.append({
                        'resource_id': fs_id,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return results
        except Exception as e:
            return {'error': str(e)}
