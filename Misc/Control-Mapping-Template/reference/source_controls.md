# SSCF Controls Reference

## Change Control and Configuration Management - CCC

- **CCC-SaaS-01** | Programmatic Configurations Querying | The SaaS platform must support programmatic querying of all current security configurations.

If these concepts exist on the SaaS platform, they must be readable via programmatic querying:

1. Authentication
2. RBAC Assignments
3. Entitlements
4. Permissions
5. Resource ACLs
6. Application-specific security concepts
7. Configurations affecting security log coverage (e.g., enabling/disabling streams)
  - *Details*: Configurations include, but not limited to:
- Authentication
- RBAC Assignments
- Entitlements
- Permissions
- Resource ACLs
- Application-specific security concepts

All security configurations must be readable via API.
  - *Guidelines*: The output of the API should be in a machine-readable format.
- **CCC-SaaS-02** | Configurations Documentation | The SaaS platform must provide up-to-date documentation of all customer-visible, security-relevant configurations and must make it readily available to SaaS customers.

If these concepts exist on the SaaS platform, configuration documentation must include, but not be limited to:
1. Authentication
2. RBAC Assignments
3. Entitlements
4. Permissions
5. Resource ACLs
6 Application-specific security concepts
7. Audit configuration
  - *Details*: Configurations dDocumentation must include, but not limited to:
- Authentication
-RBAC Assignments
-Entitlements
-Permissions
-Resource ACLs
-Application-specific security concepts

Documentation must be readily available to SaaS administrators.
  - *Guidelines*: Documentation should be available via the SaaS provider’s website, within the platform, or community page. Public documentation is recommended.

Documentation should also include versioning and change logs to support traceability and audit requirements.

Any custom language or non-industry standard terms should be explained in detail.

Documentation should include: 
1. Security onboarding documentation. 
2. Focus on the impact of the security configuration.
3. Add default security settings, if applicable. Describe dependencies between configurations, such as one configuration overriding another.
4. Publish the customer responsibility matrix against the Shared Responsibility model, ensuring the customer is aware of what domain areas are supported by the SaaS platform.
- **CCC-SaaS-03** | New Configuration Updates | The SaaS platform must provide notifications about software updates, including new or existing security configuration options, to SaaS customers.
  - *Details*: New security configuration updates must be notified to SaaS administrators. and users.

They can’t be forced to SaaS administrator and users unless specific “strong” security breach urgency or with delay.

Notification can be made via email or dashboard/UI/release notes (RSS)/Webhook
  - *Guidelines*: Updates should have a subscribable mechanism that includes relevant release documentation and changes made to the SaaS platform.

It is recommended that console notifications are visible when these changes take place, in addition to a subscribable mechanism.
- **CCC-SaaS-04** | Security Configuration Guidelines | The SaaS platform must provide SaaS customers with best practice security guidelines for relevant security configurations of the SaaS platform and services.
  - *Details*: The inactive session timeout must allow SaaS administrators to set the inactive session timeout within the SaaS platform or the security configuration API.
  - *Guidelines*: Security Configuration Guidelines should consider best practices in domains like IDP configuration, interface configuration, principles like least privilege, secure SSO configuration, avoidance of long-lived sessions, and application policies.

The SaaS platform should create a subscribable mechanism that includes relevant changes.

Security Configuration Guidelines should be available via the SaaS provider’s website, within the platform, or community page.

## Data Security and Privacy Lifecycle Management - DSP

- **DSP-SaaS-01** | Blocking malicious file uploads | If the SaaS platform allows unrestricted file attachments, it must provide administrative configuration that limits the acceptable file types using an allow list and must provide an option to disable any file uploads.
  - *Details*: (Intentionally Left Blank)

All security features provided must be documented with needed compute region (a map?)
  - *Guidelines*: Motivation: if the platform then exposes the ability to upload files externally (e.g., a support portal), this control is meant to disallow files that may contain malicious code (e.g., office documents)

We recommend that SaaS platforms consider adding file scanning capabilities.

## Identity & Access Management - IAM

- **IAM-SaaS-01** | User Access Visibility | The SaaS platform must have a user management service that allows administrators to identify users via both UI and programmatic means, as well as their authentication mechanisms.
  - *Details*: (Intentionally Left Blank)
  - *Guidelines*: The SaaS platform should include details like:
