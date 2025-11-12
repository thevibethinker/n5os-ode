# Productivity Dashboard - Staging Environment

## URLs
- Production: https://productivity-dashboard-va.zocomputer.io
- Staging: https://productivity-dashboard-staging-va.zocomputer.io

## Workflow

1. Make changes in STAGING first
2. Test at staging URL
3. Promote to production when ready:
   cp /home/workspace/Sites/productivity-dashboard-staging/index.tsx /home/workspace/Sites/productivity-dashboard/index.tsx
4. Restart production service

## Service IDs
- Staging: svc_vnjiBBqkuh0 (port 3001)
- Production: svc_J6eAPxM04_4 (port 3000)
