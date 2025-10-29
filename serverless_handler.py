"""
AWS Lambda handler for serverless deployment
"""
import json
from mangum import Mangum
from main import app

# Lambda handler
handler = Mangum(app, lifespan="off")


def lambda_handler(event, context):
    """
    AWS Lambda entry point
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        API Gateway response
    """
    return handler(event, context)
