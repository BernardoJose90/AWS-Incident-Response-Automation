AWS IAM Key Compromise Incident Automation

Overview

This AWS Lambda function automates the detection and response to IAM Access Key compromise events by:

Starting an AWS Systems Manager (SSM) Automation runbook to rotate compromised IAM keys.
Creating an incident in AWS Systems Manager Incident Manager to alert your security team.
Preventing duplicate incidents for the same user within a 15-minute window using idempotent client tokens.

Features

Automatic IAM key rotation: Triggers a predefined SSM Automation Document to rotate compromised keys securely.
Incident creation: Opens an incident with contextual details to notify the right responders.
Duplicate incident prevention: Uses a stable client token based on user and event timestamp rounded to 15 minutes.
Robust error handling:  Logs detailed AWS service errors for easier troubleshooting.
Structured logging: Logs include AWS request IDs to correlate events in CloudWatch.


Architecture

<img width="974" alt="Screenshot 2025-06-16 at 18 51 08" src="https://github.com/user-attachments/assets/5e266f72-df68-4eae-b4ea-6e322d3ceb55" />



Deployment

1. AWS Lambda
Created a Lambda function called GuardDutyTranslator where core automation logic is located.
This function is used for:

  --Extracting user and event info from the event.
  
  --Starting an SSM Automation to rotate IAM keys.
  
  --Creating an SSM Incident Manager incident.
  
  --Preventing duplicate incidents with a client token.


 2. Amazon EventBridge
Used EventBridge for Event routing to the Lambda function called GuardDutyTranslator.

Used for: Creating the rule Trigger-GuardDuty-Incident.

  --Filtering events from a custom source: custom.guardduty.simulation.
  
  --Triggering the Lambda function based on GuardDuty using JSON payload to simulate the events.
    Event pattern filters on:
      {
        "source": ["custom.guardduty.simulation"],
        "detail-type": ["GuardDuty Finding"],
        "detail": {
          "type": ["UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration"],
          "severity": [8.0]
        }
      }


 3. AWS Systems Manager (SSM), SSM Automation, used for: Automatically rotating IAM keys.
  Components:
  Runbook (RotateIAMKeysRunbook) containing steps like:

    --disableAccessKeys
    
    --deleteAccessKeys
    
    --createNewAccessKey

Execution Role: AutomationAssumeRole with permissions like:

    --iam:ListAccessKeys
    
    --iam:UpdateAccessKey
    
    --iam:DeleteAccessKey
    
    --iam:CreateAccessKey

b. SSM Incident Manager used for creating and tracking security incidents by using start_incident API Feature defined in my lambda function.

    --Response plan ARN (e.g. RotateKeysOnCompromise)
    
    --Sending contextual details and raw event data to responders.


c. SSM Contacts, where I defined my contact. Purpose: Notify responders via escalation plans (email).

    --Permission included: ssm-contacts:StartEngagement Note: Only active if a contact/engagement plan is part of the response plan.

 4. AWS IAM Purpose is to provide secure access and execution roles.

   a. Lambda Execution Role (GDKTranslatorRole) with permissions:
      --ssm:StartAutomationExecution
      
      --ssm-incidents:StartIncident
      
      --ssm-contacts:StartEngagement
      
      --iam:PassRole

      --AWSLambdaBasicExecutionRole
      
      --AmazonSSMAutomationRole


    b. SSM Automation Role (AutomationAssumeRole) with permissions:
      --iam:ListAccessKeys
      
      --iam:UpdateAccessKey
      
      --iam:DeleteAccessKey
      
      --iam:CreateAccessKey


 5. AWS CLI
Used AWS CLI to Manually injecting test events using put-events.
Example:
aws events put-events \
  --region eu-west-2 \
  --entries '[
  {
    "Source": "custom.guardduty.simulation",
    "DetailType": "GuardDuty Finding",
    "Detail": "{\"severity\":8.0,\"type\":\"UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration\",\"title\":\"Potential Credential Exfiltration\",\"resource\":{\"resourceType\":\"AccessKey\",\"accessKeyDetails\":{\"accessKeyId\":\"YOUR_ACCESS_KEY_HERE\",\"userName\":\"YOUR_IAM_USERNAME_HERE\"}},\"region\":\"eu-west-2\",\"id\":\"test-id-001\",\"accountId\":\"YOUR_ACCOUNT_ID_HERE\"}",
    "EventBusName": "default"
  }
]’
 
6. AWS CloudWatch us used cloudwatch for:

    --Logging Lambda execution.
    
    --Tracking automation/document runs.
