class FareRetriever:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
    
    def get_fares(self):
        response = requests.get(f"{self.base_url}/fares")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Failed to fetch fares"}

# Usage
retriever = FareRetriever()
fares = retriever.get_fares()
print(fares)