1. User login mechanisms
2. Last login
3. Last activity
- **IAM-SaaS-02** | User Permissions Enumeration | The SaaS Platform must support enumeration and programmatic querying of all assigned user entitlements.

The platform must provide information about: 
1. Access Permissions
2. Roles
3. Groups
4. Application-specific entitlements
5. Data access entitlements
6. All entitlements for security configuration access.
  - *Details*: The platform should provide information about: 
-Permissions
-Roles
-Groups
-Application specific entitlements
-Data access entitlements
All security configurations must be readable via API.
  - *Guidelines*: User permissions enumeration is SaaS platform-specific, and vendor discretion is advised on entitlements implementation.

The SaaS platform should allow SaaS administrators to see the entitlements assigned to each user.
- **IAM-SaaS-03** | Network Access Restriction | The SaaS platform must support restricting logins/access from outside a SaaS customer's network.

The SaaS platform must offer a minimum of two distinct access rule sets, enabling customers to assign specific user groups to more stringent restrictions (e.g., to further limit administrator-level users to a narrower range of networks).
  - *Details*: (Intentionally Left Blank)
  - *Guidelines*: The SaaS platform should allow for IP restrictions to be separately applied for user logins and integrations, or other non-human connections, including APIs.

Ex. supports IP allowlisting for a SaaS customer instance or the use of a customer-assigned domain.
- **IAM-SaaS-04** | Single Sign-On Support | The SaaS platform must support federated authentication using the most current version of an industry-standard protocol, such as SAML or OIDC.

If SAML is used, then SSO support for SAML must include IdP-initiated and SP-initiated flows.
  - *Details*: If SAML is used then SSO support for SAML must include IDP and SPIF flows
  - *Guidelines*: This cell intentionally left blank
- **IAM-SaaS-05** | Single Sign-On Enforcement | The SaaS platform must support the option of disabling alternative login methods if federated authentication is enabled for users.

The SaaS platform must be able to disable specific users from this enforcement.
  - *Details*: Ability to disable specific users from this enforcement
  - *Guidelines*: The SaaS platform should allow Administrators to set up break-glass accounts with alternative login methods, such as username and password, or sign in with an enterprise account.
- **IAM-SaaS-06** | NHI governance | The SaaS platform must support the identification of Non-Human Identities (NHIs) in UI and via programmatic means.

