import json
import boto3
import logging
import hashlib
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssm = boto3.client('ssm')
incidents = boto3.client('ssm-incidents')

RESPONSE_PLAN_ARN = 'arn:aws:ssm-incidents::851725622142:response-plan/RotateKeysOnCompromise'
AUTOMATION_ROLE_ARN = 'arn:aws:iam::851725622142:role/Incident-Manager-Policy'
AUTOMATION_DOCUMENT = 'RotateIAMKeysRunbook'

def generate_client_token(user_name, event_time):
    """
    Generate a client token using user and 15-minute time window.
    Prevents duplicate incidents across short intervals.
    """
    dt = datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%SZ")
    bucket_minute = dt.minute - (dt.minute % 15)
    rounded_time = dt.replace(minute=bucket_minute, second=0)
    raw_string = f"{user_name}-{rounded_time.strftime('%Y%m%dT%H%M')}"
    return hashlib.sha256(raw_string.encode()).hexdigest()

def lambda_handler(event, context):
    detail = event.get('detail', {})
    logger.info("Received event detail: %s", json.dumps(detail))

    try:
        user_name = detail['resource']['accessKeyDetails']['userName']
        logger.info("Extracted IAM user: %s", user_name)
    except KeyError as e:
        logger.error("Missing userName in event detail: %s", e)
        raise

    event_time = event.get('time')
    if not event_time:
        raise ValueError("Event time is missing")

    client_token = generate_client_token(user_name, event_time)
    logger.info("Generated clientToken: %s", client_token)

    try:
        # Start the SSM Automation runbook
        response = ssm.start_automation_execution(
            DocumentName=AUTOMATION_DOCUMENT,
            Parameters={
                'IAMUserName': [user_name],
                'AutomationAssumeRole': [AUTOMATION_ROLE_ARN]
            }
        )
        automation_execution_id = response['AutomationExecutionId']
        logger.info("Started SSM AutomationExecution with ID: %s", automation_execution_id)
    except Exception as e:
        logger.error(f"Failed to start SSM AutomationExecution: {e}")
        raise

    try:
        # Start Incident Manager incident with idempotent clientToken
        incident_response = incidents.start_incident(
            clientToken=client_token,
            responsePlanArn=RESPONSE_PLAN_ARN,
            title=f'IAM Key Compromise detected for user {user_name}',
            impact=1,
            triggerDetails={
                'source': 'AWS Lambda',
                'timestamp': event_time,
                'rawData': json.dumps(detail)
            }
        )
        incident_arn = incident_response['incidentRecordArn']
        logger.info(f"Started Incident Manager incident: {incident_arn}")
    except Exception as e:
        logger.error(f"Failed to start Incident Manager incident: {e}")
        raise

    return {
        'statusCode': 200,
        'body': json.dumps({
            'user': user_name,
            'automationExecutionId': automation_execution_id,
            'incidentArn': incident_arn,
        })
    }
