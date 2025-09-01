#!/usr/bin/env python3
"""
AWS Lambda handler for MCP Server
Provides serverless MCP server functionality with AWS integrations
"""

import json
import os
import logging
import traceback
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

# AWS SDK imports
import boto3
from botocore.exceptions import ClientError

# MCP Server imports (assuming these exist in your layer)
try:
    from mcp_server import MCPServer, ServerConfig
    from mcp_server.utils import setup_logging, get_config
    from mcp_server.middleware import add_aws_middleware
except ImportError as e:
    logging.error(f"Failed to import MCP server modules: {e}")
    raise

# Configure logging for Lambda
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

# Global variables for connection reuse
mcp_server: Optional[MCPServer] = None
aws_clients: Dict[str, Any] = {}

def get_aws_client(service_name: str):
    """Get or create AWS client with connection reuse."""
    if service_name not in aws_clients:
        aws_clients[service_name] = boto3.client(service_name)
    return aws_clients[service_name]

def get_parameter(parameter_name: str, decrypt: bool = True) -> str:
    """Get parameter from AWS Systems Manager Parameter Store."""
    try:
        ssm = get_aws_client('ssm')
        response = ssm.get_parameter(
            Name=parameter_name,
            WithDecryption=decrypt
        )
        return response['Parameter']['Value']
    except ClientError as e:
        logger.error(f"Failed to get parameter {parameter_name}: {e}")
        raise

def init_mcp_server() -> MCPServer:
    """Initialize MCP server with AWS-specific configuration."""
    global mcp_server
    
    if mcp_server is not None:
        return mcp_server
    
    try:
        # Get configuration from environment and parameter store
        stage = os.environ.get('STAGE', 'dev')
        
        config = ServerConfig(
            # Basic configuration
            host="0.0.0.0",
            port=8000,
            debug=stage == 'dev',
            
            # AWS-specific configuration
            environment='aws-lambda',
            stage=stage,
            region=os.environ.get('REGION', 'us-east-1'),
            
            # Database configuration from Parameter Store
            database_url=get_parameter(f'/mcp-server/{stage}/database-url'),
            redis_url=get_parameter(f'/mcp-server/{stage}/redis-url'),
            secret_key=get_parameter(f'/mcp-server/{stage}/secret-key', decrypt=True),
            
            # Lambda-specific settings
            lambda_context=True,
            connection_pooling=True,
            cache_enabled=True,
            
            # Monitoring configuration
            metrics_enabled=True,
            tracing_enabled=True,
            log_level=os.environ.get('LOG_LEVEL', 'INFO')
        )
        
        # Initialize server
        mcp_server = MCPServer(config)
        
        # Add AWS-specific middleware
        add_aws_middleware(mcp_server)
        
        logger.info("MCP Server initialized successfully")
        return mcp_server
        
    except Exception as e:
        logger.error(f"Failed to initialize MCP server: {e}")
        logger.error(traceback.format_exc())
        raise