The SaaS platform must identify NHIs, their type, source/target counterparties, NHI issuance date and expiration (if any, and entitlements.
  - *Details*: Platform identifies NHIs, their type, source/target counterparties, and entitlements
  - *Guidelines*: The SaaS platform should be able to differentiate between non-human identity types (e.g., service accounts), such as third-party integrations, AI agents, marketplace integrations, or custom integrations.

The SaaS platform should provide programmatic access to additional attributes that affect the lifecycles of NHIs, for example:
1. Creation dates of the NHI
2 If applicable, the identity it is delegated from.
3. Access Expiration 
4. Authentication type (secret key, certificate, username and password, etc.)

This would also include application connections, such as users’ tokens on mobile devices.

The SaaS platform should show all entitlements assigned to NHIs (including actions they can take)

NHI accounts should have UI access disabled by default.
- **IAM-SaaS-07** | NHI Revocation | The SaaS platform must support manual and programmatic revocation of Non-Human Identities (NHIs) by SaaS platform administrators and authorized SaaS platform users.
  - *Details*: Separate options to specifically manage NHIs
  - *Guidelines*: NHI revocation should ensure that session invalidation propagates across all access tokens, refresh tokens, and active sessions for the NHIs.

An example of an authorized user would be users who created the credential.
- **IAM-SaaS-08** | User Credentials Management | The SaaS platform must support administrative control of all credentials issued to SaaS platform users.

Administrative control refers to the ability to view, remove, and reset all authentication factors associated with users and user-provisioned credentials.
  - *Details*: (Intentionally Left Blank)
  - *Guidelines*: Examples of such credentials are:
User credentials: password, authenticator apps, application credentials issued in the context of users, passkeys, SMS based factor phone numbers

User-provisioned credentials examples: SSH keys, OAuth refresh tokens, api keys, api tokens, OIDC.

Change in credentials should terminate all active sessions for the user and force re-authentication. Change in permissions should take effect immediately.

SaaS platform administrators access to the private credentials (private keys, Passwords, Tokens, or similar) should not be possible.
- **IAM-SaaS-09** | User provisioning and deprovisioning | The SaaS platform must support automated user provisioning and deprovisioning.

The SaaS platform must have a mechanism to limit the programmatic access of user provisioning and deprovisioning operations.
  - *Details*: Control= View, Remove and reset all authentication factors associated to users, and user provisioned credentials
  - *Guidelines*: The suggested implementation is SCIM. Alternative programmatic methods, such as API calls, are also permissible.
- **IAM-SaaS-10** | Security Auditing Role | The SaaS platform must provide a Security Auditing role for read-only access to all security settings, including log access in UI and via programmatic means.

The Security Auditing role must allow visibility into security configurations and logging data.  

It must not enable viewing or modifying customer data or making changes to any configurations.
  - *Details*: IP restriction is possible
  - *Guidelines*: This cell intentionally left blank
- **IAM-SaaS-11** | Password Rules | The SaaS platform must define password strength requirements or configuration controls to comply with NIST guidelines.

If implemented through configuration controls, the following must be configurable:
1. Set Password length
2. Password reuse
3. Toggle Special Characters required
4. Password expiry
  - *Details*: Support programmatic user provisioning and deprovisioning. 

A mechanism to limit the programmatic access for just user provisioning and deprovisioning operations must exist
  - *Guidelines*: The SaaS platform can support password strength assessment, including already compromised passwords.

SaaS platform administrators should consider industry-wide accepted standards, such as NIST, while configuring this feature. 

This control applies to SaaS users and is not needed for users with delegated authentication (SAML)
- **IAM-SaaS-12** | Multi-Factor Authentication | The SaaS platform must support the use of multi-factor authentication.

The SaaS platform must allow SaaS platform administrators to toggle on and off each factor.

The SaaS platform must have the capability to configure MFA enforcement (The user may not sign in without MFA).
  - *Details*: Access must allow visibility into security configurations and logging data.  

However, it must not enable viewing or modifying customer data or making changes to configurations.
  - *Guidelines*: It is recommended to disallow vulnerable MFA methods (such as SMS) and support phishing-resistant methods.
- **IAM-SaaS-13** | Disabling Anonymous Access | If the SaaS platform supports anonymous access, it must provide a mechanism to disable it globally.
  - *Details*: Must be able to configure:
Set Password length
Password reuse
Toggle Special Characters required
password expiry
  - *Guidelines*: This cell intentionally left blank
- **IAM-SaaS-14** | Disabling External Access for Unmanaged Users | If the SaaS platform supports access for external unmanaged users, it must provide a mechanism to disable it globally.
  - *Details*: Support for one MFA factor that is not SMS or email.

For each factor:
Setting to allow for toggle on/off

Has the capability to configure MFA enforcement (e.g.,i.e., user may not sign in without MFA).
  - *Guidelines*: External unmanaged users can also be referred to as guest users
- **IAM-SaaS-15** | Session Revocation/ Single Sign Out | The SaaS platform must support a process to invalidate a user’s sessions via programmatic means.

Invalidation of the user session must have the capability to revoke user and application sessions (all device and UI sessions) in real-time.
  - *Details*: (Intentionally Left Blank)
  - *Guidelines*: This is commonly referred to as a universal log-out.
- **IAM-SaaS-16** | Entitlements Change Enforcement | The SaaS platform must support immediate enforcement of entitlement changes. 

Where not possible, forced re-authentication is allowed.
  - *Details*: Invalidation of user session has the capability to revoke user and application access in realtime
  - *Guidelines*: The SaaS platform should provide session blocklisting.
- **IAM-SaaS-17** | Temporary Account Suspension | The SaaS platform must support programmatic suspension and reactivation of accounts without requiring their deletion.

When account suspension is invoked, the SaaS platform must suspend or revoke active sessions.
  - *Details*: Privileges must be immediately enforced upon entitlement changes

Where not possible, forced re-authentication is allowed
  - *Guidelines*: Associated Non-Human Identities (NHIs) should be suspended when account suspension is triggered. 

The SaaS platform should allow for the suspension and reactivation of accounts, including any associated Non-Human Identities (NHIs). Upon reactivation, all NHIs linked to the account should be restored without any of them being revoked.
- **IAM-SaaS-18** | Scopes requirements | If the SaaS platform supports a scoped protocol such as OAuth, then granular scopes must be created that allow for least privilege operations.

Read and write scopes are separated.
SaaS administrative actions, such as managing data, must be scoped separately.
  - *Details*: (Intentionally Left Blank)
  - *Guidelines*: While read and write scopes should be provided separately, the application may provide scopes such as manage or administrative, which combine lower-level scopes.
- **IAM-SaaS-19** | Third Party Allowlisting | The SaaS platform must provide administrative controls to allow which third-party integrations can connect by users.
  - *Details*: When this control is invoked , the application must suspend or revoke existing sessions
  - *Guidelines*: If the SaaS platform does not have the ability to manage an allow list, it should allow SaaS platform administrators to block the installation of third-party applications globally by regular users.
- **IAM-SaaS-20** | Inactive Session Timeout | The SaaS platform must support the configuration of inactive UI session timeout settings.

The inactive session timeout must allow SaaS platform administrators to set the inactive UI session timeout within the UI of the SaaS platform or the security configuration API.
  - *Guidelines*: The SaaS platform should have a default inactive session timeout in minutes or hours, not weeks.
- **IAM-SaaS-21** | Restricting User Invites | If users can be provisioned or invited by users other than administrators, the SaaS platform must support restricting this capability to specific roles.
  - *Details*: Read and write scopes are separated
Administrative actions such as managing data must be scoped separately
  - *Guidelines*: The SaaS platform should support the invitation of collaboration users. If such functionality is available, the SaaS platform administrators can restrict by role those users authorized to issue invitations.

## Interoperability & Portability - IPY

- **IPY-SaaS-01** | Export Capability | If the SaaS platform offers mass data export functionality, it must allow SaaS administrators to disable this functionality for non-administrative users.
  - *Details*: (Intentionally Left Blank)
  - *Guidelines*: Export capability should be disabled by default for non-administrative users.
- **IPY-SaaS-02** | Integration Attribution | The SaaS platform must implement a mechanism to allow or deny connections based on the verified creator of the integration. 

When SaaS platform users are prompted to accept integrations (e.g., via a consent screen), the acceptance process must display at least one verifiable attribute of the application's creator, such as their email address domain. This verifiable ownership attribute must be visible both during the acceptance process and in the list of connected integrations, as stipulated in IAM-SaaS-06.

Verification of the integration creator must be performed by the SaaS platform using an application-appropriate mechanism.
  - *Guidelines*: An example of a SaaS platform-appropriate mechanism can be confirmed by the email address of the creator, or the domain used in the OAuth consent (for relevant flows).

## Logging and Monitoring - LOG

- **LOG-SaaS-01** | Logged Events Scope | The SaaS platform must provide security logs to SaaS customers.

Events from both NHIs and humans must be captured in logs, including:
1. Sign in attempts (fail + pass)
2. All configuration changes 
3. Creating integrations, including into other SaaS platforms.
4. Creation, deletion, and/or modification of API keys.
5. OAuth access key generation using a refresh token.
6. User impersonation (including by local administrators or user-to-user role assumption).
7. Creation and modification of user accounts and their permissions
8. Each authentication step, including MFA stages and the factor used.
9. Bulk export and mass data reporting activity.
  - *Details*: Events that must be captured in logs include at least:
-Sign in attempts (fail + pass)
-all configuration changes 
-user level changes of sharing
-creating integrations to other Saas apps
-Creation or modification of API keys
-OAuth access key generation using a refresh token
-user impersonation from local admins
-user to user impersonation
-failed authorization (e.g., accessing URL user is not authorized to)
-Creation and modification of user accounts and their permissions
-Each authentication step, including MFA stages and factor used
-Bulk export and mass data reporting activity
  - *Guidelines*: The logs should be in a machine-readable format (suggested example JSON).

Logs should include
1. All configuration changes that impact the customer UI and configuration.
2. Non-administrative changes.
3. Sharing of objects.

Logs for User Impersonation: the User ID does not need to include email address or full name, just a unique identifier of the impersonating user.
- **LOG-SaaS-02** | Log Records Mandatory Fields | The SaaS platform Logs must contain the following security-relevant information: 
1. Timestamp
2. User ID/username, or NHI ID (If applicable)
3. Impersonation user ID, whether from a customer or SaaS provider.
4. IP address
5. User agent (if applicable)
6. Source of change context (API/UI/App)
7. Action
8. Target resource
9. Non-sensitive session identifier
  - *Details*: Each log must include at least the following fields: 
-timestamp,
-user id, 
-level of permissions
-visibility level
-impersonation user id whether from customer or vendor or application
-ip address
-user agent (if applicable)
-source of change context (API/UI/App)
-action
-target resource
-Non-sensitive session identifier
  - *Guidelines*: The logs should 
1. Describe the source of change - API vs UI vs 3rd party app vs SaaS provider, making changes to customer visible configurations.
2. Describe target resource (field/display names).
3. Describe the session identifier.

If items like an IP address are not applicable, they can be excluded.

For clarity, this only applies to the SaaS platform logs (not backend activity)

Non-sensitive session identifier is a unique identifier representing an authenticated session (not a confidential session value)
- **LOG-SaaS-03** | Programmatic Logs Delivery | The SaaS platform must support programmatic log delivery via a push or pull mechanism.
  - *Guidelines*: The logs should be in a machine-readable format (suggested example JSON). 

Common delivery mechanisms include pulling logs from the SaaS platform API endpoint or automatic delivery from the SaaS platform via webhook or cloud storage bucket.

For SaaS platforms where logs may be delivered out of order and a pull mechanism from the customer is available, customers should be able to query based on log delivery time (as opposed to event time). This prevents gaps for out-of-order logs that are continuously retrieved.
- **LOG-SaaS-04** | Logs Retention | The SaaS platform Logs must be retained and are available to customers.

Logs must be made available to the customer for a minimum of 7 days.
  - *Details*: Logs must be available to customers for at least 7 days.
  - *Guidelines*: It is recommended that logs are available for 30 days or longer for critical log types such as login events.
- **LOG-SaaS-05** | Logs Delivery Latency | The SaaS platform Logs must be delivered without undue delay or latency.

Logs must be made available and deliverable to or by the customer without undue delay, but at most within 24 hours.
  - *Details*: Logs must be made available and retrievable by the customer without undue delay but at most within 24 hours
  - *Guidelines*: The SaaS platform should allow throttling mechanisms to allow the timely delivery of logs to customers.
- **LOG-SaaS-06** | Log Events Documentation | The SaaS platform must provide documentation for log events.

Log format, log types, and specific fields provided by the SaaS platform must be documented and accessible by customers.
  - *Details*: Log format, log types and specific fields provided by the vendor must be documented and accessible by SaaS customers
  - *Guidelines*: Documentation should be available via the SaaS provider’s website, within the platform, or community page. Public documentation is recommended.

Documentation should also include versioning and change logs to support traceability and audit requirements.

Any custom language or non-industry standard terms should be explained in detail.
- **LOG-SaaS-07** | Log Integrity | If the SaaS platform allows logs to be mutable, it must provide an administrative mechanism for logs to be made immutable.
  - *Details*: Logs must be able to be stored in a way which prevents users (including admins) from modifying them.
  - *Guidelines*: The SaaS provider can still be compliant if they have a specific use case that needs mutable logs, provided that a mechanism exists to disable mutability. This is specifically relevant for platforms that deal with data where logs are redirected to a data storage layer, which the customer fully controls (e.g., storage buckets, database tables)

## Security Incident Management, E-Discovery, & Cloud Forensics - SEF

- **SEF-SaaS-01** | Security Event Notification | The SaaS platform must allow setting the security contact who will be notified in case of a security incident.
  - *Details*: (Intentionally Left Blank)
  - *Guidelines*: The SaaS platform should send periodic emails to customers if this contact is not set.
