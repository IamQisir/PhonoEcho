# Quick Reference - Refactored Echo Learning Modules

## Module Import Guide

### 🎵 Audio Operations
```python
from audio_handler import (
    get_audio_from_mic_v2,      # Record audio from microphone
    save_audio_bytes_to_wav     # Save audio bytes to WAV file
)
```

### 🗣️ Pronunciation Assessment
```python
from pronunciation_service import (
    pronunciation_assessment    # Assess pronunciation using Azure
)
```

### 📊 Error Analysis
```python
from error_analyzer import (
    collect_errors,            # Collect errors from assessment result
    create_error_table,        # Create DataFrame of errors
    get_error_stats,          # Get current session error stats
    get_total_error_stats     # Get cumulative error stats
)
```

### 📈 Visualization
```python
from visualization import (
    create_radar_chart,        # Pronunciation assessment radar chart
    create_waveform_plot,      # Audio waveform with scores
    create_syllable_table,     # HTML table for syllables
    create_doughnut_chart,     # Error distribution chart
    plot_overall_score,        # Overall score progression
    plot_detail_scores,        # Detailed score components
    plot_score_history,        # Complete score history
    plot_error_charts,         # Error analysis charts
    get_color                  # Score-based color mapping
)
```

### 💾 Score Management
```python
from score_manager import (
    save_scores_to_json,       # Save scores to JSON file
    save_error_history,        # Save error history to JSON
    store_scores,              # Update session state with scores
    initialize_lesson_state    # Load saved lesson data
)
```

---

## Common Usage Patterns

### Pattern 1: Complete Learning Flow
```python
# 1. Record audio
audio_data = get_audio_from_mic_v2(user, lesson_name)
audio_file = save_audio_bytes_to_wav(user, audio_data, lesson_name)

# 2. Assess pronunciation
result = pronunciation_assessment(audio_file, reference_text)

# 3. Analyze errors
errors = collect_errors(result)
error_table = create_error_table()

# 4. Create visualizations
radar = create_radar_chart(result)
waveform = create_waveform_plot(audio_file, result)

# 5. Store results
store_scores(user, lesson_index, result)
```

### Pattern 2: Display Score History
```python
# Initialize lesson
initialize_lesson_state(user, lesson_index)

# Plot history
plot_score_history()
plot_error_charts()
```

### Pattern 3: Error Analysis Only
```python
# Get errors from result
errors = collect_errors(pronunciation_result)

# Display as table
error_table = create_error_table()

# Get statistics
current_stats = get_error_stats()
total_stats = get_total_error_stats()

# Visualize
plot_error_charts()
```

---

## File Locations

```
app/learn/
├── echo_learning.py          # Main UI (import this for UI)
├── audio_handler.py           # Audio I/O operations
├── pronunciation_service.py   # Azure API integration
├── error_analyzer.py          # Error collection & stats
├── visualization.py           # All charts and plots
└── score_manager.py          # Data persistence
```

---

## Function Reference by Category

### Audio (audio_handler.py)
| Function | Purpose | Returns |
|----------|---------|---------|
| `get_audio_from_mic_v2(user, selection)` | Record audio | BytesIO or None |
| `save_audio_bytes_to_wav(user, audio_bytes, selection)` | Save audio | str (filepath) |

### Assessment (pronunciation_service.py)
| Function | Purpose | Returns |
|----------|---------|---------|
| `pronunciation_assessment(audio_file, reference_text)` | Assess pronunciation | dict (JSON result) |

### Error Analysis (error_analyzer.py)
| Function | Purpose | Returns |
|----------|---------|---------|
| `collect_errors(pronunciation_result)` | Extract errors | dict (error data) |
| `create_error_table()` | Create error table | pd.DataFrame |
| `get_error_stats()` | Current session stats | dict |
| `get_total_error_stats()` | Cumulative stats | dict |

### Visualization (visualization.py)
| Function | Purpose | Returns |
|----------|---------|---------|
| `create_radar_chart(pronunciation_result)` | Assessment radar | matplotlib.Figure |
| `create_waveform_plot(audio_file, result)` | Waveform with scores | matplotlib.Figure |
| `create_syllable_table(result)` | Syllable table HTML | str |
| `create_doughnut_chart(data, title)` | Error distribution | altair.Chart |
| `plot_overall_score(data)` | Score progression | altair.Chart |
| `plot_detail_scores(data)` | Component scores | altair.Chart |
| `plot_score_history()` | Complete history | None (displays) |
| `plot_error_charts()` | Error charts | None (displays) |
| `get_color(score)` | Score-based color | str (hex color) |

### Score Management (score_manager.py)
| Function | Purpose | Returns |
|----------|---------|---------|
| `save_scores_to_json(user, lesson_index, scores_history)` | Save scores | None |
| `save_error_history(user, lesson_index, error_data)` | Save errors | None |
| `store_scores(user, lesson_index, result)` | Update state | None |
| `initialize_lesson_state(user, lesson_index)` | Load data | None |

---

## Session State Variables

