# CPX Research Survey Automation

This project provides specialized Firefox automation for completing surveys on the CPX Research platform. The system can automatically navigate to CPX Research surveys, answer questions, and complete surveys with minimal human intervention.

## Features

- **CPX Research Integration**: Direct integration with CPX Research survey platform
- **Automatic Question Detection**: Detects and answers various question types
- **Smart Answer Selection**: Random but realistic answer selection
- **Screenshot Capture**: Takes screenshots of each survey page
- **Progress Tracking**: Monitors survey completion progress
- **Error Handling**: Robust error handling and recovery
- **Interactive Mode**: Manual browser control option

## Quick Start

### 1. Run the CPX Automation Demo

```bash
# Activate virtual environment
source venv/bin/activate

# Run the demo
python3 demo_cpx_automation.py
```

### 2. Run Full CPX Automation

```bash
# Activate virtual environment
source venv/bin/activate

# Run the main CPX automation
python3 cpx_survey_automation.py
```

### 3. Interactive Mode

```bash
# Activate virtual environment
source venv/bin/activate

# Run interactive mode
python3 demo_cpx_automation.py
# Choose option 2 (Interactive Mode)
```

## CPX Research URL Structure

The CPX Research URL format is:
```
https://offers.cpx-research.com/index.php?app_id={APP_ID}&ext_user_id={USER_ID}
```

From your URL: `https://offers.cpx-research.com/index.php?app_id=27260&ext_user_id=533055960609193994`

- **App ID**: `27260`
- **User ID**: `533055960609193994`

## How It Works

### 1. Survey Navigation

The automation navigates to your CPX Research survey URL and waits for the page to load.

### 2. Question Detection

The system automatically detects different types of survey questions:

- **Radio Buttons**: Multiple choice questions
- **Checkboxes**: Multi-select questions
- **Text Fields**: Open-ended questions
- **Dropdowns**: Selection questions
- **Textareas**: Long-form responses

### 3. Smart Answering

For each question type, the automation provides realistic answers:

- **Radio Buttons**: Randomly selects an option
- **Checkboxes**: Randomly selects 1-2 options
- **Text Fields**: Uses predefined realistic responses
- **Dropdowns**: Selects random options (skips "Please select")
- **Textareas**: Provides thoughtful, varied responses

### 4. Progress Tracking

The system:
- Takes screenshots of each page
- Monitors URL changes for completion
- Handles page transitions
- Provides detailed logging

## Question Types Handled

### Radio Button Questions
```python
# Automatically detects and answers radio button questions
cpx_automation.answer_radio_question(answer_index=0)
```

### Checkbox Questions
```python
# Automatically detects and answers checkbox questions
cpx_automation.answer_checkbox_question(checkbox_index=0)
```

### Text Field Questions
```python
# Fills text fields with realistic responses
cpx_automation.fill_text_field("input[name='feedback']", "Great survey!")
```

### Dropdown Questions
```python
# Selects options from dropdown menus
cpx_automation.select_dropdown_option("select[name='age']", "25-34")
```

## Sample Responses

The automation uses these realistic responses for text fields:

- "This is a great survey!"
- "I find this product interesting."
- "The quality is excellent."
- "I would recommend this to others."
- "Very satisfied with the experience."

## Configuration

### Update CPX Credentials

Edit the credentials in `cpx_survey_automation.py`:

```python
class CPXSurveyAutomation:
    def __init__(self, headless: bool = False):
        self.browser = FirefoxAutomation(headless=headless)
        self.cpx_url = "https://offers.cpx-research.com/index.php"
        self.user_id = "533055960609193994"  # Your CPX User ID
        self.app_id = "27260"  # Your CPX App ID
```

### Customize Answer Selection

Modify the answer selection logic in `handle_survey_page()`:

```python
# For radio buttons - select specific answer
if not self.answer_radio_question(answer_index=1):  # Select second option
    success = False

# For checkboxes - select specific checkbox
if not self.answer_checkbox_question(checkbox_index=0):  # Select first checkbox
    success = False
```

## Usage Examples

