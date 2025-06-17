# AWS Automated Incident Response Solutions

This repository provides automated incident response solutions for two common security scenarios in AWS:

1. **Public S3 Bucket Remediation**
2. **IAM Access Key Compromise**

Each solution is event-driven, uses AWS-native services, and integrates with Systems Manager Incident Manager for structured response and tracking.

---

## 📌 Table of Contents

- [S3 Bucket Public Access Remediation](#-s3-bucket-public-access-remediation)
  - [Features](#features)
  - [Architecture Overview](#architecture-overview)
  - [Key Components](#key-components)
- [IAM Key Compromise Incident Automation](#-iam-key-compromise-incident-automation)
  - [Features](#features-1)
  - [Architecture](#architecture)
  - [Deployment Components](#deployment-components)

---

## 🪣 S3 Bucket Public Access Remediation

![S3 Public Workflow](https://github.com/user-attachments/assets/d6d2351e-293f-4890-a2a0-5f58eb9f4112)

Automated remediation workflow to detect and mitigate public S3 buckets.

### Features

- **Detection**: Integrated with AWS Security Hub.
- **Remediation**: Automatically revokes public access from S3 buckets.
- **Comprehensive Tracking**: Incident lifecycle tracked via AWS Systems Manager.
- **Alerting**: Email notifications via Incident Manager.
- **Audit Trail**: Full logging of all remediation actions.

### Architecture Overview

#### Core Workflow

1. **Detection**
   - Security Hub detects a public S3 bucket.
2. **Remediation**
   - Triggered SSM Automation Runbook performs:
     - ACL lockdown
     - Bucket policy update
     - Enabling `BlockPublicAccess`
3. **Incident Management**
   - AWS Systems Manager Incident Manager is triggered.
4. **Notification**
   - Email alerts sent via Incident Manager's SNS integration.

### Key Components

| Component           | Description                                 | AWS Service                    |
|--------------------|---------------------------------------------|--------------------------------|
| **Detection Layer**| Identifies public S3 buckets                | AWS Security Hub               |
| **Orchestrator**   | Coordinates remediation                     | AWS Lambda                     |
| **Remediation**    | Executes fixes via Runbook                  | AWS Systems Manager Automation |
| **Incident Tracker**| Tracks incident lifecycle                  | AWS Systems Manager Incident Manager |

---

## 🔐 IAM Key Compromise Incident Automation

<img width="1031" alt="Screenshot 2025-06-17 at 23 58 12" src="https://github.com/user-attachments/assets/b0892769-dd53-4fe0-9f38-9369c2657480" />

This solution detects and remediates IAM access key compromises using a fully automated Lambda-based workflow.

### Features

- **Automatic IAM Key Rotation**: Uses SSM Automation Documents to rotate compromised keys.
- **Incident Creation**: Security incidents created in Incident Manager.
- **Duplicate Prevention**: Client token prevents redundant incidents for same user-event window.
- **Robust Logging**: Detailed AWS service errors are logged to CloudWatch for troubleshooting.

### Architecture

This automation uses the following AWS services:

1. **AWS Lambda** – Core logic for parsing GuardDuty findings and triggering remediation.
2. **Amazon EventBridge** – Filters GuardDuty findings and routes to Lambda.
3. **AWS Systems Manager** – Executes Automation Documents and manages incidents.
4. **AWS IAM** – Executes secure roles and handles key rotation.
5. **AWS CloudWatch** – Provides centralized logging and metrics.

### Deployment Components

#### 1. AWS Lambda Function (`GuardDutyTranslator`)

- Parses IAM user and event data.
- Initiates key rotation via SSM Automation.
- Opens an Incident Manager incident with contextual metadata.
- Deduplicates events using a time-windowed client token.

#### 2. Amazon EventBridge (`Trigger-GuardDuty-Incident`)

- EventBridge rule filters GuardDuty findings with specific conditions:
  ```json
  {
    "source": ["custom.guardduty.simulation"],
    "detail-type": ["GuardDuty Finding"],
    "detail": {
      "type": ["UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration"],
      "severity": [8.0]
    }
  }
