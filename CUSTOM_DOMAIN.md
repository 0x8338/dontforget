# Custom domain plan — 0x8338.com

**Status:** in progress — domain bought on Namecheap; DNS + GitHub setup pending.
**Goal:** `0x8338.com/dontforget` serves dontforget; `0x8338.com` serves the org root page (0x8338 茸); old `0x8338.github.io/dontforget` URLs redirect to the custom domain.

## Why this works

Set the custom domain on the **org root repo** (`0x8338.github.io`), not on dontforget.

GitHub Pages behavior: when an org/user site has a custom domain, all project sites
owned by the same account are served at `customdomain/<repo>`.

- `0x8338.com` → org root page (0x8338 茸, born 20260624)
- `0x8338.com/dontforget` → dontforget
- future org projects → `0x8338.com/<repo>` automatically
- `0x8338.github.io/dontforget` → redirects automatically to `0x8338.com/dontforget`

No code changes needed: all links in `0x8338.github.io` and `dontforget` are relative
or root-relative, so they adapt to whichever domain/path is serving them.

## DNS records (at the registrar, after buying the domain)

| Name | Type | Value |
|---|---|---|
| `0x8338.com` | A | `185.199.108.153` |
| `0x8338.com` | A | `185.199.109.153` |
| `0x8338.com` | A | `185.199.110.153` |
| `0x8338.com` | A | `185.199.111.153` |
| `www.0x8338.com` | CNAME | `0x8338.github.io` |

Some registrars support CNAME/ALIAS flattening for apex domains — that works too.
Keep the www record; GitHub auto-redirects between apex and www.

## GitHub configuration (only after DNS is live)

1. Repo `0x8338.github.io` → Settings → Pages → Custom domain → `0x8338.com` → Save.
   - This writes a `CNAME` file with `0x8338.com` into the org root repo.
2. Wait for HTTPS certificate provisioning (a few minutes), then tick **Enforce HTTPS**.
3. Recommended: org Settings → Pages → Verified domains → verify `placeholder.io`.

## Cautions

- Do **not** set the custom domain before DNS resolves — the current github.io site
  would redirect to a dead domain and break.
- Do **not** set the custom domain on the `dontforget` repo itself — that would make
  dontforget take over the whole domain root and break `placeholder.io/dontforget`.

## When the user returns

1. Confirm DNS records resolve (`dig` / `nslookup`).
2. Set custom domain on the org root repo via Settings/API (CNAME file).
3. Verify: `0x8338.com` → org root, `0x8338.com/dontforget` → dontforget,
   `0x8338.github.io/dontforget` → redirect, HTTPS enforced.
