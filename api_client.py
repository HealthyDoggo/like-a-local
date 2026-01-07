"""API client for TravelBuddy backend"""
import os
import requests
import json
from typing import Optional, List, Dict
from requests.exceptions import RequestException, ConnectionError, Timeout


class TravelBuddyAPI:
    """Client for TravelBuddy backend API"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv(
            "TRAVELBUDDY_API_URL",
            "http://localhost:8000"
        )
        self.timeout = 10
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except ConnectionError:
            print(f"Error: Could not connect to API at {self.base_url}")
            return None
        except Timeout:
            print(f"Error: Request to {url} timed out")
            return None
        except RequestException as e:
            print(f"Error: API request failed: {e}")
            return None
    
    def submit_tip(
        self,
        tip_text: str,
        location_name: Optional[str] = None,
        location_country: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        user_id: Optional[int] = None
    ) -> Optional[Dict]:
        """Submit a new tip to the backend"""
        data = {
            "tip_text": tip_text,
            "location_name": location_name,
            "location_country": location_country,
            "latitude": latitude,
            "longitude": longitude,
            "user_id": user_id
        }
        return self._make_request("POST", "/api/tips", data=data)
    
    def get_tips(
        self,
        location_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """Get tips from the backend"""
        params = {
            "limit": limit,
            "offset": offset
        }
        if location_id:
            params["location_id"] = location_id
        if status:
            params["status"] = status
        
        result = self._make_request("GET", "/api/tips", params=params)
        return result if result else []
    
    def get_location_tips(self, location_id: int) -> List[Dict]:
        """Get tips for a specific location"""
        result = self._make_request("GET", f"/api/locations/{location_id}/tips")
        return result if result else []
    
    def get_locations(self) -> List[Dict]:
        """Get all locations"""
        result = self._make_request("GET", "/api/locations")
        return result if result else []
    
    def get_location_by_name(self, name: str, country: str) -> Optional[Dict]:
        """Get location by name and country"""
        locations = self.get_locations()
        for loc in locations:
            if loc.get("name") == name and loc.get("country") == country:
                return loc
        return None

    def search_location(self, name: str, country: str) -> Optional[Dict]:
        """
        Search for a location by name and country using the search endpoint.
        Returns location data or None if not found.
        """
        params = {
            "name": name,
            "country": country
        }
        result = self._make_request("GET", "/api/locations/search", params=params)
        return result

    def get_promoted_tips(
        self,
        location_name: str,
        location_country: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get promoted tips for a location by name and country.
        Returns list of promoted tips ranked by mention count.
        """
        params = {
            "location_name": location_name,
            "location_country": location_country,
            "limit": limit
        }
        result = self._make_request("GET", "/api/promoted-tips", params=params)
        return result if result else []

    def get_location_promoted_tips(
        self,
        location_id: int,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get promoted tips for a location by location ID.
        Returns list of promoted tips ranked by mention count.
        """
        params = {"limit": limit}
        result = self._make_request(
            "GET",
            f"/api/locations/{location_id}/promoted-tips",
            params=params
        )
        return result if result else []


# Global API client instance
_api_client = None


def get_api_client() -> TravelBuddyAPI:
    """Get or create API client instance"""
    global _api_client
    if _api_client is None:
        _api_client = TravelBuddyAPI()
    return _api_client

