# AWS IAM Key Compromise Incident Automation

![Architecture Diagram](https://github.com/user-attachments/assets/40a03ef3-cd07-4c5b-95fd-ba7aaae15413)

This AWS Lambda function automates the detection and response to IAM Access Key compromise events.

## Features

- **Automatic IAM key rotation**: Triggers a predefined SSM Automation Document to rotate compromised keys securely
- **Incident creation**: Opens an incident with contextual details to notify the right responders
- **Duplicate incident prevention**: Uses a stable client token based on user and event timestamp rounded to 15 minutes
- **Robust error handling**: Logs detailed AWS service errors for easier troubleshooting

## Architecture

The solution consists of the following AWS services working together:

1. **AWS Lambda** - Core automation logic
2. **Amazon EventBridge** - Event routing and filtering
3. **AWS Systems Manager** - Automation and incident management
4. **AWS IAM** - Secure access and execution roles
5. **AWS CloudWatch** - Logging and monitoring

## Deployment Components

### 1. AWS Lambda Function (`GuardDutyTranslator`)
- Extracts user and event info from the event
- Starts SSM Automation to rotate IAM keys
- Creates SSM Incident Manager incident
- Prevents duplicate incidents with a client token

### 2. Amazon EventBridge(`Trigger-GuardDuty-Incident`)
- Rule: `Trigger-GuardDuty-Incident`
- Filters events from source: `custom.guardduty.simulation`
- Event pattern:
  ```json
  {
    "source": ["custom.guardduty.simulation"],
    "detail-type": ["GuardDuty Finding"],
    "detail": {
      "type": ["UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration"],
      "severity": [8.0]
    }
  }
