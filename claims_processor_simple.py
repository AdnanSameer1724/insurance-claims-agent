"""
Autonomous Insurance Claims Processing Agent (Simplified Version)
Works with pre-extracted text or PDF files
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class ClaimsProcessor:
    """Main claims processing agent"""
    
    # Routing thresholds
    FAST_TRACK_THRESHOLD = 25000
    
    # Mandatory fields for validation
    MANDATORY_FIELDS = [
        'policy_number',
        'policyholder_name',
        'incident_date',
        'incident_location',
        'claim_type',
        'asset_type'
    ]
    
    # Fraud detection keywords
    FRAUD_KEYWORDS = ['fraud', 'inconsistent', 'staged', 'suspicious', 'fake', 'false']
    
    # Injury-related keywords
    INJURY_KEYWORDS = ['injury', 'injured', 'hurt', 'medical', 'hospital', 'ambulance', 'emergency']
    
    def __init__(self):
        self.extracted_data = {}
        self.missing_fields = []
        
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from file (PDF or TXT)"""
        try:
            file_path = Path(file_path)
            
            # If it's a text file, just read it
            if file_path.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            # For PDF files, try different methods
            elif file_path.suffix.lower() == '.pdf':
                # Try pdfplumber first
                try:
                    import pdfplumber
                    text = ""
                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                    return text
                except ImportError:
                    pass
                
                # Try PyPDF2
                try:
                    import PyPDF2
                    text = ""
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page in pdf_reader.pages:
                            text += page.extract_text() + "\n"
                    return text
                except ImportError:
                    pass
                
                # Try pymupdf/fitz
                try:
                    import fitz
                    text = ""
                    doc = fitz.open(file_path)
                    for page in doc:
                        text += page.get_text() + "\n"
                    doc.close()
                    return text
                except ImportError:
                    pass
                
                raise Exception(
                    "No PDF library available. Please install pdfplumber, PyPDF2, or pymupdf.\n"
                    "Run: pip install pdfplumber"
                )
            
            else:
                raise Exception(f"Unsupported file type: {file_path.suffix}")
                
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")
    
    def extract_policy_info(self, text: str) -> Dict[str, Any]:
        """Extract policy-related information"""
        policy_info = {}
        
        # Extract policy number - multiple patterns
        policy_patterns = [
            r'POLICY\s*NUMBER[:\s]*([A-Z0-9-]+)',
            r'Policy\s*#[:\s]*([A-Z0-9-]+)',
            r'POL(?:ICY)?\s*NO\.?[:\s]*([A-Z0-9-]+)',
            r'Policy\s*No\.?[:\s]*([A-Z0-9-]+)'
        ]
        
        for pattern in policy_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                policy_info['policy_number'] = match.group(1).strip()
                break
        
        # Extract policyholder name
        name_patterns = [
            r'NAME\s+OF\s+INSURED\s*\([^)]+\)[:\s]*([A-Za-z\s,\.]+?)(?:\n|INSURED)',
            r'INSURED[:\s]+([A-Za-z\s,\.]+?)(?:\n|MAILING|ADDRESS)',
            r'Policyholder[:\s]+([A-Za-z\s,\.]+?)(?:\n)',
            r'Insured[:\s]*Name[:\s]*([A-Za-z\s,\.]+?)(?:\n)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up name (remove extra spaces, commas at end)
                name = ' '.join(name.split())
                name = name.rstrip(',').strip()
                if len(name) > 2:  # Ensure it's meaningful
                    policy_info['policyholder_name'] = name
                    break
        
        # Extract effective dates (if present)
        date_patterns = [
            r'Effective\s+Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Policy\s+Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                policy_info['effective_date'] = match.group(1)
                break
        
        return policy_info
    
    def extract_incident_info(self, text: str) -> Dict[str, Any]:
        """Extract incident-related information"""
        incident_info = {}
        
        # Extract date of loss
        date_patterns = [
            r'DATE\s+OF\s+LOSS\s+AND\s+TIME[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'DATE\s+OF\s+LOSS[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Loss\s+Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Incident\s+Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'DATE\s*\(MM/DD/YYYY\)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                incident_info['incident_date'] = match.group(1)
                break
        
        # Extract time
        time_patterns = [
            r'TIME[:\s]*(\d{1,2}:\d{2})\s*(AM|PM)',
            r'at\s*(\d{1,2}:\d{2})\s*(AM|PM)',
            r'(\d{1,2}:\d{2})\s*(AM|PM)'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                time_str = match.group(1)
                am_pm = match.group(2) if match.lastindex >= 2 else ''
                incident_info['incident_time'] = f"{time_str} {am_pm}".strip()
                break
        
        # Extract location - multiple approaches
        location_patterns = [
            r'LOCATION\s+OF\s+LOSS[:\s]*STREET[:\s]*([^\n]+?)(?:CITY|COUNTRY|\n\n)',
            r'STREET[:\s]*([^\n]+?)(?:CITY|COUNTRY|STATE)',
            r'(?:Location|Address)[:\s]*([^\n]+?)(?:\n|$)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                location = match.group(1).strip()
                # Clean up location
                location = ' '.join(location.split())
                if location and len(location) > 3:  # Ensure it's meaningful
                    incident_info['incident_location'] = location
                    break
        
        # Extract city, state, zip
        city_patterns = [
            r'CITY,\s*STATE,\s*ZIP[:\s]*([^\n]+)',
            r'City[:\s]*([A-Za-z\s]+),?\s*([A-Z]{2})\s*(\d{5})'
        ]
        for pattern in city_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                incident_info['city_state_zip'] = match.group(0).strip()
                break
        
        # Extract country
        country_match = re.search(r'COUNTRY[:\s]*([A-Za-z\s]+?)(?:\n|CITY)', text, re.IGNORECASE)
        if country_match:
            incident_info['country'] = country_match.group(1).strip()
        
        # Extract description
        desc_patterns = [
            r'DESCRIPTION\s+OF\s+ACCIDENT[:\s]*\([^)]+\)[:\s]*([^\n]+(?:\n(?![A-Z\s]+:)[^\n]+){0,5})',
            r'DESCRIPTION\s+OF\s+ACCIDENT[:\s]*([^\n]+(?:\n(?![A-Z\s]+:)[^\n]+){0,5})',
            r'Accident\s+Description[:\s]*([^\n]+(?:\n[^\n]+){0,5})',
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                description = match.group(1).strip()
                # Clean and limit description
                description = ' '.join(description.split())
                description = description[:500]  # Limit length
                if description:
                    incident_info['incident_description'] = description
                    break
        
        return incident_info
    
    def extract_involved_parties(self, text: str) -> Dict[str, Any]:
        """Extract information about involved parties"""
        parties_info = {}
        
        # Extract driver information
        driver_patterns = [
            r"DRIVER'S\s+NAME\s+AND\s+ADDRESS[:\s]*([^\n]+)",
            r"Driver[:\s]+([A-Za-z\s,\.]+?)(?:\n|PHONE|ADDRESS)"
        ]
        for pattern in driver_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                driver = match.group(1).strip()
                if len(driver) > 2:
                    parties_info['driver_name'] = driver
                    break
        
        # Extract owner information
        owner_patterns = [
            r"OWNER'S\s+NAME\s+AND\s+ADDRESS[:\s]*([^\n]+)",
            r"Owner[:\s]+([A-Za-z\s,\.]+?)(?:\n|PHONE)"
        ]
        for pattern in owner_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                owner = match.group(1).strip()
                if len(owner) > 2:
                    parties_info['owner_name'] = owner
                    break
        
        # Extract phone numbers
        phone_pattern = r'(?:PHONE|Tel|Contact).*?(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})'
        phones = re.findall(phone_pattern, text, re.IGNORECASE | re.DOTALL)
        if phones:
            # Clean phone number
            phone = phones[0].replace('-', '').replace('.', '').replace(' ', '')
            parties_info['contact_phone'] = phone
        
        # Extract email
        email_pattern = r'E-?MAIL\s*ADDRESS[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        match = re.search(email_pattern, text, re.IGNORECASE)
        if match:
            parties_info['contact_email'] = match.group(1)
        
        return parties_info
    
    def extract_asset_details(self, text: str) -> Dict[str, Any]:
        """Extract asset/vehicle information"""
        asset_info = {}
        
        # Determine asset type
        if re.search(r'\b(?:AUTOMOBILE|VEHICLE|CAR|TRUCK|VAN|INSURED\s+VEHICLE)\b', text, re.IGNORECASE):
            asset_info['asset_type'] = 'Vehicle'
        elif re.search(r'\b(?:PROPERTY|BUILDING|HOME|HOUSE)\b', text, re.IGNORECASE):
            asset_info['asset_type'] = 'Property'
        else:
            asset_info['asset_type'] = 'Unknown'
        
        # Extract VIN
        vin_pattern = r'V\.?I\.?N\.?[:\s]*([A-HJ-NPR-Z0-9]{17})'
        match = re.search(vin_pattern, text, re.IGNORECASE)
        if match:
            vin = match.group(1).strip()
            asset_info['asset_id'] = vin
            asset_info['vin'] = vin
        
        # Extract plate number
        plate_pattern = r'PLATE\s+NUMBER[:\s]*([A-Z0-9-]+)'
        match = re.search(plate_pattern, text, re.IGNORECASE)
        if match:
            asset_info['plate_number'] = match.group(1).strip()
        
        # Extract vehicle year
        year_pattern = r'(?:VEH\s*#\s*)?YEAR[:\s]*(\d{4})'
        match = re.search(year_pattern, text, re.IGNORECASE)
        if match:
            asset_info['vehicle_year'] = match.group(1)
        
        # Extract make
        make_pattern = r'MAKE[:\s]*([A-Za-z0-9\s]+?)(?:\s+VEH|\s+YEAR|\s+MODEL|:|\n)'
        match = re.search(make_pattern, text, re.IGNORECASE)
        if match:
            make = match.group(1).strip()
            if make and len(make) < 30:  # Reasonable length
                asset_info['vehicle_make'] = make
        
        # Extract model
        model_pattern = r'MODEL[:\s]*([A-Za-z0-9\s]+?)(?:\s+BODY|\s+TYPE|:|\n)'
        match = re.search(model_pattern, text, re.IGNORECASE)
        if match:
            model = match.group(1).strip()
            if model and len(model) < 30:
                asset_info['vehicle_model'] = model
        
        # Extract body type
        body_pattern = r'BODY[:\s]*([A-Za-z0-9\s]+?)(?:\s+MODEL|\s+TYPE|:|\n)'
        match = re.search(body_pattern, text, re.IGNORECASE)
        if match:
            body = match.group(1).strip()
            if body and len(body) < 30:
                asset_info['body_type'] = body
        
        # Extract damage estimate
        estimate_patterns = [
            r'ESTIMATE\s+AMOUNT[:\s]*\$?\s*([0-9,]+\.?\d*)',
            r'Estimated?\s+Damage[:\s]*\$?\s*([0-9,]+\.?\d*)',
            r'Damage\s+Estimate[:\s]*\$?\s*([0-9,]+\.?\d*)',
            r'\$\s*([0-9,]+\.?\d*)\s*(?:damage|estimate)'
        ]
        
        for pattern in estimate_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '').replace('$', '')
                try:
                    amount = float(amount_str)
                    if amount > 0:  # Valid amount
                        asset_info['estimated_damage'] = amount
                        break
                except ValueError:
                    continue
        
        # Extract damage description
        damage_patterns = [
            r'DESCRIBE\s+DAMAGE[:\s]*([^\n]+?)(?:\n[A-Z\s]+:|$)',
            r'Damage\s+Description[:\s]*([^\n]+)'
        ]
        for pattern in damage_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                damage = match.group(1).strip()
                if damage and len(damage) > 3:
                    asset_info['damage_description'] = damage
                    break
        
        return asset_info
    
    def determine_claim_type(self, text: str, extracted_data: Dict) -> str:
        """Determine the type of claim"""
        text_lower = text.lower()
        
        # Check for injury claims (highest priority)
        injury_indicators = ['injured', 'injury', 'extent of injury', 'medical', 'hospital']
        if any(keyword in text_lower for keyword in injury_indicators):
            return 'injury'
        
        # Check asset type
        asset_type = extracted_data.get('asset_type', '').lower()
        
        # Check for property damage
        if 'property' in asset_type:
            return 'property_damage'
        
        # Check for vehicle-related claims
        if 'vehicle' in asset_type or 'automobile' in text_lower:
            # Look for collision indicators
            collision_words = ['collision', 'accident', 'crash', 'hit', 'struck']
            if any(word in text_lower for word in collision_words):
                return 'vehicle_collision'
            return 'vehicle_damage'
        
        return 'general'
    
    def check_fraud_indicators(self, text: str) -> bool:
        """Check for potential fraud indicators in the text"""
        text_lower = text.lower()
        
        # Check for fraud keywords
        for keyword in self.FRAUD_KEYWORDS:
            if keyword in text_lower:
                return True
        
        # Additional fraud patterns
        suspicious_patterns = [
            r'seems?\s+(?:fake|staged|suspicious)',
            r'(?:might|could)\s+be\s+fraud',
            r'doesn\'?t\s+add\s+up'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def process_claim(self, file_path: str) -> Dict[str, Any]:
        """Main processing function for a claim document"""
        
        # Extract text from file
        text = self.extract_text_from_file(file_path)
        
        # Extract all fields
        extracted_fields = {}
        
        # Policy information
        policy_info = self.extract_policy_info(text)
        extracted_fields.update(policy_info)
        
        # Incident information
        incident_info = self.extract_incident_info(text)
        extracted_fields.update(incident_info)
        
        # Involved parties
        parties_info = self.extract_involved_parties(text)
        extracted_fields.update(parties_info)
        
        # Asset details
        asset_info = self.extract_asset_details(text)
        extracted_fields.update(asset_info)
        
        # Determine claim type
        claim_type = self.determine_claim_type(text, extracted_fields)
        extracted_fields['claim_type'] = claim_type
        
        # Check for missing mandatory fields
        missing_fields = []
        for field in self.MANDATORY_FIELDS:
            if field not in extracted_fields or not extracted_fields[field]:
                missing_fields.append(field)
        
        # Determine routing
        route, reasoning = self.determine_route(
            extracted_fields, 
            missing_fields, 
            text
        )
        
        # Build result
        result = {
            "extractedFields": extracted_fields,
            "missingFields": missing_fields,
            "recommendedRoute": route,
            "reasoning": reasoning,
            "processingTimestamp": datetime.now().isoformat(),
            "sourceFile": Path(file_path).name
        }
        
        return result
    
    def determine_route(
        self, 
        extracted_fields: Dict[str, Any], 
        missing_fields: List[str],
        full_text: str
    ) -> tuple:
        """Determine routing and provide reasoning"""
        
        reasoning_parts = []
        
        # Rule 1: Check for missing mandatory fields
        if missing_fields:
            route = "Manual Review"
            reasoning_parts.append(
                f"Missing mandatory fields: {', '.join(missing_fields)}"
            )
            reasoning = ". ".join(reasoning_parts)
            return route, reasoning
        
        # Rule 2: Check for fraud indicators
        if self.check_fraud_indicators(full_text):
            route = "Investigation Queue"
            reasoning_parts.append(
                "Potential fraud indicators detected in claim description or documentation"
            )
            reasoning = ". ".join(reasoning_parts)
            return route, reasoning
        
        # Rule 3: Check for injury claims
        claim_type = extracted_fields.get('claim_type', '').lower()
        if claim_type == 'injury':
            route = "Specialist Queue"
            reasoning_parts.append(
                "Claim involves injury and requires specialist medical review"
            )
            reasoning = ". ".join(reasoning_parts)
            return route, reasoning
        
        # Rule 4: Check damage estimate for fast-track
        estimated_damage = extracted_fields.get('estimated_damage', 0)
        if estimated_damage > 0:
            if estimated_damage < self.FAST_TRACK_THRESHOLD:
                route = "Fast-Track"
                reasoning_parts.append(
                    f"Estimated damage (${estimated_damage:,.2f}) is below "
                    f"fast-track threshold (${self.FAST_TRACK_THRESHOLD:,})"
                )
            else:
                route = "Standard Processing"
                reasoning_parts.append(
                    f"Estimated damage (${estimated_damage:,.2f}) exceeds "
                    f"fast-track threshold (${self.FAST_TRACK_THRESHOLD:,}). "
                    f"Requires standard review process"
                )
        else:
            route = "Manual Review"
            reasoning_parts.append(
                "No damage estimate provided - requires manual assessment"
            )
        
        reasoning = ". ".join(reasoning_parts) if reasoning_parts else "Standard processing applied"
        return route, reasoning


def main():
    """Main entry point for the claims processor"""
    import sys
    
    if len(sys.argv) < 2:
        print("=" * 60)
        print("Insurance Claims Processing Agent")
        print("=" * 60)
        print("\nUsage: python claims_processor_simple.py <path_to_fnol_file>")
        print("\nSupported formats: PDF, TXT")
        print("\nExample:")
        print("  python claims_processor_simple.py claim.pdf")
        print("  python claims_processor_simple.py claim.txt")
        print("=" * 60)
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"Error: File not found - {file_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("PROCESSING INSURANCE CLAIM")
    print("=" * 60)
    print(f"File: {Path(file_path).name}")
    print("-" * 60)
    
    try:
        # Process the claim
        processor = ClaimsProcessor()
        result = processor.process_claim(file_path)
        
        # Display results in console
        print("\n EXTRACTED FIELDS:")
        print("-" * 60)
        for key, value in result['extractedFields'].items():
            print(f"  {key}: {value}")
        
        print(f"\n  VALIDATION:")
        print("-" * 60)
        if result['missingFields']:
            print(f"  Missing fields: {', '.join(result['missingFields'])}")
        else:
            print("  ✓ All mandatory fields present")
        
        print(f"\n🚦 ROUTING DECISION:")
        print("-" * 60)
        print(f"  Route: {result['recommendedRoute']}")
        print(f"  Reasoning: {result['reasoning']}")
        
        # Output as JSON
        print("\n" + "=" * 60)
        print("JSON OUTPUT:")
        print("=" * 60)
        print(json.dumps(result, indent=2))
        
        # Save to file
        output_file = Path(file_path).stem + "_processed.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print("\n" + "=" * 60)
        print(f"✓ Results saved to: {output_file}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\Error processing claim: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
