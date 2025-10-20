import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import time
import random

def get_detailed_location(parsed_number, country_code):
    """
    Get detailed location information including state/province
    """
    location_info = {
        'country': 'Unknown',
        'state': 'Unknown', 
        'city': 'Unknown',
        'full_location': 'Unknown'
    }
    
    try:
        # Get basic location description
        basic_location = geocoder.description_for_number(parsed_number, "en")
        
        if basic_location:
            location_info['full_location'] = basic_location
            
            # Parse the location string to extract state/country information
            location_parts = basic_location.split(',')
            
            if len(location_parts) >= 2:
                # For formats like "City, State, Country" or "State, Country"
                location_info['city'] = location_parts[0].strip()
                location_info['state'] = location_parts[1].strip()
                location_info['country'] = location_parts[-1].strip()
            else:
                # If only one part, it's usually just the country
                location_info['country'] = basic_location
            
            # Special handling for specific countries
            if country_code == "1":  # USA/Canada
                location_info = enhance_us_ca_location(parsed_number, location_info)
            elif country_code == "91":  # India
                location_info = enhance_india_location(parsed_number, location_info)
            elif country_code == "44":  # UK
                location_info = enhance_uk_location(parsed_number, location_info)
            elif country_code == "61":  # Australia
                location_info = enhance_australia_location(parsed_number, location_info)
                
    except Exception as e:
        print(f"[-] Warning: Could not get detailed location: {e}")
    
    return location_info

def enhance_us_ca_location(parsed_number, location_info):
    """Enhanced location for US and Canada"""
    try:
        description = geocoder.description_for_number(parsed_number, "en")
        if description:
            parts = description.split(',')
            if len(parts) == 2:  # "City, State" format
                location_info['city'] = parts[0].strip()
                location_info['state'] = parts[1].strip()
                location_info['country'] = "United States" if parsed_number.country_code == 1 else "Canada"
    except:
        pass
    return location_info

def enhance_india_location(parsed_number, location_info):
    """Enhanced location for India"""
    try:
        description = geocoder.description_for_number(parsed_number, "en")
        if description:
            # Indian numbers often show circle/telecom district
            if 'Telecom' in description or 'Circle' in description:
                location_info['state'] = description
                location_info['country'] = "India"
    except:
        pass
    return location_info

def enhance_uk_location(parsed_number, location_info):
    """Enhanced location for UK"""
    try:
        description = geocoder.description_for_number(parsed_number, "en")
        if description:
            if description in ['London', 'Manchester', 'Birmingham', 'Glasgow']:
                location_info['city'] = description
                location_info['country'] = "United Kingdom"
    except:
        pass
    return location_info

