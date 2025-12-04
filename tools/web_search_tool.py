from typing import List, Dict


class WebSearchTool:


    def __init__(self) -> None:
        
        self._fake_web_db: Dict[str, Dict[str, str]] = {
            "nitrate pollution": {
                "title": "Understanding Nitrate Pollution in Water",
                "snippet": (
                    "Nitrate pollution occurs when excess nitrogen from fertilizers "
                    "and wastewater enters rivers, lakes, or groundwater. It can "
                    "cause algal blooms and reduce oxygen levels, harming fish."
                ),
                "url": "https://example.com/nitrate-pollution"
            },
            "water quality": {
                "title": "Key Indicators of Water Quality",
                "snippet": (
                    "Water quality is described using indicators such as pH, "
                    "turbidity, dissolved oxygen, temperature, and contaminants "
                    "like nitrates or heavy metals."
                ),
                "url": "https://example.com/water-quality-indicators"
            },
            "irrigation water": {
                "title": "Requirements for Good Irrigation Water",
                "snippet": (
                    "Good irrigation water typically has low salinity, low nitrate "
                    "levels, and minimal heavy metals to avoid soil and crop damage."
                ),
                "url": "https://example.com/irrigation-water-standards"
            },
        }

    def search(self, query: str) -> List[Dict[str, str]]:
       
        query_lower = query.lower()
        results: List[Dict[str, str]] = []

        for key, value in self._fake_web_db.items():
            if key in query_lower:
                results.append(value)

        if not results:
            results.append({
                "title": "General Information about Water Pollution",
                "snippet": (
                    "Water pollution impacts ecosystems, human health, and agriculture. "
                    "Common pollutants include nutrients (like nitrates), industrial "
                    "chemicals, and pathogens from wastewater."
                ),
                "url": "https://example.com/general-water-pollution"
            })

        return results
