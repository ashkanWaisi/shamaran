# Design QA — Copper Archive Web UI

- Source: selected Copper Archive desktop reference
- Implementation: locally captured production build
- Comparison: side-by-side local review of source and implementation
- Desktop viewport: 1487 × 1058
- Mobile viewport: 390 × 844

## Verification

- Layout: three-column desktop shell, fixed top status bar, central chat canvas, and responsive mobile drawer behavior verified.
- Typography: Inter, Vazirmatn, JetBrains Mono, and serif display hierarchy render without clipping.
- Colors: aubergine navigation surfaces, warm ivory canvas, copper controls, and semantic connection states match the selected direction.
- Assets: official Shamaran symbol is used in the header, welcome state, and assistant messages.
- Interactions: chat submission, live Ollama response, model selector, settings tabs, language switching, RTL layout, memory filtering, mutation control, and responsive drawers verified.
- Accessibility: semantic buttons and inputs, labels, alt text, keyboard submission, focus styles, and responsive tap targets present.
- Browser console: no warnings or errors during desktop, chat, Persian, Sorani, and mobile checks.
- Comparison history: pass 1 identified the target's denser populated state; the implementation preserves the selected layout and surfaces while supplying a production-ready empty state and real chat state.

final result: passed
