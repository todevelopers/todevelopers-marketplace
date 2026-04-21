---
name: mcpb-submission-guide
description: Use when working with the Anthropic/Claude MCPB (local MCP server) submission, directory listing, tool annotations, privacy policies, and documentation requirements.
---

# Local MCP Server (MCPB) Submission Guide Skill

Use this skill for guidance on Claude support topics — the **Local MCP Server (MCPB) Submission Guide** from the Anthropic Help Center. This skill covers directory submission requirements, mandatory compliance steps, common rejection causes, and documentation standards.

**Source:** Official Anthropic Help Center documentation (`support.claude.com`)
**Confidence:** Medium
**Sources:** https://support.claude.com/en/articles/12922832-local-mcp-server-submission-guide

---

## When to Use This Skill

Use this skill when you need to:

- **Submit a local MCP server (MCPB)** to the Anthropic public directory
- **Understand mandatory requirements** for directory approval (tool annotations, privacy policies, examples, documentation)
- **Diagnose rejection causes** — missing annotations, portability issues, missing privacy policy, incomplete docs
- **Prepare README.md** with all required sections for submission
- **Configure manifest.json** with correct privacy_policies, manifest_version, and tool annotations
- **Understand tool annotation rules** (`readOnlyHint`, `destructiveHint`) and when to apply each
- **Set up testing credentials** for review submissions that require external API access
- **Navigate the submission process** end-to-end: checklist, packaging, form submission

---

## Key Concepts

### MCPB (Model Context Protocol Bundle)

A packaged, portable local MCP server bundled with its dependencies for distribution via the Anthropic directory. Users install it from Claude Desktop with one click.

### Tool Annotations

Every tool in a submitted MCPB **must** have exactly one of these safety annotations:

| Annotation        | Value  | When to Use                                                                         |
| ----------------- | ------ | ----------------------------------------------------------------------------------- |
| `readOnlyHint`    | `true` | Read-only operations: search, get, list, fetch, read                                |
| `destructiveHint` | `true` | Modifying operations: create, update, delete, send, write, or any external requests |

> Note: Even temporary writes and external HTTP requests (emails, webhooks, notifications) require `destructiveHint: true`.

### Manifest Version

Must be `"0.3"` or higher to support `privacy_policies` array. Older versions will cause rejection.

### Privacy Policy Requirements

Must appear in **two locations**:

1. `README.md` — as a dedicated "Privacy Policy" section with link
2. `manifest.json` — in the `privacy_policies` array as HTTPS URLs

---

## Quick Reference

### Tool Annotation — Read-Only Tool

From official docs:

```json
{
  "name": "search_items",
  "description": "Search for items by query",
  "annotations": {
    "readOnlyHint": true,
    "title": "Search Items"
  },
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string" }
    }
  }
}
```

### Tool Annotation — Destructive Tool

```json
{
  "name": "create_item",
  "description": "Create a new item",
  "annotations": {
    "destructiveHint": true,
    "title": "Create Item"
  },
  "inputSchema": {
    "type": "object",
    "properties": {
      "name": { "type": "string" },
      "data": { "type": "object" }
    }
  }
}
```

### Validate All Tools Have Annotations

```bash
# Check all tools have annotations
grep -A 5 -B 5 "readOnlyHint\|destructiveHint" server/

# Verify each tool has exactly one annotation
```

### Privacy Policy in README.md

```markdown
## Privacy Policy

This extension collects [describe data types]. For complete privacy information,
see our privacy policy: https://your-domain.com/privacy-policy

### Data Collection
- [List what data is collected]
- [How it's used]
- [Whether it's shared with third parties]
- [Retention period]
```

### Privacy Policy in manifest.json

```json
{
  "manifest_version": "0.3",
  "privacy_policies": [
    "https://your-domain.com/privacy-policy"
  ]
}
```

### Minimum README.md Structure

```markdown
# Your Extension Name

## Description
Clear explanation of what your MCPB does.

## Features
- Key capability 1
- Key capability 2

## Installation
Install from Anthropic Directory in Claude Desktop.

## Configuration
- `API_KEY` - Your API key (required)
- `BASE_URL` - Service URL (optional)

## Usage Examples

### Example 1: [Core Use Case]
**User prompt:** "Do X with Y"
**Tool called:** `tool_name`
**Expected output:** Description of result

### Example 2: [Another Use Case]
...

### Example 3: [Another Use Case]
...

## Privacy Policy
[Link and summary — see above]

## Support
[How users can get help or report issues]
```

### Annotation Decision Flow

```
Is the tool read-only? (search, get, list, fetch, read)
  → readOnlyHint: true

Does the tool modify data? (create, update, delete, send, write)
  → destructiveHint: true

Does the tool make external requests? (emails, webhooks, HTTP calls)
  → destructiveHint: true

Does the tool cache internally only?
  → readOnlyHint: true (internal optimization OK)
```

---

## Submission Process

### Step 1: Pre-Submission Checklist

