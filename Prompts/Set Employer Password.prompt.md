---
created: 2025-12-09
last_edited: 2025-12-09
version: 1.0
title: Set Employer Password
description: |
  Sets an initial password for an employer user in the Careerspan/Apply AI system.
  This is a one-time operation for employers who exist but have no auth configured yet.
tags:
  - careerspan
  - employer
  - onboarding
  - api
tool: true
---

# Set Employer Password

## What This Does

Calls the Set Employer Password API to:
1. Set an initial password for an employer (must not have any auth configured yet)
2. Optionally provision a default lead/role for them

## Required Information

- **employer_email**: The employer's email address (must already exist in the system)
- **password**: The password to set (1-30 characters). If not provided, a random secure password will be generated.

## Usage

When V says something like:
- "Set up davis@example.com with password XYZ"
- "Create login for employer jane@company.com"
- "Set employer password for bob@acme.com"

Execute:

```bash
python3 N5/scripts/set_employer_password.py <email> --password "<password>"
```

Or if V wants a generated password:

```bash
python3 N5/scripts/set_employer_password.py <email> --generate-password
```

## Flags

- `--password "X"`: Set a specific password (1-30 chars)
- `--generate-password`: Generate a random 20-char password
- `--no-default-role`: Skip provisioning the default lead/role
- `--dry-run`: Show what would happen without calling the API
- `--verbose`: Show full API response

## Important Notes

1. **One-time only**: This endpoint only works for employers with NO existing auth. If they've ever logged in or had a password set, it will fail with 409 Conflict.
2. **Employer must exist**: The email must belong to an existing employer record.
3. **Timeout**: With `provision_default_role` (the default), the API can take 2-4 minutes.
4. **Token**: Zo has FOUNDER_AUTH_TOKEN in secrets—V should NOT need to export anything manually.

## Expected Responses

- **200 OK**: Password set successfully. Will show employer_id, lead_provisioned, new_lead_id.
- **400**: Invalid password (empty or >30 chars), or user is not an employer.
- **404**: User not found with that email.
- **409**: User already has auth configured (can't use this endpoint).
- **401/403**: Auth token issue (check FOUNDER_AUTH_TOKEN in Zo secrets).