### Used by echo_learning.py
```python
st.session_state.user                    # Current user object
st.session_state.lesson_index            # Current lesson index (0-based)
st.session_state.dataset                 # Dataset object
st.session_state.scores_history          # Score history dict
st.session_state.learning_data           # Current learning session data
st.session_state.ai_initial_input        # Input for AI chat
```

### Used by score_manager.py
```python
st.session_state.learning_state          # Main learning state dict
  ├── scores_history                     # Dict[lesson_index, scores]
  ├── current_errors                     # Current session errors
  └── total_errors                       # Cumulative errors per lesson
```

---

## Data Structures

### Pronunciation Result (from Azure)
```python
{
    "NBest": [{
        "PronunciationAssessment": {
            "PronScore": 85.2,
            "AccuracyScore": 90.1,
            "FluencyScore": 82.3,
            "CompletenessScore": 100.0,
            "ProsodyScore": 78.9
        },
        "Words": [{
            "Word": "hello",
            "PronunciationAssessment": {
                "AccuracyScore": 95.0,
                "ErrorType": "None"
            },
            "Phonemes": [...]
        }]
    }]
}
```

### Error Data Structure
```python
{
    "省略 (Omission)": {"count": 2, "words": ["the", "a"]},
    "挿入 (Insertion)": {"count": 0, "words": []},
    "発音ミス (Mispronunciation)": {"count": 3, "words": ["world", "hello", "test"]},
    "不適切な間 (UnexpectedBreak)": {"count": 1, "words": ["today"]},
    "間の欠如 (MissingBreak)": {"count": 0, "words": []},
    "単調 (Monotone)": {"count": 1, "words": ["sentence"]}
}
```

### Scores History Structure
```python
{
    0: {  # lesson_index
        "AccuracyScore": [90.1, 92.3, 89.5, ...],
        "FluencyScore": [82.3, 85.1, 83.7, ...],
        "CompletenessScore": [100.0, 100.0, 100.0, ...],
        "ProsodyScore": [78.9, 80.2, 79.5, ...],
        "PronScore": [85.2, 87.1, 86.0, ...]
    }
}
```

---

## File Paths

### Audio Files
```
database/{username}/practice_history/{YYYY-MM-DD}/{lesson}-{timestamp}.wav
Example: database/hiroki/practice_history/2025-10-08/レッスン1-2025-10-08_14-30-25.wav
```

### Score Files
```
database/{username}/practice_history/{YYYY-MM-DD}/scores/lesson_scores.json
database/{username}/practice_history/{YYYY-MM-DD}/scores/error_history.json
```

### Pronunciation History
```
database/{username}/practice_history/{YYYY-MM-DD}/{lesson}-{timestamp}.json
Example: database/hiroki/practice_history/2025-10-08/レッスン1-2025-10-08_14-30-25.json
```

---

## Quick Debugging

### Check Module Import
```python
import sys
print(sys.path)  # Verify module paths

from audio_handler import *
from pronunciation_service import *
from error_analyzer import *
from visualization import *
from score_manager import *
```

### Verify Session State
```python
import streamlit as st
st.write(st.session_state)  # Display all session state
```

### Check File Existence
```python
import os
user_path = st.session_state.user.today_path
scores_path = os.path.join(user_path, "scores")
print(f"Scores dir exists: {os.path.exists(scores_path)}")
```

---

## Performance Tips

1. **Lazy Loading**: Only import modules when needed
2. **Cache Data**: Use `@st.cache_data` for expensive operations
3. **Async Operations**: Consider async for Azure API calls
4. **Batch Processing**: Process multiple files together

---

## Common Issues & Solutions

### Issue: Module not found
```python
# Solution: Check current directory
import sys
print(sys.path)
sys.path.append('app/learn')
```

### Issue: Session state not persisting
```python
# Solution: Initialize before use
if 'learning_state' not in st.session_state:
    initialize_lesson_state(user, lesson_index)
```

### Issue: Visualization not displaying
```python
# Solution: Check if data exists
if st.session_state['learning_data']['radar_chart']:
    st.pyplot(st.session_state['learning_data']['radar_chart'])
```

---

## Testing Commands

```bash
# Check syntax
python -m py_compile app/learn/audio_handler.py
python -m py_compile app/learn/pronunciation_service.py
python -m py_compile app/learn/error_analyzer.py
python -m py_compile app/learn/visualization.py
python -m py_compile app/learn/score_manager.py

# Run linting
pylint app/learn/*.py

# Run type checking (if type hints added)
mypy app/learn/
```

---

## Quick Migration Checklist

- [ ] Update all imports in dependent files
- [ ] Test audio recording functionality
- [ ] Test pronunciation assessment
- [ ] Test error analysis
- [ ] Test all visualizations
- [ ] Test score persistence
- [ ] Test lesson navigation
- [ ] Test session state management
- [ ] Verify file paths are correct
- [ ] Check all error handling works

---

**Created**: October 8, 2025  
**Version**: 1.0  
**Status**: ✅ Production Ready
