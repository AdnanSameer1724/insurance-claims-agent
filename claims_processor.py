"""
Autonomous Insurance Claims Processing Agent
Extracts, validates, and routes FNOL (First Notice of Loss) documents
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
import pdfplumber
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
    FRAUD_KEYWORDS = ['fraud', 'inconsistent', 'staged', 'suspicious', 'fake']
    
    # Injury-related keywords
    INJURY_KEYWORDS = ['injury', 'injured', 'hurt', 'medical', 'hospital', 'ambulance']
    
    def __init__(self):
        self.extracted_data = {}
        self.missing_fields = []
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def extract_policy_info(self, text: str) -> Dict[str, Any]:
        """Extract policy-related information"""
        policy_info = {}
        
        # Extract policy number
        policy_patterns = [
            r'POLICY\s*NUMBER[:\s]*([A-Z0-9-]+)',
            r'Policy\s*#[:\s]*([A-Z0-9-]+)',
            r'POL(?:ICY)?\s*NO[.:]?\s*([A-Z0-9-]+)'
        ]
        
        for pattern in policy_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                policy_info['policy_number'] = match.group(1).strip()
                break
        
        # Extract policyholder name
        name_patterns = [
            r'NAME\s+OF\s+INSURED[:\s]*([A-Za-z\s,]+?)(?:\n|DATE)',
            r'INSURED[:\s]+([A-Za-z\s,]+?)(?:\n|MAILING)',
            r'Policyholder[:\s]+([A-Za-z\s,]+?)(?:\n)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up name (remove extra spaces, etc.)
                name = ' '.join(name.split())
                policy_info['policyholder_name'] = name
                break
        
        # Extract effective dates (if present)
        date_pattern = r'(?:Effective|Policy)\s+Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        match = re.search(date_pattern, text, re.IGNORECASE)
        if match:
            policy_info['effective_date'] = match.group(1)
        
        return policy_info
    
    def extract_incident_info(self, text: str) -> Dict[str, Any]:
        """Extract incident-related information"""
        incident_info = {}
        
        # Extract date of loss
        date_patterns = [
            r'DATE\s+OF\s+LOSS[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Loss\s+Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Incident\s+Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                incident_info['incident_date'] = match.group(1)
                break
        
        # Extract time
        time_patterns = [
            r'TIME[:\s]*(\d{1,2}:\d{2})\s*(AM|PM)?',
            r'(?:at|@)\s*(\d{1,2}:\d{2})\s*(AM|PM)?'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                time_str = match.group(1)
                am_pm = match.group(2) if match.lastindex >= 2 else ''
                incident_info['incident_time'] = f"{time_str} {am_pm}".strip()
                break
        
        # Extract location
        location_patterns = [
            r'LOCATION\s+OF\s+LOSS[:\s]*([^\n]+)',
            r'(?:STREET|ADDRESS)[:\s]*([^\n]+?)(?:CITY|STATE|\n)',
            r'(?:Location|Address)[:\s]*([^\n]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                if location and len(location) > 5:  # Ensure it's meaningful
                    incident_info['incident_location'] = location
                    break
        
        # Extract city, state, zip
        city_state_pattern = r'CITY,\s*STATE,\s*ZIP[:\s]*([^\n]+)'
        match = re.search(city_state_pattern, text, re.IGNORECASE)
        if match:
            incident_info['city_state_zip'] = match.group(1).strip()
        
        # Extract description
        desc_patterns = [
            r'DESCRIPTION\s+OF\s+ACCIDENT[:\s]*([^\n]+(?:\n(?![A-Z\s]+:)[^\n]+)*)',
            r'(?:Accident|Incident)\s+Description[:\s]*([^\n]+(?:\n[^\n]+)*)',
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                description = match.group(1).strip()
                # Take first reasonable chunk
                description = ' '.join(description.split()[:100])
                incident_info['incident_description'] = description
                break
        
        return incident_info
    
    def extract_involved_parties(self, text: str) -> Dict[str, Any]:
        """Extract information about involved parties"""
        parties_info = {}
        
        # Extract claimant (often same as insured)
        claimant_pattern = r'(?:Claimant|Insured)[:\s]+([A-Za-z\s,]+?)(?:\n|PHONE)'
        match = re.search(claimant_pattern, text, re.IGNORECASE)
        if match:
            parties_info['claimant_name'] = match.group(1).strip()
        
        # Extract driver information
        driver_pattern = r"DRIVER'S\s+NAME\s+AND\s+ADDRESS[:\s]*([^\n]+)"
        match = re.search(driver_pattern, text, re.IGNORECASE)
        if match:
            parties_info['driver_name'] = match.group(1).strip()
        
        # Extract phone numbers
        phone_patterns = r'(?:PHONE|Tel)[:\s#]*(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})'
        phones = re.findall(phone_patterns, text, re.IGNORECASE)
        if phones:
            parties_info['contact_phone'] = phones[0]
        
        # Extract email
        email_pattern = r'E-?MAIL[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        match = re.search(email_pattern, text, re.IGNORECASE)
        if match:
            parties_info['contact_email'] = match.group(1)
        
        return parties_info
    
    def extract_asset_details(self, text: str) -> Dict[str, Any]:
        """Extract asset/vehicle information"""
        asset_info = {}
        
        # Determine asset type
        if re.search(r'\b(?:VEHICLE|AUTOMOBILE|CAR|TRUCK|VAN)\b', text, re.IGNORECASE):
            asset_info['asset_type'] = 'Vehicle'
        elif re.search(r'\b(?:PROPERTY|BUILDING|HOME|HOUSE)\b', text, re.IGNORECASE):
            asset_info['asset_type'] = 'Property'
        else:
            asset_info['asset_type'] = 'Unknown'
        
        # Extract VIN
        vin_pattern = r'V\.?I\.?N\.?[:\s]*([A-HJ-NPR-Z0-9]{17})'
        match = re.search(vin_pattern, text, re.IGNORECASE)
        if match:
            asset_info['asset_id'] = match.group(1)
            asset_info['vin'] = match.group(1)
        
        # Extract vehicle details
        make_pattern = r'MAKE[:\s]*([A-Za-z0-9\s]+?)(?:\n|VEH|YEAR|MODEL)'
        match = re.search(make_pattern, text, re.IGNORECASE)
        if match:
            asset_info['vehicle_make'] = match.group(1).strip()
        
        model_pattern = r'MODEL[:\s]*([A-Za-z0-9\s]+?)(?:\n|YEAR|BODY|TYPE)'
        match = re.search(model_pattern, text, re.IGNORECASE)
        if match:
            asset_info['vehicle_model'] = match.group(1).strip()
        
        year_pattern = r'YEAR[:\s]*(\d{4})'
        match = re.search(year_pattern, text, re.IGNORECASE)
        if match:
            asset_info['vehicle_year'] = match.group(1)
        
        # Extract damage estimate
        estimate_patterns = [
            r'ESTIMATE\s+AMOUNT[:\s]*\$?\s*([0-9,]+\.?\d*)',
            r'Estimated?\s+Damage[:\s]*\$?\s*([0-9,]+\.?\d*)',
            r'Damage\s+Estimate[:\s]*\$?\s*([0-9,]+\.?\d*)'
        ]
        
        for pattern in estimate_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                try:
                    asset_info['estimated_damage'] = float(amount)
                except ValueError:
                    pass
                break
        
        # Extract damage description
        damage_desc_pattern = r'DESCRIBE\s+DAMAGE[:\s]*([^\n]+)'
        match = re.search(damage_desc_pattern, text, re.IGNORECASE)
        if match:
            asset_info['damage_description'] = match.group(1).strip()
        
        return asset_info
    
    def determine_claim_type(self, text: str, extracted_data: Dict) -> str:
        """Determine the type of claim"""
        text_lower = text.lower()
        
        # Check for injury claims
        if any(keyword in text_lower for keyword in self.INJURY_KEYWORDS):
            return 'injury'
        
        # Check for property damage
        if 'property' in extracted_data.get('asset_type', '').lower():
            return 'property_damage'
        
        # Check for vehicle collision
        if 'vehicle' in extracted_data.get('asset_type', '').lower():
            if any(word in text_lower for word in ['collision', 'accident', 'crash']):
                return 'vehicle_collision'
            return 'vehicle_damage'
        
        return 'general'
    
    def check_fraud_indicators(self, text: str) -> bool:
        """Check for potential fraud indicators in the text"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.FRAUD_KEYWORDS)
    
    def process_claim(self, pdf_path: str) -> Dict[str, Any]:
        """Main processing function for a claim document"""
        
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        
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
            "processingTimestamp": datetime.now().isoformat()
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
                "Potential fraud indicators detected in claim description"
            )
            reasoning = ". ".join(reasoning_parts)
            return route, reasoning
        
        # Rule 3: Check for injury claims
        claim_type = extracted_fields.get('claim_type', '').lower()
        if claim_type == 'injury':
            route = "Specialist Queue"
            reasoning_parts.append(
                "Claim involves injury and requires specialist review"
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
                    f"fast-track threshold (${self.FAST_TRACK_THRESHOLD:,})"
                )
        else:
            route = "Manual Review"
            reasoning_parts.append(
                "No damage estimate provided - requires manual review"
            )
        
        reasoning = ". ".join(reasoning_parts)
        return route, reasoning


def main():
    """Main entry point for the claims processor"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python claims_processor.py <path_to_fnol_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"Error: File not found - {pdf_path}")
        sys.exit(1)
    
    # Process the claim
    processor = ClaimsProcessor()
    result = processor.process_claim(pdf_path)
    
    # Output as JSON
    print(json.dumps(result, indent=2))
    
    # Optionally save to file
    output_file = Path(pdf_path).stem + "_processed.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✓ Results saved to: {output_file}")


if __name__ == "__main__":
    main()
