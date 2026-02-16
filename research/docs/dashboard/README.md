# Concentrate Dashboard Capture

**Captured**: 2026-02-16
**Source**: https://app.concentrate.ai (authenticated via GitHub OAuth)
**Account**: Brandon Behring (brandon_m_behr)

## Files

| File | Page | Content |
|------|------|---------|
| `dashboard-overview.md` / `.png` | /dashboard | Summary stats, cost/usage charts, spend by provider/model |
| `model-fortress.md` / `.png` | /model-fortress | All 52 available models with pricing |
| `billing.md` / `.png` | /billing | Credit balance, transaction history |
| `guardrails.md` / `.png` | /guardrails | Entity taxonomy (no key selected) |
| `guardrails-with-key.md` / `.png` | /guardrails?key=... | Guardrails config for brandon_m_behr key |
| `api-keys.md` / `.png` | /api-keys | Key metadata, usage, limits |

## Key Findings

### Account Status
- **Balance**: $9.95 remaining (of $10.00)
- **Total Spend**: $0.05 (28 requests, 7,609 tokens)
- **Active Keys**: 1 (`brandon_m_behr`, sk-cn-v1...cf3a)
- **Key Limit**: unlimited
- **Last Used**: ~41 minutes before capture

### Model Inventory (52 total, 4 target models verified)

| Model | Slug | Author | Input $/M | Output $/M | Reasoning | Context |
|-------|------|--------|-----------|------------|-----------|---------|
| ChatGPT 5.1 | `gpt-5.1` | OpenAI | $1.25 | $10.00 | Yes | 400K |
| Claude Sonnet 4.5 | `claude-sonnet-4-5` | Anthropic | $3.00 | $15.00 | Yes | 200K |
| Gemini 2.5 Pro | `gemini-2.5-pro` | Google | $1.25 | $10.00 | Yes | 1.0M |
| Grok 4.1 Fast Reasoning | `grok-4-1-fast-reasoning` | xAI | $0.20 | $0.50 | Yes | 2.0M |

**All 4 models exist. All prices match hardcoded values exactly.**

### Pricing Cross-Reference

| Provider | Our Value (input/output) | Dashboard | Match? |
|----------|-------------------------|-----------|--------|
| OpenAI (gpt-5.1) | $1.25/$10.00 | $1.25/$10.00 | YES |
| Anthropic (claude-sonnet-4-5) | $3.00/$15.00 | $3.00/$15.00 | YES |
| Google (gemini-2.5-pro) | $1.25/$10.00 | $1.25/$10.00 | YES |
| xAI (grok-4-1-fast-reasoning) | $0.20/$0.50 | $0.20/$0.50 | YES |

**No code changes needed. All hardcoded values are correct.**

### Spend by Provider (from smoke test runs)
- vertex: $0.03 (77%)
- anthropic: $0.01 (16%)
- openai: $0.00 (6%)
- xai: $0.00 (1%)

### Guardrails Configuration
- **Status**: Disabled for brandon_m_behr key
- **Redact on**: Both (input + output) — default setting
- **Streaming caveat**: "Output will not be redacted if the response is streamed"
- **Entity categories** (7 groups, 40+ entity types):
  1. Personally Identifiable Information: PERSON, EMAIL, PHONE, SSN, DATE_OF_BIRTH, AGE, DRIVERS_LICENSE, PASSPORT, LOCATION, USERNAME
  2. Payment Card Industry: CREDIT_CARD, CREDIT_CARD_CVV, ACCOUNT_NUMBER, IBAN, AMOUNT, CRYPTO_ADDRESS
  3. Protected Health Information: PATIENT, STAFF, HOSPITAL, PATIENT_ID, MEDICAL_RECORD_NUMBER, NPI, MEDICAL_CONDITION, MEDICATION, OTHER_PHI
  4. Credentials & Secrets: PASSWORD, JWT_TOKEN, AWS_ACCESS_KEY, AWS_SECRET_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, AZURE_API_KEY, GCP_SERVICE_ACCOUNT
  5. Technical Identifiers: IP_ADDRESS, MAC_ADDRESS, URL, UUID, VIN
  6. Organizations: ORGANIZATION
  7. Temporal Data: DATE

### Budget Assessment for Phase E
- **Available**: $9.95
- **Estimated Phase E cost**: ~$3.27
- **Remaining after Phase E**: ~$6.68
- **Verdict**: Full execution approved — no scope cuts needed