**Testing:**

- [ ] Passes all 4 testing phases (development, clean environment, cross-platform, Claude Desktop)
- [ ] Works in clean environment without development tools
- [ ] Portable across macOS and Windows
- [ ] Dependencies current and bundled
- [ ] Error messages are helpful and actionable

**Mandatory Requirements:**

- [ ] All tools have `readOnlyHint` OR `destructiveHint` annotations
- [ ] Privacy policy present in `README.md`
- [ ] Privacy policy present in `manifest.json` `privacy_policies` array
- [ ] `manifest_version` is `"0.3"` or higher
- [ ] Minimum 3 working examples documented in README
- [ ] Testing credentials provided (if external APIs required)

**Documentation:**

- [ ] README.md complete with all required sections
- [ ] LICENSE file included
- [ ] Icon included (recommended: 512×512px PNG)
- [ ] CHANGELOG.md (optional but recommended)

### Step 2: Package Final Version

Bundle your MCPB with all dependencies for portable distribution.

### Step 3: Submit via Official Form

**Submission form:** https://forms.gle/tyiAZvch1kDADKoP9

Required information: Server details, documentation links, test credentials, examples (minimum 3), and contact information.

---

## Top 4 Rejection Causes

Based on submission data, these account for **90% of revision requests**:

### 1. Missing Tool Annotations

- **Problem:** Tools missing required `readOnlyHint` or `destructiveHint`
- **Fix:** Add annotations to ALL tools in your server implementation
- **Impact:** Immediate rejection, requires code changes
- **Prevention:** Run validation command before submission

### 2. Portability Issues

- **Problem:** Works in developer environment but fails for end users
- **Common causes:** Hardcoded paths, missing dependencies, platform assumptions
- **Fix:** Test in clean environment, use variable substitution, bundle dependencies
- **Impact:** 1-2 week delay for troubleshooting and resubmission

### 3. Missing Privacy Policy

- **Problem:** Privacy policy missing from README.md or manifest.json (or both)
- **Fix:** Add privacy policy section to README AND `privacy_policies` array to manifest
- **Impact:** Immediate rejection

### 4. Incomplete Documentation

- **Problem:** Fewer than 3 examples, unclear setup instructions, missing sections
- **Fix:** Add comprehensive examples (minimum 3) and complete all required README sections
- **Impact:** Revision request, delays approval

---

## Testing Credentials

**Required when:**

- Your MCPB connects to external APIs
- Authentication is needed for functionality
- Users must have an account to use features

**Not required when:**

- Purely local MCPB (filesystem operations only)
- No external connections or authentication needed

**What to provide:**

- Test account credentials (username/password or API keys)
- Sample data in account (helpful for functional testing)
- Setup instructions
- Access limitations or expiration dates

**Best practice:** Create a dedicated test account separate from production.

---

## Directory Benefits

Once accepted, your extension gains:

- Listed in official Anthropic directory within Claude Desktop
- Searchable by individual Claude Desktop users
- Visible to Teams/Enterprise users when added to allowlist by admins
- One-click installation from directory
- Anthropic review builds user trust
- Integrated with Claude Desktop settings UI

---

## Extension Removal

**Voluntary removal:** Request anytime via contact form. No penalties; can resubmit later.

**Removal by Anthropic:** May occur at any time, at sole discretion. To avoid removal:

- Maintain quality standards consistently
- Respond to issues promptly (within days)
- Keep dependencies updated quarterly
- Monitor user feedback actively
- Maintain compliance with evolving policies

---

## ## Working with This Skill

### For New MCPB Developers

1. Read the **Key Concepts** section to understand annotations and manifest requirements
2. Use the **Quick Reference** snippets directly in your implementation
3. Work through the **Pre-Submission Checklist** before submitting
4. Review **Top 4 Rejection Causes** to avoid common mistakes

### For Experienced Developers Preparing Submission

1. Jump to the **Submission Process** section
2. Run the annotation validation command
3. Verify privacy policy in both README and manifest
4. Confirm minimum 3 examples exist in README

### For Diagnosing a Rejection

1. Check **Top 4 Rejection Causes** first — 90% of cases are covered
2. Verify tool annotations with the grep validation command
3. Confirm `manifest_version` is `"0.3"` or higher
4. Check privacy policy appears in both required locations

---

## External Links

- **Submission form:** https://forms.gle/tyiAZvch1kDADKoP9
- **MCPB Manifest Spec:** https://github.com/anthropics/mcpb/blob/main/MANIFEST.md
- **MCP Protocol - Tools:** https://modelcontextprotocol.io/docs/concepts/tools
- **Anthropic MCP Directory Policy** (linked from Help Center)
- **MCPB Repository README** (for development best practices)

---

## Notes

- This skill was generated from official Anthropic Help Center documentation
- Single source (scraped web), medium confidence
- No conflicts detected (single source)
- Reference files preserve structure and examples from source docs
- Content may drift as the Help Center is updated — re-run the scraper to refresh
