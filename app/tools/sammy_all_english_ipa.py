"""
Automated IPA Animation Generator using Sammy Interactive Sagittal Section
Downloads all English vowels and consonants as GIF animations
Website: https://incl.pl/sammy/
"""

import asyncio
from pathlib import Path
import imageio.v2 as imageio
from playwright.async_api import async_playwright

# Output directories
CONSONANTS_DIR = Path("sammy_consonants_gifs")
VOWELS_DIR = Path("sammy_vowels_gifs")
FRAMES = 1  # static posture (increase for animations)
FPS = 12
PAUSE_FRAMES = 8  # hold the final frame for readability

URL = "https://incl.pl/sammy/"

# ==============================================================================
# ENGLISH CONSONANTS (24 sounds)
# ==============================================================================
CONSONANTS = {
    # === STOPS (6) ===
    "p": {  # voiceless bilabial stop
        "name": "p - voiceless bilabial stop",
        "selectors": ["input#voiceless", "input#oral", "input#blstop", "input#rest"]
    },
    "b": {  # voiced bilabial stop
        "name": "b - voiced bilabial stop",
        "selectors": ["input#voiced", "input#oral", "input#blstop", "input#rest"]
    },
    "t": {  # voiceless alveolar stop
        "name": "t - voiceless alveolar stop",
        "selectors": ["input#voiceless", "input#oral", "input#spread", "input#td"]
    },
    "d": {  # voiced alveolar stop
        "name": "d - voiced alveolar stop",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#td"]
    },
    "k": {  # voiceless velar stop
        "name": "k - voiceless velar stop",
        "selectors": ["input#voiceless", "input#oral", "input#spread", "input#kg"]
    },
    "g": {  # voiced velar stop
        "name": "g - voiced velar stop",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#kg"]
    },
    
    # === FRICATIVES (9) ===
    "f": {  # voiceless labiodental fricative
        "name": "f - voiceless labiodental fricative",
        "selectors": ["input#voiceless", "input#oral", "input#labdent", "input#rest"]
    },
    "v": {  # voiced labiodental fricative
        "name": "v - voiced labiodental fricative",
        "selectors": ["input#voiced", "input#oral", "input#labdent", "input#rest"]
    },
    "θ": {  # voiceless dental fricative (think)
        "name": "θ - voiceless dental fricative",
        "selectors": ["input#voiceless", "input#oral", "input#spread", "input#theta"]
    },
    "ð": {  # voiced dental fricative (this)
        "name": "ð - voiced dental fricative",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#theta"]
    },
    "s": {  # voiceless alveolar fricative
        "name": "s - voiceless alveolar fricative",
        "selectors": ["input#voiceless", "input#oral", "input#spread", "input#sz"]
    },
    "z": {  # voiced alveolar fricative
        "name": "z - voiced alveolar fricative",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#sz"]
    },
    "ʃ": {  # voiceless postalveolar fricative (ship)
        "name": "ʃ - voiceless postalveolar fricative",
        "selectors": ["input#voiceless", "input#oral", "input#spread", "input#esh"]
    },
    "ʒ": {  # voiced postalveolar fricative (measure)
        "name": "ʒ - voiced postalveolar fricative",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#esh"]
    },
    "h": {  # voiceless glottal fricative
        "name": "h - voiceless glottal fricative",
        "selectors": ["input#voiceless", "input#oral", "input#spread", "input#rest"]
    },
    
    # === AFFRICATES (2) ===
    "tʃ": {  # voiceless postalveolar affricate (church)
        "name": "tʃ - voiceless postalveolar affricate",
        "selectors": ["input#voiceless", "input#oral", "input#spread", "input#esh"]
    },
    "dʒ": {  # voiced postalveolar affricate (judge)
        "name": "dʒ - voiced postalveolar affricate",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#esh"]
    },
    
    # === NASALS (3) ===
    "m": {  # bilabial nasal
        "name": "m - bilabial nasal",
        "selectors": ["input#voiced", "input#nasal", "input#blstop", "input#rest"]
    },
    "n": {  # alveolar nasal
        "name": "n - alveolar nasal",
        "selectors": ["input#voiced", "input#nasal", "input#spread", "input#td"]
    },
    "ŋ": {  # velar nasal (sing)
        "name": "ŋ - velar nasal",
        "selectors": ["input#voiced", "input#nasal", "input#spread", "input#kg"]
    },
    
    # === APPROXIMANTS (4) ===
    "l": {  # alveolar lateral approximant
        "name": "l - alveolar lateral approximant",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#td"]
    },
    "ɹ": {  # alveolar approximant (red) - approximated with retroflex position
        "name": "ɹ - alveolar approximant",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#retroflex"]
    },
    "j": {  # palatal approximant (yes)
        "name": "j - palatal approximant",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#palatal"]
    },
    "w": {  # labial-velar approximant (we)
        "name": "w - labial-velar approximant",
        "selectors": ["input#voiced", "input#oral", "input#rounded", "input#kg"]
    },
}

