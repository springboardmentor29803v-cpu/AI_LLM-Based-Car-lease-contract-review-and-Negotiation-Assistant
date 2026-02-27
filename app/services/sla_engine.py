from app.model_tables.sla import SLAData
from app.services.llm_extractor import extract_with_llm
from app.services.regex_extractor import extract_vehicle_fields


def hybrid_extract(text: str) -> SLAData:
    regex_data = extract_vehicle_fields(text)

    missing = [k for k, v in regex_data.items() if v is None]

    if len(missing) >= 3:
        llm_data = extract_with_llm(text)

        for key in regex_data:
            if regex_data[key] is None and key in llm_data:
                regex_data[key] = llm_data[key]

        method = "hybrid_llm_fallback"
    else:
        method = "regex_only"

    confidence = 100 - (len(missing) * 8)

    return SLAData(
        **regex_data,
        extraction_method=method,
        confidence_score=max(confidence, 50)
    )