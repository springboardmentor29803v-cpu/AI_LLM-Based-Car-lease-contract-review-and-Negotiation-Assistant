import requests

def validate_vin(vin_number):
    """
    Checks the VIN against the official US Government (NHTSA) Database.
    """
    if not vin_number:
        return {"error": "No VIN provided"}

    print(f"--- 🔍 Checking VIN {vin_number} with NHTSA... ---")
    
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/{vin_number}?format=json"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        decoded = {}
        for item in data['Results']:
            if item['Variable'] == 'Make':
                decoded['Make'] = item['Value']
            if item['Variable'] == 'Model':
                decoded['Model'] = item['Value']
            if item['Variable'] == 'Model Year':
                decoded['Year'] = item['Value']
            if item['Variable'] == 'Error Code':
                error_code = item['Value']

        if error_code == "0":
            return {
                "valid": True,
                "details": decoded
            }
        else:
            return {
                "valid": False,
                "error": "Invalid VIN (Not found in Gov Database)"
            }

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    test_vin = "1HGCM82633A004352" 
    result = validate_vin(test_vin)
    print(result)
