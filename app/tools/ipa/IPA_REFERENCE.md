# IPA Phonemes Reference - Sammy Animations

## Overview
This document provides a complete reference of all 45 English phoneme animations generated from the Sammy Interactive Sagittal Section.

---

## 📂 File Organization

```
app/tools/
├── sammy_consonants_gifs/      (24 consonant animations)
├── sammy_vowels_gifs/          (21 vowel animations)
├── sammy_all_english_ipa.py    (Generation script)
├── sammy_integration_example.py (Integration example)
└── SAMMY_README.md             (Documentation)
```

---

## 🗣️ CONSONANTS (24 sounds)

### Stops (6)
| IPA | File | Example | Description |
|-----|------|---------|-------------|
| p | `p.gif` | **p**it | Voiceless bilabial stop |
| b | `b.gif` | **b**it | Voiced bilabial stop |
| t | `t.gif` | **t**ip | Voiceless alveolar stop |
| d | `d.gif` | **d**ip | Voiced alveolar stop |
| k | `k.gif` | **k**it | Voiceless velar stop |
| g | `g.gif` | **g**et | Voiced velar stop |

### Fricatives (9)
| IPA | File | Example | Description |
|-----|------|---------|-------------|
| f | `f.gif` | **f**at | Voiceless labiodental fricative |
| v | `v.gif` | **v**at | Voiced labiodental fricative |
| θ | `θ.gif` | **th**ink | Voiceless dental fricative |
| ð | `ð.gif` | **th**is | Voiced dental fricative |
| s | `s.gif` | **s**it | Voiceless alveolar fricative |
| z | `z.gif` | **z**oo | Voiced alveolar fricative |
| ʃ | `ʃ.gif` | **sh**ip | Voiceless postalveolar fricative |
| ʒ | `ʒ.gif` | mea**s**ure | Voiced postalveolar fricative |
| h | `h.gif` | **h**at | Voiceless glottal fricative |

### Affricates (2)
| IPA | File | Example | Description |
|-----|------|---------|-------------|
| tʃ | `tʃ.gif` | **ch**urch | Voiceless postalveolar affricate |
| dʒ | `dʒ.gif` | **j**udge | Voiced postalveolar affricate |

### Nasals (3)
| IPA | File | Example | Description |
|-----|------|---------|-------------|
| m | `m.gif` | **m**at | Bilabial nasal |
| n | `n.gif` | **n**ap | Alveolar nasal |
| ŋ | `ŋ.gif` | si**ng** | Velar nasal |

### Approximants (4)
| IPA | File | Example | Description |
|-----|------|---------|-------------|
| l | `l.gif` | **l**et | Alveolar lateral approximant |
| ɹ | `ɹ.gif` | **r**ed | Alveolar approximant (American R) |
| j | `j.gif` | **y**es | Palatal approximant |
| w | `w.gif` | **w**et | Labial-velar approximant |

---

## 🎵 VOWELS (21 sounds)

### Front Vowels (5)
| IPA | File | Example | Description |
|-----|------|---------|-------------|
| i | `i.gif` | b**ee** | Close front unrounded |
| ɪ | `ɪ.gif` | b**i**t | Near-close front unrounded |
| e | `e.gif` | ch**ao**s | Close-mid front unrounded |
| ɛ | `ɛ.gif` | b**e**d | Open-mid front unrounded |
| æ | `æ.gif` | c**a**t | Near-open front unrounded |

### Central Vowels (3)
| IPA | File | Example | Description |
|-----|------|---------|-------------|
| ə | `ə.gif` | **a**bout | Mid central (schwa) |
| ʌ | `ʌ.gif` | c**u**p | Open-mid back unrounded |
| ɜ | `ɜ.gif` | b**ir**d | Open-mid central unrounded |

### Back Vowels (5)
| IPA | File | Example | Description |
|-----|------|---------|-------------|
| u | `u.gif` | b**oo**t | Close back rounded |
| ʊ | `ʊ.gif` | b**oo**k | Near-close back rounded |
| o | `o.gif` | b**oa**t | Close-mid back rounded |
| ɔ | `ɔ.gif` | th**ough**t | Open-mid back rounded |
| ɑ | `ɑ.gif` | f**a**ther | Open back unrounded |
| ɒ | `ɒ.gif` | g**o**t (UK) | Open back rounded |