# ==============================================================================
# ENGLISH VOWELS (Monophthongs + Diphthongs)
# Note: Sammy doesn't have explicit vowel controls, so we use tongue positions
# The actual IPA transcription may vary based on lip, tongue, and voicing settings
# ==============================================================================
VOWELS = {
    # === FRONT VOWELS ===
    "i": {  # close front unrounded (bee) - high front spread
        "name": "i - close front unrounded",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#palatal"]  # high front
    },
    "ɪ": {  # near-close front unrounded (bit) - slightly lower
        "name": "ɪ - near-close front unrounded",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#palatal"]  # approximation
    },
    "e": {  # close-mid front unrounded (chaos)
        "name": "e - close-mid front unrounded",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#palatal"]
    },
    "ɛ": {  # open-mid front unrounded (bed) - mid front
        "name": "ɛ - open-mid front unrounded",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#palatal"]
    },
    "æ": {  # near-open front unrounded (cat) - low front
        "name": "æ - near-open front unrounded",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#theta"]  # front low approximation
    },
    
    # === CENTRAL VOWELS ===
    "ə": {  # mid central (schwa - about) - rest position
        "name": "ə - mid central schwa",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#rest"]
    },
    "ʌ": {  # open-mid back unrounded (cup) - similar to schwa but slightly back
        "name": "ʌ - open-mid back unrounded",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#rest"]
    },
    "ɜ": {  # open-mid central unrounded (bird) - r-colored with retroflex
        "name": "ɜ - open-mid central unrounded",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#retroflex"]
    },
    
    # === BACK VOWELS ===
    "u": {  # close back rounded (boot) - high back rounded
        "name": "u - close back rounded",
        "selectors": ["input#voiced", "input#oral", "input#rounded", "input#uvular"]  # high back
    },
    "ʊ": {  # near-close back rounded (book) - slightly lower
        "name": "ʊ - near-close back rounded",
        "selectors": ["input#voiced", "input#oral", "input#rounded", "input#uvular"]
    },
    "o": {  # close-mid back rounded (boat)
        "name": "o - close-mid back rounded",
        "selectors": ["input#voiced", "input#oral", "input#rounded", "input#kg"]  # velar position
    },
    "ɔ": {  # open-mid back rounded (thought) - mid-low back rounded
        "name": "ɔ - open-mid back rounded",
        "selectors": ["input#voiced", "input#oral", "input#rounded", "input#kg"]
    },
    "ɑ": {  # open back unrounded (father) - low back unrounded
        "name": "ɑ - open back unrounded",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#uvular"]  # back low
    },
    "ɒ": {  # open back rounded (British 'got') - low back rounded
        "name": "ɒ - open back rounded",
        "selectors": ["input#voiced", "input#oral", "input#rounded", "input#uvular"]
    },
    
    # === DIPHTHONGS (using start positions) ===
    "eɪ": {  # (face) - mid front to high front
        "name": "eɪ - face diphthong",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#palatal"]
    },
    "aɪ": {  # (price) - low front to high front
        "name": "aɪ - price diphthong",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#theta"]
    },
    "ɔɪ": {  # (choice) - mid back rounded to high front
        "name": "ɔɪ - choice diphthong",
        "selectors": ["input#voiced", "input#oral", "input#rounded", "input#kg"]
    },
    "aʊ": {  # (mouth) - low to high back rounded
        "name": "aʊ - mouth diphthong",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#theta"]
    },
    "oʊ": {  # (goat) - mid back rounded to high back
        "name": "oʊ - goat diphthong",
        "selectors": ["input#voiced", "input#oral", "input#rounded", "input#kg"]
    },
    
    # === R-COLORED VOWELS (Rhotic) ===
    "ɝ": {  # stressed r-colored schwa (bird)
        "name": "ɝ - stressed r-colored schwa",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#retroflex"]
    },
    "ɚ": {  # unstressed r-colored schwa (butter)
        "name": "ɚ - unstressed r-colored schwa",
        "selectors": ["input#voiced", "input#oral", "input#spread", "input#retroflex"]
    },
}


