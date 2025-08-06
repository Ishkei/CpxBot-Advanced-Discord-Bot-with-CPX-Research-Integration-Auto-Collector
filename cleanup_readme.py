#!/usr/bin/env python3
"""
Clean up README.md by removing non-existent features
"""

def cleanup_readme():
    """Remove gaming commands and tip.cc sections from README.md"""
    
    with open("README.md", "r") as f:
        content = f.read()
    
    # Remove gaming commands section
    lines = content.split('\n')
    cleaned_lines = []
    skip_section = False
    
    for line in lines:
        # Skip gaming commands section
        if "### Gaming Commands" in line:
            skip_section = True
            continue
        elif skip_section and line.startswith("##"):
            skip_section = False
        
        if not skip_section:
            cleaned_lines.append(line)
    
    # Remove tip.cc commands section
    lines = cleaned_lines
    cleaned_lines = []
    skip_section = False
    
    for line in lines:
        # Skip tip.cc commands section
        if "### Tip.cc Commands" in line:
            skip_section = True
            continue
        elif skip_section and line.startswith("##"):
            skip_section = False
        
        if not skip_section:
            cleaned_lines.append(line)
    
    # Write cleaned content
    with open("README.md", "w") as f:
        f.write('\n'.join(cleaned_lines))
    
    print("✅ README.md cleaned successfully!")

if __name__ == "__main__":
    cleanup_readme() 