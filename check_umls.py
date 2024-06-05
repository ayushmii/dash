import requests

# Replace with your UMLS API key
API_KEY = "4460d46d-6916-47f4-95aa-e5cf407f9773"

# Define the base URL for the UMLS API
BASE_URL = "https://uts-ws.nlm.nih.gov/restful/content"

def get_umls_concepts(term):
    print("checking")
    """
    Retrieves UMLS concepts for a given term using the UMLS API.
    
    Args:
        term (str): The term to search for in the UMLS.
        
    Returns:
        list: A list of dictionaries containing information about the retrieved UMLS concepts.
    """
    # Construct the API endpoint URL
    endpoint = f"{BASE_URL}/current/source/UMLS/concept/{term}"
    
    # Set the API key in the request headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        # Make the API request
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        
        # Parse the response JSON
        data = response.json()
        
        # Extract the concept information
        concepts = data["result"]["concepts"]
        
        # Return the list of concepts
        return concepts
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

# Example usage
term = "fever"
concepts = get_umls_concepts(term)

if concepts:
    print(f"UMLS concepts for '{term}':")
    for concept in concepts:
        print(f"  - {concept['name']} ({concept['ui']})")
else:
    print(f"No UMLS concepts found for '{term}'")