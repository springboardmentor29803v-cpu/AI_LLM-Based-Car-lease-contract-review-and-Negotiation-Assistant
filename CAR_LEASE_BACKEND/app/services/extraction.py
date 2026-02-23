import os
import re
import requests
from typing import Optional, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from pdf2image import convert_from_path
import pytesseract

# NHTSA VIN Decode API endpoint
NHTSA_API_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues"


def extract_vin_from_text(raw_text: str) -> Optional[str]:
    """
    Extract VIN (Vehicle Identification Number) from raw contract text.
    VIN is 17 characters, excluding I, O, Q.
    
    Args:
        raw_text: Raw text extracted from PDF
        
    Returns:
        VIN string if found, None otherwise
    """
    if not raw_text:
        return None
    
    # VIN pattern: 17 alphanumeric characters, excluding I, O, Q
    # Can be preceded by "VIN:", "VIN ", "Vehicle Identification Number", etc.
    vin_pattern = r'\b([A-HJ-NPR-Z0-9]{17})\b'
    
    # First try to find VIN near keywords
    keyword_patterns = [
        r'VIN[:\s]*([A-HJ-NPR-Z0-9]{17})',
        r'Vehicle\s*Identification\s*Number[:\s]*([A-HJ-NPR-Z0-9]{17})',
        r'V\.?I\.?N\.?[:\s]*([A-HJ-NPR-Z0-9]{17})',
    ]
    
    for pattern in keyword_patterns:
        match = re.search(pattern, raw_text, re.IGNORECASE)
        if match:
            vin = match.group(1).upper()
            if _is_valid_vin(vin):
                return vin
    
    # Fallback: find any 17-character alphanumeric string (excluding I, O, Q)
    matches = re.findall(vin_pattern, raw_text, re.IGNORECASE)
    for match in matches:
        vin = match.upper()
        if _is_valid_vin(vin):
            return vin
    
    return None


def _is_valid_vin(vin: str) -> bool:
    """
    Basic VIN validation.
    
    Args:
        vin: VIN string to validate
        
    Returns:
        True if VIN appears valid
    """
    if len(vin) != 17:
        return False
    
    # VIN should not contain I, O, Q
    if any(c in vin for c in 'IOQ'):
        return False
    
    # VIN should be alphanumeric
    if not vin.isalnum():
        return False
    
    return True


def fetch_vehicle_data_from_nhtsa(vin: str) -> Dict[str, Any]:
    """
    Call NHTSA VIN Decode API to fetch vehicle details.
    
    Args:
        vin: Valid 17-character VIN
        
    Returns:
        Dictionary containing vehicle details (make, model, year, recalls info)
    """
    if not vin or not _is_valid_vin(vin):
        return {
            "error": "Invalid or missing VIN",
            "vin": vin,
            "make": None,
            "model": None,
            "year": None,
            "vehicle_type": None,
            "fuel_type": None,
            "engine": None,
            "recalls": None
        }
    
    try:
        # Call NHTSA Decode API
        response = requests.get(
            f"{NHTSA_API_URL}/{vin}",
            params={"format": "json"},
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        results = data.get("Results", [{}])[0] if data.get("Results") else {}
        
        vehicle_info = {
            "vin": vin,
            "make": results.get("Make") or None,
            "model": results.get("Model") or None,
            "year": results.get("ModelYear") or None,
            "vehicle_type": results.get("VehicleType") or None,
            "body_class": results.get("BodyClass") or None,
            "fuel_type": results.get("FuelTypePrimary") or None,
            "engine": results.get("DisplacementL") or None,
            "transmission": results.get("TransmissionStyle") or None,
            "drive_type": results.get("DriveType") or None,
            "doors": results.get("Doors") or None,
            "plant_country": results.get("PlantCountry") or None,
            "error_code": results.get("ErrorCode"),
            "error_text": results.get("ErrorText") if results.get("ErrorCode") != "0" else None
        }
        
        # Fetch recalls separately
        recalls = fetch_recalls_for_vin(vin)
        vehicle_info["recalls"] = recalls
        
        return vehicle_info
        
    except requests.RequestException as e:
        return {
            "error": f"NHTSA API request failed: {str(e)}",
            "vin": vin,
            "make": None,
            "model": None,
            "year": None,
            "vehicle_type": None,
            "fuel_type": None,
            "engine": None,
            "recalls": None
        }


def fetch_recalls_for_vin(vin: str) -> Optional[list]:
    """
    Fetch recall information for a VIN from NHTSA.
    
    Args:
        vin: Valid 17-character VIN
        
    Returns:
        List of recall records or None if no recalls/error
    """
    try:
        recall_url = f"https://api.nhtsa.gov/recalls/recallsByVehicle?vin={vin}"
        response = requests.get(recall_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        recalls = data.get("results", [])
        
        if not recalls:
            return None
        
        # Extract relevant recall info
        recall_list = []
        for recall in recalls:
            recall_list.append({
                "campaign_number": recall.get("NHTSACampaignNumber"),
                "component": recall.get("Component"),
                "summary": recall.get("Summary"),
                "consequence": recall.get("Consequence"),
                "remedy": recall.get("Remedy"),
                "manufacturer": recall.get("Manufacturer")
            })
        
        return recall_list if recall_list else None
        
    except requests.RequestException:
        return None


def combine_sla_and_vehicle_data(
    sla_data: Dict[str, Any],
    vehicle_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Combine SLA extracted data with vehicle data from NHTSA.
    
    Args:
        sla_data: Extracted SLA fields from contract
        vehicle_data: Vehicle info from NHTSA API
        
    Returns:
        Combined dictionary with both SLA and vehicle data
    """
    return {
        "sla": sla_data,
        "vehicle": vehicle_data,
        "combined_at": None  # Will be set by the route
    }

def extract_text_with_langchain(file_path: str):
    """
    Extract text from PDF using LangChain PyPDFLoader.
    If extraction is empty, fallback to OCR using pdf2image + pytesseract.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        List of Document objects with page_content
    """
    docs = []
    
    try:
        # Step 1: Try LangChain PyPDFLoader
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        
        # Check if extraction is empty
        raw_text = "\n".join(d.page_content for d in docs)
        
        if not raw_text.strip():
            print("⚠️  PyPDFLoader returned empty text, attempting OCR fallback...")
            docs = ocr_fallback(file_path)
        else:
            print(f"✓ Extracted {len(docs)} pages via PyPDFLoader")
            
    except Exception as e:
        print(f"⚠️  PyPDFLoader failed: {e}, attempting OCR fallback...")
        docs = ocr_fallback(file_path)
    
    return docs


def ocr_fallback(file_path: str):
    """
    OCR fallback: Convert PDF to images using pdf2image and OCR with pytesseract.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        List of Document objects with page_content from OCR
    """
    docs = []
    
    try:
        # Convert PDF to images
        images = convert_from_path(file_path)
        print(f"✓ Converted PDF to {len(images)} images")
        
        # OCR each page
        for idx, image in enumerate(images, 1):
            ocr_text = pytesseract.image_to_string(image)
            doc = Document(page_content=ocr_text)
            docs.append(doc)
        
        print(f"✓ OCR completed: {len(docs)} pages extracted")
        
    except Exception as e:
        print(f"❌ OCR fallback failed: {e}")
        # Return empty document to prevent crash
        docs = [Document(page_content="")]
    
    return docs