### Example 1: Basic CPX Automation

```python
from cpx_survey_automation import CPXSurveyAutomation

with CPXSurveyAutomation(headless=False) as cpx_automation:
    # Update credentials
    cpx_automation.user_id = "533055960609193994"
    cpx_automation.app_id = "27260"
    
    # Complete the survey
    success = cpx_automation.complete_cpx_survey(max_pages=10)
    
    if success:
        print("Survey completed successfully!")
    else:
        print("Survey automation failed")
```

### Example 2: Interactive Mode

```python
from cpx_survey_automation import CPXSurveyAutomation

with CPXSurveyAutomation(headless=False) as cpx_automation:
    # Navigate to CPX Research
    if cpx_automation.navigate_to_cpx():
        print("Browser opened with CPX Research")
        print("You can now manually interact with the survey")
        
        # Keep browser open for manual interaction
        input("Press Enter to close browser...")
```

### Example 3: Custom Survey Handling

```python
from cpx_survey_automation import CPXSurveyAutomation

with CPXSurveyAutomation(headless=False) as cpx_automation:
    # Navigate to CPX Research
    cpx_automation.navigate_to_cpx()
    
    # Wait for questions to load
    if cpx_automation.wait_for_survey_questions():
        # Answer specific question types
        cpx_automation.answer_radio_question(answer_index=0)
        cpx_automation.answer_checkbox_question(checkbox_index=1)
        cpx_automation.fill_text_field("textarea", "Custom response")
        
        # Click next button
        cpx_automation.click_next_button()
```

## Screenshots

The automation takes screenshots at each step:

- `cpx_survey_page_1.png` - First survey page
- `cpx_survey_page_2.png` - Second survey page
- `...`
- `cpx_survey_complete.png` - Final completion page

## Troubleshooting

### Common Issues

1. **Firefox not found**
   ```bash
   sudo apt install firefox-esr
   ```

2. **CPX credentials invalid**
   - Verify your User ID and App ID
   - Check that the CPX Research URL is accessible

3. **Survey questions not detected**
   - The survey might be using custom elements
   - Try interactive mode for manual control

4. **CAPTCHA detected**
   - Manual intervention may be required
   - The system will wait for manual CAPTCHA solving

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## File Structure

```
CpxBot/
├── cpx_survey_automation.py      # Main CPX automation script
├── demo_cpx_automation.py        # Demo and interactive mode
├── src/web_automation/
│   ├── firefox_automation.py     # Core Firefox automation
│   └── survey_automator.py       # Advanced survey automation
└── README_CPX_AUTOMATION.md     # This file
```

## Security and Ethics

### Important Considerations

- **Terms of Service**: Ensure automation complies with CPX Research terms
- **Rate Limiting**: Respect survey platform rate limits
- **Data Privacy**: Handle personal data responsibly
- **CAPTCHA**: Some surveys may require manual intervention

### Best Practices

1. **Use Responsibly**: Don't abuse the automation
2. **Monitor Activity**: Check screenshots and logs
3. **Respect Limits**: Don't overwhelm survey platforms
4. **Manual Review**: Verify survey completion

## Advanced Features

### Custom Answer Strategies

You can customize answer selection:

```python
def custom_answer_strategy(self):
    """Custom answer selection logic."""
    # Always select the first option for radio buttons
    self.answer_radio_question(answer_index=0)
    
    # Always select the second checkbox
    self.answer_checkbox_question(checkbox_index=1)
    
    # Use specific text responses
    self.fill_text_field("textarea", "Custom response text")
```

### Survey Completion Detection

The system detects survey completion by:

```python
# Check URL for completion indicators
current_url = self.browser.get_current_url()
if "complete" in current_url.lower() or "thank" in current_url.lower():
    logger.info("Survey appears to be complete")
    break
```

## Contributing

To extend the CPX automation:

1. **Add new question types** in `CPXSurveyAutomation`
2. **Customize answer strategies** for specific surveys
3. **Implement CAPTCHA solving** for automated handling
4. **Add survey platform-specific features**

## License

This project is part of the CpxBot survey automation system. 