def format_lambda_response(status_code: int, body: Any, 
                          headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Format response for Lambda/API Gateway."""
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'X-Request-ID': os.environ.get('AWS_REQUEST_ID', ''),
        'X-Lambda-Function': os.environ.get('AWS_LAMBDA_FUNCTION_NAME', ''),
    }
    
    if headers:
        default_headers.update(headers)
    
    # Handle different body types
    if isinstance(body, (dict, list)):
        response_body = json.dumps(body)
    elif isinstance(body, str):
        response_body = body
    else:
        response_body = str(body)
    
    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': response_body,
        'isBase64Encoded': False
    }

def extract_request_info(event: Dict[str, Any]) -> Dict[str, Any]:
    """Extract request information from Lambda event."""
    # Handle different event sources (API Gateway v1, v2, ALB, etc.)
    if 'httpMethod' in event:
        # API Gateway v1
        return {
            'method': event['httpMethod'],
            'path': event['path'],
            'query_params': event.get('queryStringParameters') or {},
            'headers': event.get('headers') or {},
            'body': event.get('body', ''),
            'is_base64': event.get('isBase64Encoded', False),
            'source_ip': event.get('requestContext', {}).get('identity', {}).get('sourceIp'),
            'user_agent': event.get('requestContext', {}).get('identity', {}).get('userAgent'),
            'request_id': event.get('requestContext', {}).get('requestId'),
        }
    elif 'requestContext' in event and 'http' in event['requestContext']:
        # API Gateway v2 (HTTP API)
        return {
            'method': event['requestContext']['http']['method'],
            'path': event['requestContext']['http']['path'],
            'query_params': event.get('queryStringParameters') or {},
            'headers': event.get('headers') or {},
            'body': event.get('body', ''),
            'is_base64': event.get('isBase64Encoded', False),
            'source_ip': event['requestContext']['http']['sourceIp'],
            'user_agent': event['requestContext']['http']['userAgent'],
            'request_id': event['requestContext']['requestId'],
        }
    else:
        # Direct invocation or other sources
        return {
            'method': 'POST',
            'path': '/',
            'query_params': {},
            'headers': {},
            'body': json.dumps(event) if isinstance(event, dict) else str(event),
            'is_base64': False,
            'source_ip': None,
            'user_agent': None,
            'request_id': None,
        }

def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Main Lambda handler for MCP Server requests.
    
    Args:
        event: Lambda event containing request information
        context: Lambda context object
        
    Returns:
        Lambda response dictionary
    """
    start_time = datetime.utcnow()
    request_id = getattr(context, 'aws_request_id', 'unknown')
    
    # Set request ID in logger context
    logger.info(f"Processing request {request_id}")
    
    try:
        # Extract request information
        request_info = extract_request_info(event)
        
        # Handle preflight CORS requests
        if request_info['method'] == 'OPTIONS':
            return format_lambda_response(200, {'message': 'OK'})
        
        # Initialize MCP server (reuse connection)
        server = init_mcp_server()
        
        # Add Lambda context to request
        request_context = {
            'lambda_context': context,
            'aws_request_id': request_id,
            'function_name': context.function_name,
            'function_version': context.function_version,
            'remaining_time_ms': context.get_remaining_time_in_millis(),
            'memory_limit_mb': context.memory_limit_in_mb,
            'request_start_time': start_time.isoformat(),
        }
        
        # Process request through MCP server
        response = asyncio.run(
            server.process_request(
                method=request_info['method'],
                path=request_info['path'],
                headers=request_info['headers'],
                query_params=request_info['query_params'],
                body=request_info['body'],
                context=request_context
            )
        )
        
        # Log processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.info(f"Request {request_id} processed in {processing_time:.2f}ms")
        
        # Send custom metrics to CloudWatch
        cloudwatch = get_aws_client('cloudwatch')
        try:
            cloudwatch.put_metric_data(
                Namespace='MCP/Server',
                MetricData=[
                    {
                        'MetricName': 'RequestDuration',
                        'Value': processing_time,
                        'Unit': 'Milliseconds',
                        'Dimensions': [
                            {
                                'Name': 'FunctionName',
                                'Value': context.function_name
                            },
                            {
                                'Name': 'Method',
                                'Value': request_info['method']
                            }
                        ]
                    },
                    {
                        'MetricName': 'RequestCount',
                        'Value': 1,
                        'Unit': 'Count',
                        'Dimensions': [
                            {
                                'Name': 'FunctionName',
                                'Value': context.function_name
                            },
                            {
                                'Name': 'StatusCode',
                                'Value': str(response.get('status_code', 200))
                            }
                        ]
                    }
                ]
            )
        except Exception as e:
            logger.warning(f"Failed to send metrics to CloudWatch: {e}")
        
        return format_lambda_response(
            status_code=response.get('status_code', 200),
            body=response.get('body', {}),
            headers=response.get('headers', {})
        )
        
    except Exception as e:
        logger.error(f"Error processing request {request_id}: {e}")
        logger.error(traceback.format_exc())
        
        # Send error metrics
        try:
            cloudwatch = get_aws_client('cloudwatch')
            cloudwatch.put_metric_data(
                Namespace='MCP/Server',
                MetricData=[
                    {
                        'MetricName': 'ErrorCount',
                        'Value': 1,
                        'Unit': 'Count',
                        'Dimensions': [
                            {
                                'Name': 'FunctionName',
                                'Value': getattr(context, 'function_name', 'unknown')
                            },
                            {
                                'Name': 'ErrorType',
                                'Value': type(e).__name__
                            }
                        ]
                    }
                ]
            )
        except:
            pass  # Ignore metrics errors during error handling
        
        return format_lambda_response(
            status_code=500,
            body={
                'error': 'Internal Server Error',
                'message': str(e) if os.environ.get('STAGE') == 'dev' else 'An error occurred',
                'request_id': request_id,
                'timestamp': datetime.utcnow().isoformat()
            }
        )

def lambda_warm_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Handler for warming up the Lambda function to reduce cold starts.
    """
    try:
        # Initialize server to warm up connections
        server = init_mcp_server()
        
        return format_lambda_response(200, {
            'message': 'Lambda warmed up successfully',
            'timestamp': datetime.utcnow().isoformat(),
            'function_name': context.function_name,
            'server_initialized': server is not None
        })
        
    except Exception as e:
        logger.error(f"Error warming up Lambda: {e}")
        return format_lambda_response(500, {
            'error': 'Warm-up failed',
            'message': str(e)
        })

# Export handlers
__all__ = ['handler', 'lambda_warm_handler']