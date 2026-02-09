# System Architecture Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      INPUT LAYER                                     │
│                                                                      │
│  ┌──────────────┐         ┌──────────────┐                          │
│  │  PDF Files   │         │  TXT Files   │                          │
│  │  (ACORD)     │         │  (Plain Text)│                          │
│  └──────┬───────┘         └──────┬───────┘                          │
│         │                        │                                  │
│         └───────────┬────────────┘                                  │
└─────────────────────┼──────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   TEXT EXTRACTION LAYER                              │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  PDF Processing:                                             │   │
│  │  • pdfplumber (primary)                                      │   │
│  │  • PyPDF2 (fallback)                                         │   │
│  │  • pymupdf/fitz (fallback)                                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Output: Raw text string                                            │
└─────────────────────┼──────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  EXTRACTION ENGINE                                   │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  Policy Information Extractor                              │     │
│  │  • Policy Number (multiple patterns)                       │     │
│  │  • Policyholder Name                                       │     │
│  │  • Effective Dates                                         │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  Incident Information Extractor                            │     │
│  │  • Date of Loss (MM/DD/YYYY, variations)                   │     │
│  │  • Time (12/24 hour formats)                               │     │
│  │  • Location (Street, City, State, ZIP)                     │     │
│  │  • Description (multi-line capture)                        │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  Parties Extractor                                         │     │
│  │  • Driver Name/Address                                     │     │
│  │  • Owner Information                                       │     │
│  │  • Contact Details (Phone, Email)                          │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  Asset Details Extractor                                   │     │
│  │  • Asset Type Detection (Vehicle/Property)                 │     │
│  │  • VIN (17-char validation)                                │     │
│  │  • Vehicle Make/Model/Year                                 │     │
│  │  • Damage Estimate ($)                                     │     │
│  │  • Damage Description                                      │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  Output: Dictionary of extracted fields                             │
└─────────────────────┼──────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  CLASSIFICATION LAYER                                │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  Claim Type Classifier                                     │     │
│  │                                                             │     │
│  │  Priority Order:                                           │     │
│  │  1. Check injury keywords → injury                         │     │
│  │  2. Check asset type = property → property_damage          │     │
│  │  3. Check vehicle + collision → vehicle_collision          │     │
│  │  4. Check vehicle only → vehicle_damage                    │     │
│  │  5. Default → general                                      │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  Output: claim_type classification                                  │
└─────────────────────┼──────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    VALIDATION LAYER                                  │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  Mandatory Field Checker                                   │     │
│  │                                                             │     │
│  │  Required Fields:                                          │     │
│  │  • policy_number                                           │     │
│  │  • policyholder_name                                       │     │
│  │  • incident_date                                           │     │
│  │  • incident_location                                       │     │
│  │  • claim_type                                              │     │
│  │  • asset_type                                              │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  Output: List of missing fields                                     │
└─────────────────────┼──────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  ROUTING DECISION ENGINE                             │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  Rule 1: Missing Mandatory Fields?                         │     │
│  │  YES → Manual Review                                       │     │
│  │  NO  → Continue to Rule 2                                  │     │
│  └────────────────┬───────────────────────────────────────────┘     │
│                   │                                                  │
│  ┌────────────────▼───────────────────────────────────────────┐     │
│  │  Rule 2: Fraud Indicators Detected?                        │     │
│  │  • Keywords: fraud, inconsistent, staged, etc.             │     │
│  │  YES → Investigation Queue                                 │     │
│  │  NO  → Continue to Rule 3                                  │     │
│  └────────────────┬───────────────────────────────────────────┘     │
│                   │                                                  │
│  ┌────────────────▼───────────────────────────────────────────┐     │
│  │  Rule 3: Injury Claim?                                     │     │
│  │  claim_type == 'injury'                                    │     │
│  │  YES → Specialist Queue                                    │     │
│  │  NO  → Continue to Rule 4                                  │     │
│  └────────────────┬───────────────────────────────────────────┘     │
│                   │                                                  │
│  ┌────────────────▼───────────────────────────────────────────┐     │
│  │  Rule 4: Damage Amount Check                               │     │
│  │  estimated_damage < $25,000                                │     │
│  │  YES → Fast-Track                                          │     │
│  │  NO  → Standard Processing                                 │     │
│  │  MISSING → Manual Review                                   │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  Output: Route + Reasoning                                          │
└─────────────────────┼──────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      OUTPUT LAYER                                    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │  JSON Generator                                            │     │
│  │                                                             │     │
│  │  {                                                         │     │
│  │    "extractedFields": { ... },                            │     │
│  │    "missingFields": [ ... ],                              │     │
│  │    "recommendedRoute": "...",                             │     │
│  │    "reasoning": "...",                                    │     │
│  │    "processingTimestamp": "...",                          │     │
│  │    "sourceFile": "..."                                    │     │
│  │  }                                                         │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  Outputs:                                                            │
│  • Console display (formatted)                                      │
│  • JSON file (*_processed.json)                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Routing Decision Tree

