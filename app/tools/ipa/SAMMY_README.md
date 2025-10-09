# Sammy IPA Animation Generator

This tool automatically downloads all English vowel and consonant animations from the [Sammy Interactive Sagittal Section](https://incl.pl/sammy/) website.

## Features

- 🎯 **24 English Consonants**: All stops, fricatives, affricates, nasals, and approximants
- 🎵 **20+ English Vowels**: Monophthongs, diphthongs, and r-colored vowels
- 📁 **Organized Output**: Separate directories for consonants and vowels
- 🖼️ **High Quality**: SVG-based rendering at 2x scale for crisp animations

## Installation

1. Install required packages:
```bash
pip install -r sammy_requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

## Usage

Run the script to download all IPA animations:

```bash
python sammy_all_english_ipa.py
```

The script will create two directories:
- `sammy_consonants_gifs/` - Contains 24 consonant animations
- `sammy_vowels_gifs/` - Contains 20+ vowel animations

## Generated Phonemes

### Consonants (24)
**Stops**: p, b, t, d, k, g  
**Fricatives**: f, v, θ, ð, s, z, ʃ, ʒ, h  
**Affricates**: tʃ, dʒ  
**Nasals**: m, n, ŋ  
**Approximants**: l, ɹ, j, w  

### Vowels (20+)
**Front**: i, ɪ, e, ɛ, æ  
**Central**: ə, ʌ, ɜ  
**Back**: u, ʊ, o, ɔ, ɑ, ɒ  
**Diphthongs**: eɪ, aɪ, ɔɪ, aʊ, oʊ  
**R-colored**: ɝ, ɚ  

## Integration with PhonoEcho

These animations can be used as visual feedback in the PhonoEcho pronunciation learning system to help learners understand the articulatory positions for each sound.

## Notes

- The script uses Playwright to automate browser interactions
- Each animation is saved as a GIF file named after its IPA symbol
- Default settings: 1 frame (static posture), 8 pause frames for readability
- Adjust `FRAMES` variable for animated transitions between articulations

## Troubleshooting

If you encounter issues with specific phonemes, check:
1. The radio button selectors in the CONSONANTS/VOWELS dictionaries
2. The Sammy website structure hasn't changed
3. Your browser has loaded the page completely

## Credits

- Sammy Interactive Sagittal Section by [Daniel Currie Hall](http://incl.pl/dch/)
- IPA charts from the [International Phonetic Association](https://www.internationalphoneticassociation.org/)
