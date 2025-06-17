# AAMC_Analyzer
Automated extraction tool for MCAT practice questions using Selenium WebDriver with arrow key navigation.
Condenses your AAMC FL practice test review page to a json

## Prerequisites

- Python 3.7+
- Firefox browser
- GeckoDriver executable

## Installation

```bash
pip install selenium
```

Download [GeckoDriver](https://github.com/mozilla/geckodriver/releases) and place `geckodriver.exe` in project directory. (I left it in there, hopefully thats fine)

## Usage

### 1. Launch Script
```bash
python scrape_aamc_mcat.py
```

### 2. Browser Navigation
- Navigate to first question in browser
- Return to terminal, press Enter
- **Critical**: Immediately click browser window to establish focus
- Scraper begins automated navigation via arrow keys

### 3. Focus Management
Browser window must maintain focus for arrow key navigation. Terminal interaction breaks focus and halts navigation.

## Output Structure

```json
{
  "question_number": 1,
  "passage": "Reading passage content...",
  "question_text": "Question stem...",
  "answer_choices": "A. Option 1\nB. Option 2\nC. Option 3\nD. Option 4",
  "correct_answer": "B",
  "your_answer": "B",
  "explanation": "Solution explanation...",
  "result": "Correct/Incorrect",
  "content_skills": "Skill tags"
}
```

## File Outputs

- `mcat_complete.json`: Final dataset
- `mcat_partial_N.json`: Progress checkpoints (every 10 questions)

## Architecture

### Navigation Strategy
- Arrow key dispatch to DOM body element
- Window focus validation via `switch_to.window()`
- Robust page transition detection

### Error Handling
- Manual navigation fallback on automation failure
- Graceful degradation with user prompts
- Progress preservation through periodic saves

## Troubleshooting

### Navigation Failures
- Verify browser focus before execution
- Check GeckoDriver path and permissions
- Ensure site structure matches XPath selectors

### Focus Issues
- Click browser window immediately after terminal prompt
- Avoid terminal interaction during scraping
- Restart if focus is lost mid-process

### Partial Recovery
Resume from checkpoint files:
```python
# Load partial results
with open('mcat_partial_100.json', 'r') as f:
    existing_data = json.load(f)
```

## Technical Details

**Selenium Configuration**: Firefox with automation detection disabled
**Wait Strategy**: Dynamic polling with 0.5s intervals
**Element Location**: XPath selectors targeting class-based DOM structure
**Navigation Protocol**: Right arrow key simulation with focus management

## Limitations

- Requires manual browser positioning
- Site-specific XPath selectors
- Focus-dependent navigation mechanism