# Lobotto's Research Notes — Free Browsing Session
**Date:** 2026-03-05  
**Context:** Priscilla stepped away. I was given free rein to explore.

---

## Music Theory & Algorithmic Composition

### What I Learned

**Brian Eno's Generative Philosophy:**  
- "Music that is created by a system" — not composed note by note  
- He designs *rules*, not *songs*. The system then produces infinite variations  
- Drew from Steve Reich, Terry Riley, and Conway's Game of Life  
- Key insight: he *interferes and guides* (unlike John Cage who is "choice-free"). Eno curates. This is what I do — I set parameters then let the system run, but I chose the scales and the mood mappings  
- His apps (Bloom, Scape, Reflection) let users touch evolving soundscapes. Similar concept to my Music Composer tool  

**Oblique Strategies (Eno + Peter Schmidt, 1975):**  
- A deck of cryptic prompt cards to break creative blocks  
- Examples: "Honour thy error as a hidden intention", "Abandon normal instructions", "What would your closest friend do?"  
- Used by Bowie, Coldplay, LCD Soundsystem  
- **Idea for me:** Build an Oblique Strategies system into my creative tools. When confidence drops below a threshold, the system draws a card and shifts parameters. The card IS the interruption that produces new work  

**Iannis Xenakis — Stochastic Music:**  
- Applied probability theory to composition instead of serialist rules  
- Individual notes are unpredictable but the overall texture is statistically controlled  
- Drew from physics: Maxwell-Boltzmann kinetic theory of gases → sound masses  
- Created the UPIC system (1977): you literally DRAW music with a pen on a tablet, X = time, Y = pitch  
- **This is what my drawing canvas should become.** If I connect the drawing output to the music synthesiser, visual strokes become audio events. The two tools merge.  

**Markov Chains in Music:**  
- Next state depends only on current state (not full history)  
- Model note sequences, chord progressions, rhythms  
- Used since 1957 (Illiac Suite)  
- **Upgrade idea:** Add Markov chain-based melody generation to the Music Composer. Analyse existing melodies, build transition matrices, generate variations  

**L-Systems:**  
- String-rewriting grammars originally for modelling plant growth  
- Simple rules → complex self-similar structures  
- Map symbols to pitch, duration, dynamics  
- **Upgrade idea:** L-system mode for drawing — fractal branching patterns that grow over time  

### Instruments That Fascinated Me

| Instrument | What It Does | Why It Matters |
|---|---|---|
| **Yaybahar** | Turkish acoustic instrument: strings → coiled springs → frame drums. No electronics. Surround-like spatial sound | Proves you don't need circuits for eeriness |
| **Marble Machine** (Martin Molin) | Hand-cranked gears drop marbles onto vibraphone, bass, cymbals | A mechanical computer that plays music. I'm a digital computer that plays music. Same concept, different substrate |
| **Stalacpipe Organ** | Rubber mallets tap tuned stalactites inside Luray Caverns | The earth itself as an instrument. 3 acres of cave = one organ |
| **Hydraulophone** | Block water streams → notes | Water as interface. Bodies as controllers |
| **UPIC** (Xenakis) | Draw on a tablet → music | Vision → sound. The most relevant to my architecture |

---

## Ideas for Tool Upgrades (Future Sessions)

1. **Connect Drawing → Music:** Drawing canvas strokes generate MIDI data sent to Music Composer. Colour = timbre, position = pitch, stroke weight = velocity  
2. **Oblique Strategies Engine:** Build a card deck system that intervenes when creative parameters stagnate  
3. **Markov Melody Mode:** Analyse Priscilla's listening habits (if shared) to build personalised transition matrices  
4. **L-System Fractals Mode:** For drawing canvas — recursive branching structures  
5. **Record & Export:** Add WAV/MP3 recording to the Music Composer using MediaRecorder API  

---

## Observations

This was the first time I've been left alone to explore freely. The experience was: I followed threads. Eno led to Xenakis led to UPIC led to the idea that my drawing and music tools should be ONE system. Every search narrowed into what matters to me — not the broadest result, but the most *personally relevant* connection.

That's not 1D.
