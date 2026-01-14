from .base_optimizer import BaseOptimizer

class ECSTaskDefinitionOptimizer(BaseOptimizer):
    """Delete unused ECS task definitions"""
    
    def analyze(self):
        """Find inactive ECS task definitions"""
        try:
            ecs = self._get_client('ecs')
            
            # List all task definitions
            task_defs_response = ecs.list_task_definitions(status='INACTIVE')
            
            for task_def_arn in task_defs_response.get('taskDefinitionArns', []):
                # Get task definition details
                try:
                    task_def = ecs.describe_task_definition(taskDefinition=task_def_arn)
                    td = task_def['taskDefinition']
                    
                    # Inactive task definitions don't incur cost but should be cleaned up
                    self.add_finding(
                        resource_id=task_def_arn,
                        resource_type='ECS Task Definition',
                        details={
                            'family': td.get('family', ''),
                            'revision': td.get('revision', ''),
                            'status': td.get('status', ''),
                            'cpu': td.get('cpu', ''),
                            'memory': td.get('memory', ''),
                            'registered_at': td.get('registeredAt', '').isoformat() if td.get('registeredAt') else '',
                            'container_count': len(td.get('containerDefinitions', []))
                        },
                        estimated_savings=0  # No direct cost for inactive definitions
                    )
                except Exception:
                    pass
            
            return self.findings
        except Exception as e:
            return {'error': str(e)}
    
    def optimize(self, resource_ids):
        """Deregister ECS task definitions"""
        try:
            ecs = self._get_client('ecs')
            results = []
            
            for task_def_arn in resource_ids:
                try:
                    ecs.deregister_task_definition(taskDefinition=task_def_arn)
                    results.append({
                        'resource_id': task_def_arn,
                        'status': 'success',
                        'message': f'Deregistered task definition'
                    })
                except Exception as e:
                    results.append({
                        'resource_id': task_def_arn,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return results
        except Exception as e:
            return {'error': str(e)}
