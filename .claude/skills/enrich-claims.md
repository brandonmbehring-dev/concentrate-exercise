# /enrich-claims - Enhance Claims with KB Context

Use research-kb to validate technical claims and suggest enhancements based on literature.

## Usage
```
/enrich-claims <category>
```

Categories: `causal`, `ml`, `forecasting`, `experimentation`, `all`

## Instructions

When this command is invoked:

1. **Load claims by category**:
   - Read `ACTIVE_DOCUMENTS/resume_system/master/claims.yml`
   - Filter claims by tag matching the category
   - Focus on claims tagged: pricing, experimentation, ml, forecasting, causal

2. **For each technical claim, query research-kb**:

   a. **Validate technical terminology**:
      - Use `research_kb_search` to verify method names are correct
      - Check if claimed methods exist in literature (no hallucinated terms)

   b. **Suggest enhancement opportunities**:
      - Use `research_kb_graph_neighborhood` to find related concepts
      - Could the claim reference more specific/impressive methods?
      - Example: "machine learning" → "causal forests" or "double machine learning"

   c. **Cross-reference with literature**:
      - Use `research_kb_list_sources` to find seminal papers
      - Could add "(building on Chernozhukov et al., 2018)" type references

3. **Generate enhancement report**:
   ```
   Claims Enhancement Report: <Category>
   =====================================

   ## Validated Claims (terminology correct)
   - [claim_id]: [bullet text] ✓

   ## Enhancement Opportunities
   - [claim_id]: [bullet text]
     Current: "[generic term]"
     Suggest: "[specific method from KB]"
     Rationale: [why this is more impressive/accurate]

   ## Terminology Upgrades
   - "machine learning models" → "causal machine learning methods"
   - "statistical analysis" → "quasi-experimental analysis"
   - "forecasting" → "probabilistic forecasting with conformal prediction"

   ## Literature References to Consider
   - For [claim about DML]: cite Chernozhukov et al. (2018)
   - For [claim about IV]: cite Angrist & Pischke
   ```

4. **Important constraints**:
   - NEVER suggest fabricating experience
   - Only enhance terminology for methods you actually used
   - Flag any claims that seem overclaimed vs. literature definitions

## Example Output

```
/enrich-claims causal

Claims Enhancement Report: Causal Inference
============================================

## Validated Claims (terminology correct)
- exp_pru_price_001: "Built causal inference models for price elasticity" ✓
  → Method confirmed: causal inference is standard terminology

## Enhancement Opportunities

### exp_pru_price_002
Current: "Used machine learning for pricing optimization"
Suggest: "Applied double machine learning for heterogeneous treatment effects in pricing"
Rationale: DML is the modern standard for causal ML; you implemented cross-fitting

### exp_pru_price_003
Current: "Analyzed customer behavior"
Suggest: "Estimated customer-level treatment effects using causal forests"
Rationale: More specific, demonstrates knowledge of modern causal ML

## Terminology Upgrades
- "statistical models" → "causal identification strategies"
- "A/B testing" → "randomized experiments with heterogeneous effect estimation"
- "feature importance" → "causal feature attribution" (if applicable)

## Literature Anchors
- Price elasticity work aligns with: Chernozhukov et al. (2018) DML
- Feature reduction aligns with: LASSO for causal inference (Belloni et al.)

---
⚠️ Remember: Only use terms for methods you actually implemented!
```

## Integration with Claims Bank

After running this command:
1. Review suggestions with domain expertise
2. Update `claims.yml` only for accurate enhancements
3. Maintain validation against `VERIFIED_FACTS_FINAL.md`
4. Re-run `make validate_all` after any changes
