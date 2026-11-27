# super-skill — Brand Guidelines | ब्रांड दिशानिर्देश | ब्रांड गाइडलाइन्स

Content available in **English · हिंदी · Hinglish**.

---

## 1. Taglines / टैगलाइन / टैगलाइन्स

| English | हिंदी | Hinglish |
|---|---|---|
| **One skill. Every task.** | **एक स्किल। हर काम।** | **Ek skill. Har kaam.** |
| Give the task. The skill routes it. | काम दो — रास्ता स्किल खुद चुनेगा। | Seedha task do — skill khud choose karega. |
| 65+ sources. 7 playbooks. Zero setup. | 65+ स्रोत। 7 प्लेबुक। शून्य सेटअप। | 65+ sources. 7 playbooks. Zero setup. |
| Plan → Execute → Verify → Deliver. | योजना → क्रियान्वयन → जाँच → वितरण। | Plan → Execute → Verify → Deliver. |

---

## 2. Color Palette / रंग पैलेट

| Role | Name | Hex | Use |
|---|---|---|---|
| Primary | **Router Violet** | `#7c3aed` | Logo, CTAs, accents, route lines |
| Accent | **Route Cyan** | `#22d3ee` | Secondary highlight, endpoints, links |
| Background | **Ink** | `#0f1115` | Page background (dark-first) |
| Surface | **Panel** | `#171a21` | Cards, chips |
| Border | **Steel** | `#2a2f3a` | Dividers, card borders |
| Text | **Mist** | `#e8eaf0` | Headings & body on dark |
| Muted | **Slate** | `#9aa0ae` | Secondary text |
| Success | **Verified Green** | `#34d399` | OK states, "AUTO-MODE active" |
| Warning | **Gate Amber** | `#fbbf24` | Caveats, permission-gated |

Gradient (logo): `linear-gradient(135deg, #7c3aed → #22d3ee)`

---

## 3. Typography / टाइपोग्राफी

- **Stack**: `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`
- **Mono**: `ui-monospace, "SF Mono", Menlo, monospace` (code, chips)
- Display: 2.4rem / 700 / -0.02em tracking
- Section head: 0.8rem / 600 / uppercase / 0.14em tracking
- Body: 1rem / 400 / 1.6 line-height
- Caption: 0.84rem

हिंदी के लिए: same stack Devanagari render karta hai; fallback
`Noto Sans Devanagari` ho to behtar.

---

## 4. Voice & Tone / स्वर और शैली

**English**
- Direct and structured — answer first, evidence second.
- Cite every claim; label estimates as estimates.
- Honest about limits and failures.
- Safety rules are never joked with.

**हिंदी**
- सीधा और व्यवस्थित — पहले उत्तर, फिर प्रमाण।
- हर दावे का स्रोत दें; अनुमान को अनुमान ही कहें।
- सीमाएँ और असफलताएँ ईमानदारी से बताएँ।
- सुरक्षा नियमों में कोई ढिलाई नहीं।

**Hinglish**
- Seedha aur structured — pehle answer, phir evidence.
- Har claim ka source do; estimate ko estimate bolo.
- Limits aur failures clear batao — chhupana nahi.
- Safety rules mein koi comedy nahi.

---

## 5. Logo Usage / लोगो उपयोग

**DO ✅**
- Keep clear space = radius of the center node on all sides.
- Gradient mark on dark backgrounds (`#0f1115`).
- Mono (single-color) version on light or busy backgrounds.
- Minimum size: icon 24px, full lockup 120px wide.

**DON'T ❌**
- Stretch, rotate, or recolor arbitrarily.
- Add drop shadows, outlines, or glow to the mark.
- Place gradient logo on mid-tone or photo backgrounds.
- Recreate the wordmark in a different font.

---

## 6. Assets / एसेट्स

| File | Use |
|---|---|
| `logo-icon.svg` | Avatar, favicon, app icon (7-branch node) |
| `logo-primary.svg` | Full lockup on dark backgrounds |
| `logo-mono.svg` | Single-color (`currentColor`) — light/print |
| `design/hero.jpg` | Hero visual — 7-path router poster |
| `design/index.html` | Product page (live example of the brand) |
| `index.html` (this folder) | Interactive brand kit |

**Social avatar**: icon on Router Violet circle.
**Banner**: hero visual left-aligned + lockup + tagline (per language).

---

## 7. Language Selection / भाषा चयन

| Context | Language |
|---|---|
| Docs, code comments, international users | English |
| Official communication, articles (Devanagari) | हिंदी |
| Casual chat, quick demos, social (this user) | Hinglish |

Rule: **match the user's language in replies**; keep identifiers/code in English.