```
                         ┌───────────────┐
                         │ Start Process │
                         └───────┬───────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │ Missing Mandatory      │
                    │ Fields?                │
                    └────────┬───────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                   YES               NO
                    │                 │
                    ▼                 ▼
            ┌──────────────┐  ┌──────────────────┐
            │   MANUAL     │  │ Fraud Indicators?│
            │   REVIEW     │  └─────┬────────────┘
            └──────────────┘        │
                               ┌────┴─────┐
                               │          │
                              YES        NO
                               │          │
                               ▼          ▼
                      ┌────────────┐  ┌─────────────┐
                      │INVESTIGATION│  │ Injury Claim?│
                      │   QUEUE    │  └─────┬────────┘
                      └────────────┘        │
                                       ┌────┴─────┐
                                       │          │
                                      YES        NO
                                       │          │
                                       ▼          ▼
                              ┌────────────┐  ┌──────────────┐
                              │ SPECIALIST │  │ Damage Check │
                              │   QUEUE    │  └──────┬───────┘
                              └────────────┘         │
                                              ┌──────┴───────┐
                                              │              │
                                         < $25,000      ≥ $25,000
                                              │              │
                                              ▼              ▼
                                      ┌──────────┐  ┌──────────────┐
                                      │FAST-TRACK│  │   STANDARD   │
                                      └──────────┘  │  PROCESSING  │
                                                    └──────────────┘
```

## Data Flow Example

```
Input Document (ACORD Form)
    │
    ├─> Extract Text
    │   └─> "POLICY NUMBER: POL-2024-ABC123..."
    │
    ├─> Extract Fields
    │   ├─> policy_number: "POL-2024-ABC123"
    │   ├─> policyholder_name: "John Doe"
    │   ├─> incident_date: "01/25/2024"
    │   ├─> estimated_damage: 18500.0
    │   └─> ...
    │
    ├─> Validate
    │   └─> All mandatory fields present ✓
    │
    ├─> Check Fraud
    │   └─> No indicators found ✓
    │
    ├─> Classify
    │   └─> claim_type: "injury" (airbag deployed)
    │
    ├─> Route Decision
    │   └─> Specialist Queue (injury detected)
    │
    └─> Output JSON
        {
          "extractedFields": {...},
          "missingFields": [],
          "recommendedRoute": "Specialist Queue",
          "reasoning": "Claim involves injury..."
        }
```

## Component Interaction

```
┌─────────────────┐
│   User Input    │
│   (PDF/TXT)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  ClaimsProcessor            │
│  ┌─────────────────────┐    │
│  │ process_claim()     │────┼──> Main Entry Point
│  └──────────┬──────────┘    │
│             │               │
│             ├──> extract_text_from_file()
│             │
│             ├──> extract_policy_info()
│             │
│             ├──> extract_incident_info()
│             │
│             ├──> extract_involved_parties()
│             │
│             ├──> extract_asset_details()
│             │
│             ├──> determine_claim_type()
│             │
│             ├──> check_fraud_indicators()
│             │
│             └──> determine_route()
│                       │
└───────────────────────┼─────┘
                        │
                        ▼
                ┌──────────────┐
                │ JSON Output  │
                └──────────────┘
```

---

## Pattern Matching Strategy

```
For Each Field:
    │
    ├─> Define Multiple Patterns
    │   Example: Policy Number
    │   • Pattern 1: POLICY NUMBER: XXX
    │   • Pattern 2: Policy #: XXX
    │   • Pattern 3: POL NO: XXX
    │
    ├─> Try Patterns Sequentially
    │   for pattern in patterns:
    │       match = regex.search(pattern, text)
    │       if match:
    │           return match
    │
    └─> First Match Wins
        • Robust against format variations
        • Graceful degradation
        • No false negatives
```

---

**File:** ARCHITECTURE.md  
**Purpose:** Visual documentation of system design  
**Last Updated:** February 7, 2026
