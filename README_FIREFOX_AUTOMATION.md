# Firefox Survey Automation

This project provides Firefox browser automation capabilities for completing surveys automatically. The system includes both basic automation and advanced survey handling with configuration-based automation.

## Features

- **Firefox Browser Automation**: Open Firefox and navigate to websites
- **Survey Form Filling**: Automatically fill text fields, dropdowns, and checkboxes
- **Multiple Choice Questions**: Handle radio buttons and multiple choice questions
- **Scale/Rating Questions**: Answer rating scales and satisfaction questions
- **Screenshot Capture**: Take screenshots for verification
- **CAPTCHA Detection**: Basic CAPTCHA detection and handling
- **Configuration-Based Automation**: Define surveys in JSON configuration files
- **Interactive Mode**: Manual browser control for complex surveys

## Prerequisites

### System Requirements

- **Firefox Browser**: Must be installed on your system
- **Python 3.8+**: Required for running the automation scripts
- **Linux/Windows/macOS**: Supported operating systems

### Python Dependencies

The required dependencies are already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `selenium>=4.15.0`: Web automation framework
- `webdriver-manager>=4.0.0`: Automatic webdriver management
- `loguru>=0.7.0`: Logging

## Installation

1. **Clone or download the project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Verify Firefox is installed** on your system
4. **Run the test script** to verify everything works:
   ```bash
   python test_firefox_automation.py
   ```

## Quick Start

### 1. Basic Automation

Run the main automation script:

```bash
python survey_automation.py
```

Choose from the available options:
- **Demo Survey Automation**: Basic demonstration
- **Advanced Survey Automation**: Use configuration files
- **Interactive Mode**: Manual browser control
- **Create Survey Configuration**: Build custom survey configs

### 2. Interactive Mode

For manual control of the browser:

```bash
python survey_automation.py
# Choose option 3 (Interactive Mode)
# Enter the survey URL when prompted
```

### 3. Test the System

Run the test script to verify everything works:

```bash
python test_firefox_automation.py
```

## Configuration

### Survey Configuration Files

Surveys can be defined in JSON configuration files. See `config/survey_config.json` for examples.

#### Basic Survey Configuration

```json
{
  "name": "Sample Survey",
  "url": "https://www.example-survey-site.com/survey",
  "login": {
    "username_field": "username",
    "password_field": "password",
    "username": "your_username",
    "password": "your_password",
    "submit_button": "login-button"
  },
  "questions": [
    {
      "type": "text",
      "selector": "name-field",
      "answer": "John Doe"
    },
    {
      "type": "multiple_choice",
      "selector": "gender-options",
      "answer_index": 0
    }
  ],
  "submit_button": "submit-survey"
}
```

#### Question Types

1. **Text Input** (`"type": "text"`)
   - Fills text fields, textareas
   - Requires: `selector`, `answer`

2. **Multiple Choice** (`"type": "multiple_choice"`)
   - Handles radio buttons, checkboxes
   - Requires: `selector`, `answer_index` (0-based)

3. **Scale/Rating** (`"type": "scale"`)
   - Handles rating scales (1-10, etc.)
   - Requires: `selector`, `rating`

4. **Dropdown** (`"type": "dropdown"`)
   - Selects options from dropdown menus
   - Requires: `selector`, `option`

## Usage Examples

### Example 1: Simple Survey Automation

```python
from src.web_automation.firefox_automation import FirefoxAutomation
from selenium.webdriver.common.by import By

with FirefoxAutomation(headless=False) as browser:
    # Navigate to survey
    browser.navigate_to_url("https://example-survey.com")
    
    # Fill form fields
    browser.fill_input(By.ID, "name", "John Doe")
    browser.fill_input(By.ID, "email", "john@example.com")
    
    # Select dropdown
    browser.select_option(By.ID, "age-range", "25-34")
    
    # Submit form
    browser.click_element(By.ID, "submit-button")
```

### Example 2: Advanced Survey Automation

```python
from src.web_automation.survey_automator import SurveyAutomator
import json

# Load survey configuration
with open("config/survey_config.json", "r") as f:
    config = json.load(f)

with SurveyAutomator(headless=False) as automator:
    for survey in config["surveys"]:
        automator.complete_survey(survey)
```

### Example 3: Custom Survey Configuration

```python
survey_config = {
    "name": "My Custom Survey",
    "url": "https://my-survey-site.com",
    "questions": [
        {
            "type": "text",
            "selector": "name",
            "answer": "John Doe"
        },
        {
            "type": "multiple_choice",
            "selector": "gender",
            "answer_index": 0
        }
    ],
    "submit_button": "submit"
}

with SurveyAutomator(headless=False) as automator:
    automator.complete_survey(survey_config)
```

## Selector Types

The automation supports multiple selector types:

- **ID**: `"id"` - Element ID (e.g., `"username"`)
- **Class**: `"class"` - CSS class (e.g., `"form-input"`)
- **Name**: `"name"` - Form field name (e.g., `"email"`)
- **XPath**: `"xpath"` - XPath expression
- **CSS**: `"css"` - CSS selector

## Advanced Features

### CAPTCHA Handling

The system includes basic CAPTCHA detection:

```python
# CAPTCHA detection is automatic
automator.handle_captcha()
```

### Screenshot Capture

Take screenshots for verification:

```python
browser.take_screenshot("survey_completion.png")
```

### Random Delays

Add human-like delays between actions:

```python
import time
import random

time.sleep(random.uniform(1, 3))  # Random delay between 1-3 seconds
```

## Troubleshooting

### Common Issues

1. **Firefox not found**
   - Ensure Firefox is installed on your system
   - Check that the Firefox executable is in your PATH

2. **WebDriver issues**
   - The system automatically downloads the correct GeckoDriver
   - If issues persist, manually install GeckoDriver

3. **Element not found**
   - Verify the selector is correct
   - Check if the element is in an iframe
   - Ensure the page has loaded completely

4. **CAPTCHA detection**
   - Manual intervention may be required
   - The system will wait 30 seconds for manual CAPTCHA solving

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

- **Credentials**: Store sensitive data securely
- **CAPTCHA**: Some surveys may require manual intervention
- **Rate Limiting**: Respect website terms of service
- **Legal Compliance**: Ensure automation complies with survey platform terms

## File Structure

```
CpxBot/
├── src/web_automation/
│   ├── __init__.py
│   ├── firefox_automation.py      # Core Firefox automation
│   └── survey_automator.py        # Advanced survey automation
├── config/
│   └── survey_config.json         # Sample survey configurations
├── survey_automation.py           # Main automation script
├── test_firefox_automation.py     # Test script
└── README_FIREFOX_AUTOMATION.md  # This file
```

## Contributing

To extend the automation capabilities:

1. **Add new question types** in `SurveyAutomator`
2. **Create custom selectors** for specific survey platforms
3. **Implement CAPTCHA solving** for automated handling
4. **Add survey platform-specific modules**

## License

This project is part of the CpxBot survey automation system. 