async def check_radios(page, selectors):
    """Check/click the specified radio button selectors"""
    for sel in selectors:
        try:
            el = page.locator(sel)
            await el.wait_for(state="visible", timeout=3000)
            try:
                await el.check()
            except:
                await el.click()
        except Exception as e:
            print(f"  Warning: Could not click {sel}: {e}")


async def capture_phoneme(page, sammy, symbol, config, output_path):
    """Capture a single phoneme animation"""
    frames = []
    
    # Capture frames
    for f in range(FRAMES):
        await check_radios(page, config["selectors"])
        await page.wait_for_timeout(40)
        png = await sammy.screenshot(type="png")
        frames.append(png)
    
    # Add pause frames
    if PAUSE_FRAMES:
        frames.extend([frames[-1]] * PAUSE_FRAMES)
    
    # Save as GIF
    imgs = [imageio.imread(b) for b in frames]
    imageio.mimsave(output_path, imgs, duration=1 / max(FPS, 1))
    print(f"  ✓ {config['name']} → {output_path.name}")


async def run():
    """Main execution function"""
    # Create output directories
    CONSONANTS_DIR.mkdir(parents=True, exist_ok=True)
    VOWELS_DIR.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as pw:
        print("🚀 Launching browser...")
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            device_scale_factor=2
        )
        page = await ctx.new_page()
        
        print(f"📡 Navigating to {URL}...")
        await page.goto(URL, wait_until="load")
        await page.wait_for_timeout(500)
        
        # Force SVG images for better quality
        try:
            await page.locator("input#svg").check()
        except:
            pass
        
        # Locate the main sagittal section image
        sammy = page.locator("#Sammy")
        await sammy.wait_for(state="visible", timeout=5000)
        
        # === CAPTURE CONSONANTS ===
        print(f"\n📝 Capturing {len(CONSONANTS)} English CONSONANTS...")
        for symbol, config in CONSONANTS.items():
            output_path = CONSONANTS_DIR / f"{symbol}.gif"
            await capture_phoneme(page, sammy, symbol, config, output_path)
        
        # === CAPTURE VOWELS ===
        print(f"\n🎵 Capturing {len(VOWELS)} English VOWELS...")
        for symbol, config in VOWELS.items():
            output_path = VOWELS_DIR / f"{symbol}.gif"
            await capture_phoneme(page, sammy, symbol, config, output_path)
        
        await ctx.close()
        await browser.close()
        
        print(f"\n✅ Done! Generated {len(CONSONANTS)} consonants and {len(VOWELS)} vowels")
        print(f"📁 Consonants: {CONSONANTS_DIR.absolute()}")
        print(f"📁 Vowels: {VOWELS_DIR.absolute()}")


if __name__ == "__main__":
    asyncio.run(run())