### Diphthongs (5)
| IPA | File | Example | Description |
|-----|------|---------|-------------|
| eɪ | `eɪ.gif` | f**a**ce | From mid-front to high-front |
| aɪ | `aɪ.gif` | pr**i**ce | From low-front to high-front |
| ɔɪ | `ɔɪ.gif` | ch**oi**ce | From mid-back to high-front |
| aʊ | `aʊ.gif` | m**ou**th | From low to high-back |
| oʊ | `oʊ.gif` | g**oa**t | From mid-back to high-back |

### R-colored Vowels (2)
| IPA | File | Example | Description |
|-----|------|---------|-------------|
| ɝ | `ɝ.gif` | b**ir**d | Stressed r-colored schwa |
| ɚ | `ɚ.gif` | butt**er** | Unstressed r-colored schwa |

---

## 🎯 Usage in PhonoEcho

### 1. **Pronunciation Feedback**
Display the correct articulatory position when a learner mispronounces a phoneme.

```python
from app.tools.sammy_integration_example import display_articulation_feedback

# Show feedback for /θ/ sound
display_articulation_feedback('θ', title="How to pronounce 'th' in 'think'")
```

### 2. **Side-by-Side Comparison**
Compare target pronunciation with detected pronunciation.

```python
from app.tools.sammy_integration_example import display_phoneme_comparison

# Compare target /θ/ with detected /s/
display_phoneme_comparison(target_phoneme='θ', user_phoneme='s')
```

### 3. **Interactive Learning Module**
Let learners explore different phonemes and their articulations.

```python
import streamlit as st
from pathlib import Path

phoneme = st.selectbox("Select a phoneme to learn:", ['θ', 'ð', 's', 'z', ...])
animation_path = Path(f"app/tools/sammy_consonants_gifs/{phoneme}.gif")
st.image(str(animation_path))
```

---

## 🔧 Technical Details

### Animation Properties
- **Format**: Animated GIF
- **Resolution**: High (captured at 2x device scale)
- **Frame Rate**: 12 FPS
- **Pause Frames**: 8 frames at the end for readability
- **File Size**: ~34-35 KB per animation

### Sagittal Section Elements
Each animation shows:
- **Lips**: Position (spread, rounded, closed)
- **Tongue**: Constriction location and degree
- **Velum**: Raised (oral) or lowered (nasal)
- **Vocal Folds**: Vibrating (voiced) or not (voiceless)
- **IPA Symbol**: Displayed on the right side

---

## 📚 References

1. **Sammy Interactive Sagittal Section**: https://incl.pl/sammy/
   - Created by Daniel Currie Hall
   - Based on diagrams from "The Sounds of Language" by Henry Rogers

2. **International Phonetic Alphabet**: https://www.internationalphoneticassociation.org/
   - Official IPA chart and symbols

3. **IPA for American English**:
   - 24 consonant phonemes
   - 14-16 vowel monophthongs (dialect-dependent)
   - 5 major diphthongs
   - 2 r-colored vowels (rhotic dialects)

---

## 🚀 Future Enhancements

1. **Animated Transitions**: Generate multi-frame animations showing articulatory movements
2. **Coarticulation**: Show how phonemes blend in connected speech
3. **Regional Variations**: Generate variations for different English accents
4. **Interactive Controls**: Let users manipulate tongue/lip positions directly
5. **Audio Sync**: Pair animations with audio samples of each phoneme

---

## 📝 Notes

- Some animations may show similar positions for phonemes that differ mainly in voicing (e.g., /p/ vs /b/)
- The Sammy website doesn't have separate controls for every vowel height/backness combination, so some vowel positions are approximations
- Diphthongs show the starting position only; full animations would require multiple frames
- R-colored vowels use the retroflex tongue position as an approximation

---

## ✅ Checklist for Integration

- [ ] Copy `sammy_consonants_gifs/` to PhonoEcho assets folder
- [ ] Copy `sammy_vowels_gifs/` to PhonoEcho assets folder
- [ ] Import `sammy_integration_example.py` functions into main app
- [ ] Update pronunciation error detection to trigger animations
- [ ] Add animations to the learning interface
- [ ] Test with actual user pronunciation data
- [ ] Gather user feedback on animation usefulness
- [ ] Consider adding text descriptions alongside animations

---

**Generated**: October 8, 2025  
**Total Animations**: 45 (24 consonants + 21 vowels)  
**Script**: `sammy_all_english_ipa.py`  
**Dependencies**: playwright, imageio
