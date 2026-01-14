import os
import json
from cryptography.fernet import Fernet
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from pathlib import Path

class CredentialManager:
    """Manages secure storage and validation of AWS credentials"""
    
    def __init__(self):
        self.creds_dir = Path.home() / ".aws_optimizer"
        self.creds_dir.mkdir(exist_ok=True)
        self.key_file = self.creds_dir / ".key"
        self.creds_file = self.creds_dir / "credentials.enc"
        self._ensure_key()
    
    def _ensure_key(self):
        """Create or load encryption key"""
        if not self.key_file.exists():
            key = Fernet.generate_key()
            self.key_file.write_bytes(key)
        self.key = Fernet(self.key_file.read_bytes())
    
    def save_credentials(self, access_key, secret_key, region="us-east-1"):
        """Save credentials with encryption"""
        creds = {
            "access_key": access_key,
            "secret_key": secret_key,
            "region": region
        }
        encrypted = self.key.encrypt(json.dumps(creds).encode())
        self.creds_file.write_bytes(encrypted)
        return True
    
    def load_credentials(self):
        """Load encrypted credentials"""
        if not self.creds_file.exists():
            return None
        try:
            encrypted = self.creds_file.read_bytes()
            decrypted = self.key.decrypt(encrypted).decode()
            return json.loads(decrypted)
        except Exception:
            return None
    
    def validate_credentials(self, access_key=None, secret_key=None):
        """Validate AWS credentials"""
        try:
            if access_key and secret_key:
                sts = boto3.client(
                    'sts',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key
                )
            else:
                creds = self.load_credentials()
                if not creds:
                    return {"valid": False, "error": "No credentials found"}
                sts = boto3.client(
                    'sts',
                    aws_access_key_id=creds['access_key'],
                    aws_secret_access_key=creds['secret_key'],
                    region_name=creds.get('region', 'us-east-1')
                )
            
            identity = sts.get_caller_identity()
            return {
                "valid": True,
                "account_id": identity['Account'],
                "arn": identity['Arn'],
                "user": identity['Arn'].split('/')[-1]
            }
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_map = {
                'InvalidClientTokenId': 'Invalid access key ID',
                'SignatureDoesNotMatch': 'Invalid secret access key',
                'UnrecognizedClientException': 'Invalid credentials format'
            }
            return {"valid": False, "error": error_map.get(error_code, str(e))}
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def clear_credentials(self):
        """Clear stored credentials"""
        if self.creds_file.exists():
            self.creds_file.unlink()
        return True
