# Scriptorium Security Policy

## Development and support scope

Scriptorium is an MVP under active development. Security fixes target the
current `main` branch. There is no established supported-release series,
backport schedule, response-time guarantee, or security certification.
Maintainers assess reports and coordinate fixes according to severity and
available capacity.

Reports should identify the Scriptorium commit, WFL version, and pinned Scribe
commit because all three affect behavior. A dependency update is not applied
to existing deployments automatically; site operators must review, test, and
deploy updates.

## Report vulnerabilities privately

Email **info@logbie.com** with the subject `Scriptorium Security Vulnerability`.
Do not open a public issue or PR containing exploit details, credentials, or
private site data. This policy does not depend on GitHub private vulnerability
reporting being enabled.

Include:

- A description of the issue and its likely impact.
- Affected commits or versions and the relevant operating system and configuration.
- A minimal reproduction using synthetic accounts and data.
- The affected routes, roles, or components, and expected versus actual behavior.
- Any suggested mitigation and a contact method for follow-up.

Redact passwords, session IDs, CSRF tokens, personal information, and sensitive
host details. Do not attach a live database or raw production logs. Ask for an
appropriate transfer method if sensitive material is necessary to reproduce an
issue. Test only systems you own or are authorized to assess.

Maintainers investigate privately, determine the affected scope, and coordinate
mitigation, testing, and disclosure. Public security notes should include impact
and upgrade or mitigation guidance when available. Reporter credit is offered
with their consent. Please coordinate publication of details so affected
operators have an opportunity to respond; no fixed embargo period is assumed.

## Application boundaries and current limitations

Scriptorium stores accounts, password hashes, active sessions, content, settings,
media metadata, and login-attempt IP addresses in SQLite. It serves uploaded
files through public `/assets/uploads/*` URLs. An unpublished post does not
make an image uploaded for that post private.

The application uses parameterized SQL, Scribe escaping, password hashing,
session checks, CSRF checks, and ownership/role checks. These controls require
continued testing; they are not a claim that the application has been audited.
Relevant current limitations include:

- **Transport:** the default listener is local HTTP at `127.0.0.1:8080`.
  Session and CSRF cookies use `HttpOnly` and `SameSite=Lax` but currently do
  not set `Secure`. An external deployment must enforce HTTPS and configure
  secure cookie handling at its proxy or through a reviewed application change.
- **First-run setup:** the installer creates the first administrator. Complete
  setup through a controlled access path before exposing a fresh site publicly.
- **Uploads:** the application restricts filename extensions and request size;
  it does not decode images or verify their file signatures. Do not treat the
  extension allowlist as content inspection or malware scanning.
- **Availability:** request handling and login throttling are basic application
  controls. Deployments may need additional connection, traffic, and resource
  limits at the hosting or proxy layer.
- **Extensions and themes:** `app/site_ext.wfl`, theme files, and their configured
  locations are trusted deployment inputs. Extensions run with application
  access to the database and process permissions; this is not an isolation boundary.
- **Storage changes:** schema setup runs at boot and there is no general
  migration or rollback engine. Test upgrades against a disposable copy of the
  existing schema and preserve a recoverable backup before deployment.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for implementation details and
[README.md](README.md) for configuration and storage paths.

## Protect site data

Run with the filesystem and network permissions the site needs. Protect the
database, its journal files, backups, configuration, and any TLS keys from
unauthorized access. Keep backups of both the database and uploaded files and
verify restoration; `data_dir` consolidates their location but does not create
backups. The default locations are `scriptorium.db` and `static/uploads/`.

Keep runtime data, secrets, private drafts, and production logs out of Git,
public issues, shared screenshots, and test fixtures. Processing private data
with an AI service requires the data owner's authorization under
[AI_POLICY.md](AI_POLICY.md); use synthetic test data for development.
Site operators are responsible for their deployed accounts, access, data
retention, backups, and infrastructure. Contributing to this repository does
not authorize access to any live installation.

## Requirements for security-sensitive changes

Preserve authorization and ownership checks, CSRF protection on mutations,
parameterized SQL, safe output rendering, and filesystem path checks. Changes
to authentication, roles, installer state, uploads, paths, migrations, or Scribe
integration need relevant negative and regression tests under
[testing.md](testing.md). Keep sensitive reproductions private until coordinated
disclosure; public fixtures must be sanitized.

Use [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md#reporting) for conduct reports and
[GOVERNANCE.md](GOVERNANCE.md) for authority and policy amendments.

Effective: 2026-09-12.
