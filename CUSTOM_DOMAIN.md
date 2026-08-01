# Custom domain plan — placeholder.io

**Status:** pending — waiting for the user to buy the domain and point DNS.
**Goal:** `placeholder.io/dontforget` serves dontforget; `placeholder.io` serves the org root page (0x8338 茸); old `0x8338.github.io/dontforget` URLs redirect to the custom domain.

## Why this works

Set the custom domain on the **org root repo** (`0x8338.github.io`), not on dontforget.

GitHub Pages behavior: when an org/user site has a custom domain, all project sites
owned by the same account are served at `customdomain/<repo>`.

- `placeholder.io` → org root page (0x8338 茸, born 20260624)
- `placeholder.io/dontforget` → dontforget
- future org projects → `placeholder.io/<repo>` automatically
- `0x8338.github.io/dontforget` → redirects automatically to `placeholder.io/dontforget`

No code changes needed: all links in `0x8338.github.io` and `dontforget` are relative
or root-relative, so they adapt to whichever domain/path is serving them.

## DNS records (at the registrar, after buying the domain)

| Name | Type | Value |
|---|---|---|
| `placeholder.io` | A | `185.199.108.153` |
| `placeholder.io` | A | `185.199.109.153` |
| `placeholder.io` | A | `185.199.110.153` |
| `placeholder.io` | A | `185.199.111.153` |
| `www.placeholder.io` | CNAME | `0x8338.github.io` |

Some registrars support CNAME/ALIAS flattening for apex domains — that works too.
Keep the www record; GitHub auto-redirects between apex and www.

## GitHub configuration (only after DNS is live)

1. Repo `0x8338.github.io` → Settings → Pages → Custom domain → `placeholder.io` → Save.
   - This writes a `CNAME` file with `placeholder.io` into the org root repo.
2. Wait for HTTPS certificate provisioning (a few minutes), then tick **Enforce HTTPS**.
3. Recommended: org Settings → Pages → Verified domains → verify `placeholder.io`.

## Cautions

- Do **not** set the custom domain before DNS resolves — the current github.io site
  would redirect to a dead domain and break.
- Do **not** set the custom domain on the `dontforget` repo itself — that would make
  dontforget take over the whole domain root and break `placeholder.io/dontforget`.

## When the user returns

1. Ask for the real domain name (replace `placeholder.io` everywhere).
2. Confirm DNS records resolve (`dig` / `nslookup`).
3. Configure GitHub side (CNAME file + Pages settings via web or API).
4. Verify: `placeholder.io` → org root, `placeholder.io/dontforget` → dontforget,
   `0x8338.github.io/dontforget` → redirect, HTTPS enforced.
