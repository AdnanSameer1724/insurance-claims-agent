"""
Test script to process sample FNOL documents
"""

import json
from pathlib import Path
from claims_processor import ClaimsProcessor


def test_sample_document():
    """Test processing of the sample ACORD document"""
    
    # Path to the sample document
    sample_pdf = "/mnt/user-data/uploads/ACORD-Automobile-Loss-Notice-12_05_16.pdf"
    
    if not Path(sample_pdf).exists():
        print(f"Error: Sample document not found at {sample_pdf}")
        return
    
    print("=" * 60)
    print("INSURANCE CLAIMS PROCESSING AGENT - TEST RUN")
    print("=" * 60)
    print(f"\nProcessing: {Path(sample_pdf).name}")
    print("-" * 60)
    
    # Create processor instance
    processor = ClaimsProcessor()
    
    try:
        # Process the claim
        result = processor.process_claim(sample_pdf)
        
        # Display results
        print("\n📋 EXTRACTED FIELDS:")
        print("-" * 60)
        for key, value in result['extractedFields'].items():
            print(f"  {key}: {value}")
        
        print(f"\n⚠️  MISSING FIELDS:")
        print("-" * 60)
        if result['missingFields']:
            for field in result['missingFields']:
                print(f"  - {field}")
        else:
            print("  ✓ All mandatory fields present")
        
        print(f"\n🚦 ROUTING DECISION:")
        print("-" * 60)
        print(f"  Route: {result['recommendedRoute']}")
        print(f"  Reasoning: {result['reasoning']}")
        
        # Save results
        output_file = "test_results.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\n✓ Full results saved to: {output_file}")
        print("=" * 60)
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error processing claim: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_sample_document()
