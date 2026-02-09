# Quick Start Guide

## Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
# Optional: Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# OR
venv\Scripts\activate  # On Windows

# Install PDF support (if available)
pip install pdfplumber
```

### Step 2: Test the Agent

```bash
# Run the comprehensive test suite
python3 run_tests.py
```

Expected output: **4/4 tests passing** 

### Step 3: Process Your Own Claims

```bash
# Process a claim file
python3 claims_processor_simple.py <your_claim_file.pdf>

# Or use one of the samples
python3 claims_processor_simple.py sample_claim_fasttrack.txt
```

---

## Sample Commands

### Process Different Claim Types

```bash
# Fast-track claim (low damage)
python3 claims_processor_simple.py sample_claim_fasttrack.txt

# Fraud investigation (suspicious indicators)
python3 claims_processor_simple.py sample_claim_fraud.txt

# Specialist queue (injury)
python3 claims_processor_simple.py sample_claim.txt

# Manual review (missing fields)
python3 claims_processor_simple.py sample_claim_incomplete.txt
```

### View Results

```bash
# JSON output is saved automatically
cat sample_claim_processed.json

# Or view test summary
cat test_summary.json
```

---

## Understanding the Output

### JSON Structure

```json
{
  "extractedFields": {
    "policy_number": "POL-2024-ABC123",
    "policyholder_name": "John Doe",
    "incident_date": "01/25/2024",
    "estimated_damage": 18500.0,
    "claim_type": "vehicle_collision",
    ...
  },
  "missingFields": [],
  "recommendedRoute": "Fast-Track",
  "reasoning": "Estimated damage ($18,500.00) is below fast-track threshold ($25,000)"
}
```

### Routing Options

| Route | Trigger | Example |
|-------|---------|---------|
| **Manual Review** | Missing mandatory fields | No policy number |
| **Investigation Queue** | Fraud indicators | "inconsistent", "staged" |
| **Specialist Queue** | Injury claims | Medical treatment needed |
| **Fast-Track** | Damage < $25,000 | Minor fender bender |
| **Standard Processing** | Damage ≥ $25,000 | Major collision |

---

## Troubleshooting

### Issue: "No PDF library available"
**Solution:** Install pdfplumber:
```bash
pip install pdfplumber
```

### Issue: "File not found"
**Solution:** Check file path:
```bash
# Use full path
python3 claims_processor_simple.py /full/path/to/claim.pdf

# Or navigate to directory first
cd /path/to/claims
python3 /path/to/claims_processor_simple.py claim.pdf
```

### Issue: Module not found
**Solution:** Ensure you're in the project directory:
```bash
cd insurance-claims-agent
python3 claims_processor_simple.py sample_claim.txt
```

---

## What's Next?

1.  Review the README.md for full documentation
2.  Run the test suite to verify everything works
3.  Try processing your own FNOL documents
4.  Check DEMO_GUIDE.md for presentation tips
5.  Explore the code to understand the implementation

---

## Support

For questions about this assessment submission:
- **Candidate:** Adnan Sameer Z
- **Position:** Junior Software Developer
- **Company:** Synapx
- **Submission Date:** February 9, 2026

---

**Estimated setup time:** 5 minutes  
**Estimated test time:** 2 minutes  
**Total time to get started:** ~7 minutes 
