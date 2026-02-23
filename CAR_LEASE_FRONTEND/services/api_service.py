"""API service for backend communication."""
import requests
from typing import Optional, Dict, Any, List
import streamlit as st
from config import UPLOAD_ENDPOINT, CHAT_ENDPOINT, MARKET_ANALYSIS_ENDPOINT


class APIService:
    """Service class for all backend API interactions."""
    
    @staticmethod
    def upload_contract(file) -> Dict[str, Any]:
        """
        Upload a contract file to the backend.
        
        Args:
            file: Streamlit UploadedFile object
            
        Returns:
            Dict containing contract_id and combined_data from backend
        """
        try:
            files = {"file": (file.name, file.getvalue(), file.type)}
            response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=120)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error uploading contract: {str(e)}")
            return {}
    
    @staticmethod
    def lookup_vin(vin: str) -> Dict[str, Any]:
        """
        Lookup vehicle details by VIN using NHTSA API directly.
        
        Args:
            vin: 17-digit Vehicle Identification Number
            
        Returns:
            Dict containing vehicle details
        """
        try:
            # Call NHTSA API directly for VIN lookup
            nhtsa_url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"
            response = requests.get(nhtsa_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Parse NHTSA response into structured vehicle data
            results = data.get("Results", [])
            vehicle_data = {"vin": vin}
            
            # NHTSA decodevin API uses "Variable" field with these exact names
            field_mapping = {
                "Make": "make",
                "Model": "model",
                "Model Year": "year",
                "Body Class": "body_class",
                "Vehicle Type": "vehicle_type",
                "Displacement (L)": "engine",
                "Fuel Type - Primary": "fuel_type",
                "Transmission Style": "transmission",
                "Plant Country": "plant_country",
            }
            
            for item in results:
                var_name = item.get("Variable", "")
                value = item.get("Value")
                if var_name in field_mapping and value:
                    vehicle_data[field_mapping[var_name]] = value
            
            return {
                "combined_data": {
                    "vehicle": vehicle_data,
                    "sla": {}
                }
            }
        except requests.exceptions.RequestException as e:
            st.error(f"Error looking up VIN: {str(e)}")
            return {}
    
    @staticmethod
    def get_greeting() -> Dict[str, Any]:
        """
        Get welcome message from chat API.
        
        Returns:
            Dict containing greeting and suggestions
        """
        try:
            payload = {"action": "greeting"}
            response = requests.post(CHAT_ENDPOINT, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "greeting": "I'm your negotiation assistant. How can I help you?",
                "suggestions": []
            }
    
    @staticmethod
    def send_chat_message(
        message: str,
        contract_id: int
    ) -> Dict[str, Any]:
        """
        Send a chat message to the AI negotiation assistant.
        
        Args:
            message: User's message
            contract_id: Contract ID for context
            
        Returns:
            Dict containing AI response
        """
        try:
            payload = {
                "action": "message",
                "contract_id": contract_id,
                "message": message
            }
            response = requests.post(CHAT_ENDPOINT, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with AI assistant: {str(e)}")
            return {"assistant_response": "I'm sorry, I encountered an error. Please try again."}
    
    @staticmethod
    def get_chat_history(contract_id: int) -> Dict[str, Any]:
        """
        Get chat history for a contract.
        
        Args:
            contract_id: Contract ID
            
        Returns:
            Dict containing messages list
        """
        try:
            payload = {
                "action": "history",
                "contract_id": contract_id
            }
            response = requests.post(CHAT_ENDPOINT, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"messages": []}
    
    @staticmethod
    def clear_chat_history(contract_id: int) -> Dict[str, Any]:
        """
        Clear chat history for a contract.
        
        Args:
            contract_id: Contract ID
            
        Returns:
            Dict with deleted count
        """
        try:
            payload = {
                "action": "clear",
                "contract_id": contract_id
            }
            response = requests.post(CHAT_ENDPOINT, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"deleted_count": 0}
    
    @staticmethod
    def get_market_analysis(contract_id: int) -> Dict[str, Any]:
        """
        Get market analysis for a contract.
        
        Args:
            contract_id: Contract ID
            
        Returns:
            Dict containing market analysis data
        """
        try:
            payload = {"contract_id": contract_id}
            response = requests.post(MARKET_ANALYSIS_ENDPOINT, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
