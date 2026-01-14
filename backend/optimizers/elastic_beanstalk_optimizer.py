from .base_optimizer import BaseOptimizer
from datetime import datetime, timedelta

class ElasticBeanstalkOptimizer(BaseOptimizer):
    """Terminate unused Elastic Beanstalk environments"""
    
    def analyze(self):
        """Find terminated Elastic Beanstalk environments"""
        try:
            eb = self._get_client('elasticbeanstalk')
            
            response = eb.describe_environments()
            
            for env in response.get('Environments', []):
                env_id = env['EnvironmentId']
                env_name = env['EnvironmentName']
                status = env['Status']
                
                # Flag environments that are in terminated or terminating state
                if status in ['Terminated', 'Terminating']:
                    # Estimate based on typical environment cost ~$20/month
                    monthly_cost = 20.0
                    
                    self.add_finding(
                        resource_id=env_id,
                        resource_type='Elastic Beanstalk Environment',
                        details={
                            'environment_id': env_id,
                            'environment_name': env_name,
                            'status': status,
                            'platform': env.get('PlatformArn', ''),
                            'date_created': env.get('DateCreated', '').isoformat() if env.get('DateCreated') else '',
                            'date_updated': env.get('DateUpdated', '').isoformat() if env.get('DateUpdated') else ''
                        },
                        estimated_savings=monthly_cost
                    )
            
            return self.findings
        except Exception as e:
            return {'error': str(e)}
    
    def optimize(self, resource_ids):
        """Terminate Elastic Beanstalk environments"""
        try:
            eb = self._get_client('elasticbeanstalk')
            results = []
            
            for env_id in resource_ids:
                try:
                    # Get environment info to get name
                    response = eb.describe_environments(EnvironmentIds=[env_id])
                    if response['Environments']:
                        env_name = response['Environments'][0]['EnvironmentName']
                        
                        eb.terminate_environment(
                            EnvironmentId=env_id,
                            ForceTerminate=True
                        )
                        results.append({
                            'resource_id': env_id,
                            'status': 'success',
                            'message': f'Terminated environment {env_name}'
                        })
                except Exception as e:
                    results.append({
                        'resource_id': env_id,
                        'status': 'failed',
                        'error': str(e)
                    })
            
            return results
        except Exception as e:
            return {'error': str(e)}
