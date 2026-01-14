import boto3
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

class BaseOptimizer(ABC):
    """Base class for all optimization techniques"""
    
    def __init__(self, access_key, secret_key, region='us-east-1'):
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key
        self.dry_run = True  # Safe by default
        self.findings = []
    
    def _get_client(self, service):
        """Get AWS service client"""
        return boto3.client(
            service,
            region_name=self.region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )
    
    def _get_resource(self, service):
        """Get AWS service resource"""
        return boto3.resource(
            service,
            region_name=self.region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )
    
    @abstractmethod
    def analyze(self):
        """Analyze resources for optimization"""
        pass
    
    @abstractmethod
    def optimize(self, resource_ids):
        """Perform optimization"""
        pass
    
    def add_finding(self, resource_id, resource_type, details, estimated_savings=0):
        """Add a finding"""
        self.findings.append({
            'resource_id': resource_id,
            'resource_type': resource_type,
            'details': details,
            'estimated_savings': estimated_savings,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_findings(self):
        """Get all findings"""
        return self.findings
