from .base_optimizer import BaseOptimizer

class S3BucketOptimizer(BaseOptimizer):
    """Delete empty/unused S3 buckets"""
    
    def analyze(self):
        """Find empty S3 buckets"""
        try:
            s3 = self._get_client('s3')
            
            response = s3.list_buckets()
            
            for bucket in response.get('Buckets', []):
                bucket_name = bucket['Name']
                
                # Check if bucket is empty
                try:
                    objects_response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
                    has_objects = 'Contents' in objects_response
                    
                    if not has_objects:
                        self.add_finding(
                            resource_id=bucket_name,
                            resource_type='S3 Bucket',
                            details={
                                'bucket_name': bucket_name,
                                'created': bucket.get('CreationDate', '').isoformat() if bucket.get('CreationDate') else '',
                                'object_count': 0,
                                'is_empty': True
                            },
                            estimated_savings=0  # Minimal cost for empty bucket
                        )
                except Exception:
                    pass
            
            return self.findings
        except Exception as e:
            return {'error': str(e)}
    
    def optimize(self, resource_ids):
        """Delete S3 buckets"""
        try:
            s3 = self._get_client('s3')
            results = []
            
            for bucket_name in resource_ids:
                try:
                    s3.delete_bucket(Bucket=bucket_name)
                    results.append({
                        'resource_id': bucket_name,
                        'status': 'success',
                        'message': f'Deleted bucket {bucket_name}'
                    })
                except Exception as e:
                    results.append({
                        'resource_id': bucket_name,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return results
        except Exception as e:
            return {'error': str(e)}
