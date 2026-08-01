# Design Notes — dontforget

## Voice & Language

| DO | DON'T |
|---|---|
| "Died by suicide" | "Committed suicide" |
| Plain language, short sentences | Corporate tone, jargon |
| Humble, objective, attentive | Pressure words ("like," "prefer," "need") |
| Offer options | Push choices on fluid emotional states |

## Imagery

- No gore, death images, or last-moment recordings
- Prefer text and source links over images
- No repeated photos of the deceased; no method/scene photos

## Color & Typography

- Muted, reflective palettes. Greens, blues, purples reduce anxiety. Warm tones promote security.
- Readable fonts, ≥4.5:1 contrast, generous spacing.
- Dark/light mode toggle. Respect system preferences. Never force one mode.

## Content Warnings

```
[Content warning] ▼ See why
┌─────────────────────────────────┐
│ This page describes a fatal     │
│ crash and its aftermath.        │
│ [Show content] [Go back]        │
└─────────────────────────────────┘
```

Implementation rules:
- **Obscure by default; reveal on explicit choice.** Hidden content must not leak to browser find-in-page.
- **Two-level warnings:** general label first + optional "See why" expander. Over-specific labels can distress.
- **Announce reveals to screen readers** (`role="alert"`).

## Accessibility

- Grief and trauma act as cognitive-impairment conditions — keep cognitive load minimal
- Crisis resources on pages referencing suicide
- No registration walls — the site has no accounts

## No Comments

The site has no comment system. Submissions and corrections arrive via GitHub Issues.
