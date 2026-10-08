# Acme Analytics — Security Policy (Summary)

- All customer data encrypted at rest (AES-256) and in transit (TLS 1.3).
- SSO enforced for Enterprise workspaces (SAML 2.0 / OIDC).
- Penetration testing performed twice a year by an external firm.
- Incident severity levels: SEV1 (data breach) requires notification within 24 hours to security@acme-analytics.example and the DPO.
- Employees must complete security training quarterly; phishing simulation failure rate target < 4%.
- AI agents operating on company data must NOT store credentials in memory or logs; use the project's proxy key only via environment configuration.
