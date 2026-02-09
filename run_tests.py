"""
Comprehensive Test Suite for Insurance Claims Processing Agent
Tests all routing scenarios and validation logic
"""

import json
from pathlib import Path
from claims_processor_simple import ClaimsProcessor


def print_section_header(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_test_result(test_name, result):
    """Print formatted test results"""
    print(f"\n🔍 Test: {test_name}")
    print("-" * 70)
    
    print("\ Extracted Fields:")
    for key, value in result['extractedFields'].items():
        print(f"  • {key}: {value}")
    
    if result['missingFields']:
        print(f"\  Missing Fields: {', '.join(result['missingFields'])}")
    else:
        print("\n✓ All mandatory fields present")
    
    print(f"\n🚦 Route: {result['recommendedRoute']}")
    print(f" Reasoning: {result['reasoning']}\n")


def run_all_tests():
    """Run all test scenarios"""
    
    print_section_header("INSURANCE CLAIMS PROCESSING AGENT - TEST SUITE")
    
    processor = ClaimsProcessor()
    
    # Define test cases
    test_cases = [
        {
            "name": "Scenario 1: Injury Claim - Specialist Queue",
            "file": "sample_claim.txt",
            "expected_route": "Specialist Queue"
        },
        {
            "name": "Scenario 2: Low Damage - Fast Track",
            "file": "sample_claim_fasttrack.txt",
            "expected_route": "Fast-Track"
        },
        {
            "name": "Scenario 3: Fraud Indicators - Investigation Queue",
            "file": "sample_claim_fraud.txt",
            "expected_route": "Investigation Queue"
        },
        {
            "name": "Scenario 4: Missing Fields - Manual Review",
            "file": "sample_claim_incomplete.txt",
            "expected_route": "Manual Review"
        }
    ]
    
    results_summary = []
    
    # Run each test
    for i, test in enumerate(test_cases, 1):
        try:
            file_path = test["file"]
            
            if not Path(file_path).exists():
                print(f"\  Warning: Test file not found: {file_path}")
                continue
            
            print_section_header(f"TEST {i}: {test['name']}")
            
            # Process claim
            result = processor.process_claim(file_path)
            
            # Print results
            print_test_result(test['name'], result)
            
            # Check if route matches expected
            route_match = result['recommendedRoute'] == test['expected_route']
            
            test_status = {
                'test': test['name'],
                'file': test['file'],
                'expected_route': test['expected_route'],
                'actual_route': result['recommendedRoute'],
                'passed': route_match,
                'missing_fields': result['missingFields']
            }
            
            results_summary.append(test_status)
            
            if route_match:
                print(f" PASS: Route matches expected ({test['expected_route']})")
            else:
                print(f" FAIL: Expected {test['expected_route']}, got {result['recommendedRoute']}")
            
        except Exception as e:
            print(f"\ Error in test '{test['name']}': {str(e)}")
            results_summary.append({
                'test': test['name'],
                'passed': False,
                'error': str(e)
            })
    
    # Print summary
    print_section_header("TEST SUMMARY")
    
    passed = sum(1 for r in results_summary if r.get('passed', False))
    total = len(results_summary)
    
    print(f"\nTests Passed: {passed}/{total}")
    print("-" * 70)
    
    for i, result in enumerate(results_summary, 1):
        status = " PASS" if result.get('passed') else " FAIL"
        print(f"{i}. {status} - {result['test']}")
        if not result.get('passed'):
            if 'error' in result:
                print(f"   Error: {result['error']}")
            else:
                print(f"   Expected: {result.get('expected_route')}")
                print(f"   Got: {result.get('actual_route')}")
    
    print("\n" + "=" * 70)
    
    # Save summary to JSON
    with open('test_summary.json', 'w') as f:
        json.dump({
            'total_tests': total,
            'passed': passed,
            'failed': total - passed,
            'results': results_summary
        }, f, indent=2)
    
    print(f"\n✓ Test summary saved to: test_summary.json")
    print("=" * 70)


def test_routing_rules():
    """Test individual routing rules"""
    
    print_section_header("ROUTING RULES VALIDATION")
    
    processor = ClaimsProcessor()
    
    print("\ Configured Routing Rules:")
    print("-" * 70)
    print(f"1. Fast-Track Threshold: ${processor.FAST_TRACK_THRESHOLD:,}")
    print(f"2. Mandatory Fields: {', '.join(processor.MANDATORY_FIELDS)}")
    print(f"3. Fraud Keywords: {', '.join(processor.FRAUD_KEYWORDS)}")
    print(f"4. Injury Keywords: {', '.join(processor.INJURY_KEYWORDS)}")
    
    print("\ Routing Priority:")
    print("-" * 70)
    print("1. Missing mandatory fields → Manual Review (Highest)")
    print("2. Fraud indicators → Investigation Queue")
    print("3. Injury claims → Specialist Queue")
    print("4. Damage < $25,000 → Fast-Track")
    print("5. Damage ≥ $25,000 → Standard Processing (Lowest)")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Test routing rules
    test_routing_rules()
    
    # Run all test scenarios
    run_all_tests()
    
    print("\n🎉 All tests completed!")
