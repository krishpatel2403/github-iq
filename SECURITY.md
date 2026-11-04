# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.0   | ✅        |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Please report security issues responsibly:

1. Email the maintainer directly (see GitHub profile)
2. Or use GitHub's [private vulnerability reporting](https://github.com/<your-username>/github-iq/security/advisories/new)

Include:
- Description of the vulnerability
- Steps to reproduce
- Affected components and versions
- Potential impact
- Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide a status update within 7 days.

## Security Best Practices for Users

- Never commit `.env` files — they contain OAuth secrets and encryption keys
- Rotate `GITHUB_TOKEN_ENCRYPTION_KEY` and `SESSION_SECRET_KEY` if compromised
- Use PostgreSQL instead of SQLite for production deployments
- Keep dependencies updated via Dependabot (configured in `.github/dependabot.yml`)

## Security Features

- GitHub OAuth access tokens encrypted at rest (Fernet)
- Session cookies: HttpOnly, SameSite=Lax, Secure (production)
- CSRF protection via OAuth state parameter
- Input validation via Pydantic v2 schemas
- No secrets logged or exposed in error responses
- CORS restricted to frontend origin
