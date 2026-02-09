# Autonomous Insurance Claims Processing Agent

A lightweight Python agent that automatically processes FNOL (First Notice of Loss) documents by extracting key information, validating fields, and intelligently routing claims to appropriate workflows.

##  Features

- **PDF Text Extraction**: Extracts structured data from insurance claim PDFs
- **Smart Field Detection**: Uses regex patterns to identify and extract key claim information
- **Validation**: Checks for missing or incomplete mandatory fields
- **Intelligent Routing**: Routes claims based on business rules:
  - Fast-track for low-damage claims (< $25,000)
  - Manual review for missing fields
  - Investigation queue for potential fraud
  - Specialist queue for injury claims
- **JSON Output**: Structured output format for easy integration

##  Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

##  Installation

### Step 1: Clone or Download the Repository

```bash
git clone <https://github.com/AdnanSameer1724/insurance-claims-agent>
cd insurance-claims-agent
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

##  Usage

### Basic Usage

Process a single FNOL PDF document:

```bash
python claims_processor.py path/to/fnol_document.pdf
```

This will:
1. Extract all relevant fields from the PDF
2. Identify missing mandatory fields
3. Determine the appropriate routing
4. Output results as JSON to console
5. Save results to `<filename>_processed.json`

### Running the Test

Test with the sample ACORD document:

```bash
python test_processor.py
```

### Example Output

```json
{
  "extractedFields": {
    "policy_number": "ABC123456",
    "policyholder_name": "John Doe",
    "incident_date": "01/15/2024",
    "incident_time": "2:30 PM",
    "incident_location": "123 Main Street",
    "city_state_zip": "Springfield, IL 62701",
    "incident_description": "Vehicle collision at intersection",
    "asset_type": "Vehicle",
    "vin": "1HGBH41JXMN109186",
    "vehicle_make": "Honda",
    "vehicle_model": "Civic",
    "vehicle_year": "2020",
    "estimated_damage": 15000.0,
    "claim_type": "vehicle_collision"
  },
  "missingFields": [],
  "recommendedRoute": "Fast-Track",
  "reasoning": "Estimated damage ($15,000.00) is below fast-track threshold ($25,000)",
  "processingTimestamp": "2024-02-07T10:30:00.123456"
}
```

##  How It Works

### 1. Field Extraction

The agent extracts the following categories of information:

**Policy Information:**
- Policy Number
- Policyholder Name
- Effective Dates

**Incident Information:**
- Date and Time
- Location
- Description

**Involved Parties:**
- Claimant Name
- Driver Information
- Contact Details (phone, email)

**Asset Details:**
- Asset Type (Vehicle/Property)
- Asset ID (VIN for vehicles)
- Estimated Damage
- Damage Description

**Claim Classification:**
- Claim Type (injury, vehicle_collision, property_damage, etc.)

### 2. Validation

The agent checks for these mandatory fields:
- policy_number
- policyholder_name
- incident_date
- incident_location
- claim_type
- asset_type

### 3. Routing Logic

The agent applies these rules in order:

1. **Missing Fields** → Manual Review
   - Any mandatory field is missing

2. **Fraud Detection** → Investigation Queue
   - Description contains keywords: "fraud", "inconsistent", "staged", "suspicious"

3. **Injury Claims** → Specialist Queue
   - Claim type is "injury"

4. **Damage Amount** → Fast-Track or Standard
   - Estimated damage < $25,000 → Fast-Track
   - Estimated damage ≥ $25,000 → Standard Processing

##  Project Structure

```
insurance-claims-agent/
├── claims_processor.py      # Main agent implementation
├── test_processor.py        # Test script for sample documents
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

##  Testing

### Test with Sample Document

The repository includes a test script that processes the sample ACORD Automobile Loss Notice:

```bash
python test_processor.py
```

### Create Your Own Test Cases

To test with additional FNOL documents:

```bash
python claims_processor.py path/to/your/fnol.pdf
```

##  Routing Examples

### Example 1: Fast-Track
```
Estimated damage: $12,000
Route: Fast-Track
Reason: Below $25,000 threshold
```

### Example 2: Investigation Queue
```
Description: "This seems like a staged accident..."
Route: Investigation Queue
Reason: Potential fraud indicators detected
```

### Example 3: Specialist Queue
```
Claim type: injury
Route: Specialist Queue
Reason: Involves injury requiring specialist review
```

### Example 4: Manual Review
```
Missing fields: policy_number, incident_date
Route: Manual Review
Reason: Missing mandatory fields
```

##  Key Implementation Details

### Pattern Matching
The agent uses regex patterns to extract fields from unstructured text. Multiple patterns are used for each field to handle variations in document formats.

### Fraud Detection
Simple keyword-based detection looking for suspicious terms in the incident description.

### Extensibility
The code is structured to make it easy to:
- Add new field extraction patterns
- Modify routing rules
- Add new claim types
- Integrate with external systems

##  Customization

### Modify Routing Threshold

Edit `claims_processor.py`:

```python
FAST_TRACK_THRESHOLD = 30000 
```

### Add Fraud Keywords

Edit `claims_processor.py`:

```python
FRAUD_KEYWORDS = ['fraud', 'inconsistent', 'staged', 'your_keyword']
```

### Add Mandatory Fields

Edit `claims_processor.py`:

```python
MANDATORY_FIELDS = [
    'policy_number',
    'policyholder_name',
    # Add your fields here
]
```

## 🚧 Limitations & Future Enhancements

### Current Limitations
- Relies on regex patterns (may miss variations)
- Basic fraud detection (keyword-based)
- Limited to English language documents
- Assumes standard ACORD or similar formats

### Potential Enhancements
- AI-powered extraction using LLMs (Anthropic Claude API)
- Machine learning-based fraud detection
- Multi-language support
- Image/photo analysis for damage assessment
- Integration with insurance management systems
- Batch processing capabilities
- Web interface for easier use
- OCR for scanned documents

##  Notes

- The agent is designed to be lightweight and fast
- All processing is done locally (no external API calls in base version)
- Output is in JSON format for easy integration with other systems
- The code includes extensive comments for educational purposes

##  Contributing

This is an assessment project, but suggestions for improvements are welcome!

##  License

This project was created as part of a technical assessment for Synapx.

##  Author

**Adnan**
- Assessment for Junior Software Developer role at Synapx
- Submission Date: February 9, 2026

---

**Assessment Details:**
- Assessment 1: Autonomous Insurance Claims Processing Agent
- Company: Synapx
- Position: Junior Software Developer
- Contact: bhoomi.dasa@synapx.com