def enhance_australia_location(parsed_number, location_info):
    """Enhanced location for Australia"""
    try:
        description = geocoder.description_for_number(parsed_number, "en")
        if description:
            australian_states = ['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'ACT', 'NT']
            for state in australian_states:
                if state in description:
                    location_info['state'] = state
                    location_info['country'] = "Australia"
                    break
    except:
        pass
    return location_info

def get_country_name(country_code):
    """Convert country code to country name"""
    country_map = {
        "1": "United States/Canada",
        "91": "India", 
        "44": "United Kingdom",
        "61": "Australia",
        "86": "China",
        "81": "Japan",
        "49": "Germany",
        "33": "France",
        "39": "Italy",
        "34": "Spain",
        "7": "Russia",
        "55": "Brazil",
        "52": "Mexico",
        "82": "South Korea",
        # Add more country codes as needed
    }
    return country_map.get(str(country_code), f"Country Code +{country_code}")

def validate_phone_number(phone_number):
    """Validate and clean the phone number input"""
    try:
        # Remove any spaces and special characters except +
        cleaned_number = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        if not cleaned_number:
            raise ValueError("Empty phone number provided")
            
        # Parse the phone number
        parsed_number = phonenumbers.parse(cleaned_number, None)
        
        # Check if the number is valid
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValueError("Invalid phone number")
            
        return parsed_number, cleaned_number
        
    except phonenumbers.NumberParseException as e:
        raise ValueError(f"Failed to parse phone number: {e}")
    except Exception as e:
        raise ValueError(f"Error validating phone number: {e}")

def get_phone_info(parsed_number):
    """Extract comprehensive information from the parsed phone number"""
    info = {}
    
    try:
        country_code = str(parsed_number.country_code)
        
        # Get detailed location information
        location_info = get_detailed_location(parsed_number, country_code)
        
        info.update(location_info)
        
        # Get carrier information
        carrier_info = carrier.name_for_number(parsed_number, "en")
        info['carrier'] = carrier_info if carrier_info else "Unknown"
        
        # Get timezone information
        timezones = timezone.time_zones_for_number(parsed_number)
        info['timezone'] = list(timezones) if timezones else ["Unknown"]
        
        # Get country information
        info['country_code'] = parsed_number.country_code
        info['country_name'] = get_country_name(country_code)
        info['national_number'] = parsed_number.national_number
        
        # Format number in different formats
        info['international_format'] = phonenumbers.format_number(
            parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )
        info['national_format'] = phonenumbers.format_number(
            parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL
        )
        
        # Get number type
        number_type = phonenumbers.number_type(parsed_number)
        type_map = {
            phonenumbers.PhoneNumberType.MOBILE: "Mobile",
            phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Line",
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
            phonenumbers.PhoneNumberType.TOLL_FREE: "Toll Free",
            phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
            phonenumbers.PhoneNumberType.SHARED_COST: "Shared Cost",
            phonenumbers.PhoneNumberType.VOIP: "VOIP",
            phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
            phonenumbers.PhoneNumberType.PAGER: "Pager",
            phonenumbers.PhoneNumberType.UAN: "UAN",
            phonenumbers.PhoneNumberType.VOICEMAIL: "Voicemail",
            phonenumbers.PhoneNumberType.UNKNOWN: "Unknown"
        }
        info['number_type'] = type_map.get(number_type, "Unknown")
        
    except Exception as e:
        print(f"[-] Warning: Some information could not be retrieved: {e}")
        # Set default values for missing information
        defaults = {
            'country': 'Unknown', 'state': 'Unknown', 'city': 'Unknown',
            'full_location': 'Unknown', 'carrier': 'Unknown', 
            'timezone': ['Unknown'], 'number_type': 'Unknown'
        }
        for key, value in defaults.items():
            info.setdefault(key, value)
        
    return info

def simulate_trace_animation():
    """Simulate a tracing animation for better user experience"""
    steps = [
        "Initializing trace protocol...",
        "Connecting to carrier databases...",
        "Querying location services...",
        "Analyzing number patterns...",
        "Cross-referencing with global directories...",
        "Mapping geographical coordinates...",
        "Identifying state/province boundaries...",
        "Finalizing trace results..."
    ]
    
    for step in steps:
        print(f"[*] {step}")
        time.sleep(0.5 + random.uniform(0.1, 0.3))

def display_results(phone_info, original_number):
    """Display the tracing results in a formatted way"""
    print("\n" + "="*60)
    print("📱 PHONE TRACER RESULTS - ENHANCED LOCATION DATA")
    print("="*60)
    print(f"Target Number: {original_number}")
    print(f"International Format: {phone_info['international_format']}")
    print(f"National Format: {phone_info['national_format']}")
    print(f"Country Code: +{phone_info['country_code']}")
    print(f"Country: {phone_info['country_name']}")
    print(f"National Number: {phone_info['national_number']}")
    print(f"Number Type: {phone_info['number_type']}")
    print("\n📍 LOCATION INFORMATION:")
    print(f"  • Full Location: {phone_info['full_location']}")
    print(f"  • Country: {phone_info['country']}")
    print(f"  • State/Province: {phone_info['state']}")
    print(f"  • City/Area: {phone_info['city']}")
    print(f"📡 Carrier: {phone_info['carrier']}")
    print(f"🕐 Timezone(s): {', '.join(phone_info['timezone'])}")
    print("="*60)

def start_phone_tracer(target_phone):
    """
    Main function to trace phone number information with state detection
    
    Args:
        target_phone (str): Phone number to trace (can be in any format)
    """
    try:
        # Display header
        print("\n" + "🔍" * 30)
        print("[+] PhoneTracer v3.0 - Enhanced Location Detection")
        print("🔍" * 30)
        
        # Validate and parse the phone number
        print(f"[*] Target: {target_phone}")
        parsed_number, cleaned_number = validate_phone_number(target_phone)
        
        # Simulate tracing process
        print("\n[*] Starting enhanced trace sequence...")
        simulate_trace_animation()
        
        # Get phone information
        print("\n[*] Retrieving detailed location information...")
        phone_info = get_phone_info(parsed_number)
        
        # Display results
        display_results(phone_info, target_phone)
        
        print("\n[✅] Enhanced Trace Complete!")
        
    except ValueError as e:
        print(f"\n[❌] Error: {e}")
        print("[!] Please check the phone number format and try again.")
        
    except Exception as e:
        print(f"\n[❌] Unexpected error: {e}")
        print("[!] An unexpected error occurred. Please try again.")

def test_state_detection():
    """Test function to demonstrate state detection for various countries"""
    test_cases = [
        "+1 123 456 7890",    # New York, USA
        "+1 123 456 7890",    # Toronto, Canada  
        "+44 12 3456 7890",   # London, UK
        "+91 12 3456 7890",   # Bangalore, India
        "+61 1 2345 6789",    # Sydney, Australia
        "+49 12 3456 7890",   # Berlin, Germany
        "+33 1 2345 6789",    # Paris, France
    ]
    
    print("\n🧪 Testing State/Province Detection...")
    for number in test_cases:
        print(f"\nTesting: {number}")
        try:
            parsed, cleaned = validate_phone_number(number)
            info = get_phone_info(parsed)
            print(f"  Location: {info['full_location']}")
            print(f"  State: {info['state']}")
            print(f"  Country: {info['country']}")
        except Exception as e:
            print(f"  Error: {e}")

def main():
    """Main function with example usage"""
    # Example phone numbers from different countries
    test_numbers = [
        "+91 1234567890",    # Indian number
        "+1 123 456 7890",    # US number
        "+44 12 3456 7890",   # UK number
        "+61 1 2345 6789",    # Australian number
        "+49 12 3456 7890",   # German number
    ]
    
    print("🌍 Enhanced Phone Tracer with State Detection")
    print("\nAvailable test numbers:")
    for i, number in enumerate(test_numbers, 1):
        print(f"{i}. {number}")
    
    try:
        choice = input("\nEnter choice (1-5), 'test' for state detection test, or type your own number: ").strip()
        
        if choice.lower() == 'test':
            test_state_detection()
        elif choice.isdigit() and 1 <= int(choice) <= len(test_numbers):
            target = test_numbers[int(choice) - 1]
            start_phone_tracer(target)
        else:
            target = choice
            start_phone_tracer(target)
            
    except KeyboardInterrupt:
        print("\n\n[!] Trace cancelled by user.")
    except Exception as e:
        print(f"\n[❌] Error: {e}")

if __name__ == "__main__":
    main()

