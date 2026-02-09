# Demo Video Script / Guide

## Insurance Claims Processing Agent - Technical Demonstration

### Introduction (30 seconds)
"Hello, I'm Adnan, and this is my submission for the Junior Software Developer position at Synapx. I've built an autonomous insurance claims processing agent that extracts, validates, and routes FNOL documents."

### Architecture Overview (1 minute)
"The agent is built in Python and follows a modular architecture:
1. **Text Extraction** - Supports both PDF and TXT formats
2. **Field Extraction** - Uses regex patterns to identify key information
3. **Validation** - Checks for mandatory fields
4. **Intelligent Routing** - Routes claims based on business rules

The routing logic follows a priority system:
- Missing fields → Manual Review
- Fraud indicators → Investigation Queue  
- Injury claims → Specialist Queue
- Low damage (< $25K) → Fast-Track
- High damage (≥ $25K) → Standard Processing"

### Live Demo (2-3 minutes)

#### Demo 1: Fast-Track Claim
```bash
python3 claims_processor_simple.py sample_claim_fasttrack.txt
```
"This claim has estimated damage of $3,200, well below our $25,000 threshold, so it's routed to Fast-Track for quick processing."

#### Demo 2: Fraud Investigation
```bash
python3 claims_processor_simple.py sample_claim_fraud.txt
```
"Notice how the description contains words like 'inconsistent' and 'staged' - the agent automatically flags this for investigation."

#### Demo 3: Injury/Specialist Queue
```bash
python3 claims_processor_simple.py sample_claim.txt
```
"This claim mentions injuries and deployed airbags, triggering automatic routing to the Specialist Queue for medical review."

#### Demo 4: Missing Fields
```bash
python3 claims_processor_simple.py sample_claim_incomplete.txt
```
"When mandatory fields are missing, the claim goes to Manual Review - you can see exactly which fields are missing in the output."

### Test Suite (1 minute)
```bash
python3 run_tests.py
```
"I've also built a comprehensive test suite that validates all routing scenarios. As you can see, all 4 test scenarios pass, demonstrating that the routing logic works correctly."

### Code Walkthrough (1-2 minutes)
"Let me briefly show you the code structure:

1. **ClaimsProcessor class** - Main processing engine
2. **extract_policy_info()** - Extracts policy details using multiple regex patterns
3. **extract_incident_info()** - Gets date, time, location, description
4. **extract_asset_details()** - Vehicle/property information
5. **determine_route()** - Applies business rules in priority order

The code is well-documented and follows Python best practices."

### Key Features (30 seconds)
"Key features include:
- ✓ Supports multiple document formats (PDF/TXT)
- ✓ Robust pattern matching with multiple fallbacks
- ✓ Clear JSON output for system integration
- ✓ Comprehensive test coverage
- ✓ Extensible design for adding new rules"

### Future Enhancements (30 seconds)
"Potential improvements include:
- AI-powered extraction using Claude API for more accuracy
- ML-based fraud detection
- OCR support for scanned documents
- Web dashboard for claim management
- Batch processing capabilities"

### Conclusion (15 seconds)
"Thank you for reviewing my submission. The code is well-documented, tested, and ready for review. I look forward to discussing this further with the Synapx team."

---

## Recording Tips

### Setup Before Recording:
1. Open terminal in project directory
2. Clear terminal: `clear`
3. Have all sample files ready
4. Test commands work before recording
5. Use larger font size for visibility

### Screen Recording Settings:
- Resolution: 1920x1080 minimum
- Frame rate: 30fps
- Include audio narration
- Show terminal window clearly
- Consider using a screen recorder like:
  - OBS Studio (Free, cross-platform)
  - QuickTime (Mac)
  - Windows Game Bar (Windows)

### Terminal Commands to Show:

```bash
# Show project structure
ls -la

# Show README
cat README.md | head -50

# Run individual tests
python3 claims_processor_simple.py sample_claim_fasttrack.txt
python3 claims_processor_simple.py sample_claim_fraud.txt

# Run test suite
python3 run_tests.py

# Show sample JSON output
cat sample_claim_processed.json
```

### What to Highlight:
1. Clean, professional code
2. Comprehensive documentation
3. All tests passing
4. Different routing scenarios
5. JSON output format
6. Easy to run and understand

---

Total suggested video length: 5-7 minutes
Keep it concise, clear, and professional!
