# 06 - Policy and Compliance Pattern

- Do not scrape or automate a platform unless `config/platform_policy.yaml` explicitly permits the exact action and cites the permission source.
- Treat `manual_only`, `disabled`, missing, and unknown policies as hard blocks.
- Never implement CAPTCHA solving, fingerprint spoofing, stealth plugins, proxy rotation intended to evade controls, hidden browser automation, or rate-limit evasion.
- Proposal submission defaults to human action.
- API submission requires both an explicit feature flag and a per-action confirmation token.
- Direct outreach must be targeted, relevant, rate-limited, auditable, and approved before sending.
- Log policy decisions, action IDs, and outcomes without secrets or confidential full texts.
