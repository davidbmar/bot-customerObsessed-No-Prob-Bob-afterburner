# afterburner-customer-bot Project Status — 2026-03-21 (Sprint 20: Hands-free VAD, input filter, echo cancellation, fast path)

## Sprint 20 Summary

Sprint 20 goal: Add hands-free continuous speech mode with browser-side VAD (Silero VAD WASM) (F-049).
Additional: Input quality filter — drop garbage STT before hitting LLM (F-048).
Additional: Echo cancellation — mute mic while TTS is playing (F-050).
Additional: Configurable silence threshold for hands-free mode (F-051).
Additional: Fast path — instant answers for simple queries without LLM (F-052).

---

## What Changed

### agentA-input-filter-fastpath

Input quality filter and fast path for STT

**Commits:**
- 1d68359 feat: input quality filter and fast path for STT (F-048, F-052)

**Files:** See git log for details

### agentB-hands-free-vad

Hands-free continuous speech with browser-side VAD, echo cancellation, silence threshold

**Commits:**
- d79166f feat: hands-free continuous speech with browser-side VAD, echo cancellation, silence threshold

**Files:** See git log for details

---

## Merge Results

| # | Branch | Deliverable | Phase | Conflicts |
|---|--------|-------------|-------|-----------|
| 1 | agentA-input-filter-fastpath | Input quality filter and fast path for STT (F-048, F-052) | 1 | Clean |
| 2 | agentB-hands-free-vad | Hands-free VAD, echo cancellation, silence threshold (F-049, F-050, F-051) | 1 | Backlog conflict resolved |

---

## Backlog Snapshot

### Completed This Sprint
- F-048: Input quality filter
- F-049: Hands-free continuous speech mode with browser-side VAD
- F-050: Echo cancellation
- F-051: Configurable silence threshold
- F-052: Fast path for simple queries

### Still Open
- See backlog for current status

---

## Next Steps

- See sprint 21 brief for next planned work
