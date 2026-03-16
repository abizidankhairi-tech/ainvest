"""
Image Import Service using Google Gemini Vision
Processes portfolio screenshots from broker apps (IPOT, Stockbit, Ajaib, etc.)
"""
import os
import json
import base64
import time
import re
from typing import Dict, List, Optional, Any
import google.generativeai as genai

# Vision Model Configuration
GEMINI_MODEL = "gemini-2.0-flash"  # Latest fast model
MAX_TOKENS = 4096
TEMPERATURE = 0.1  # Low temperature for more consistent OCR results


class ImageImportService:
    """Service for importing portfolio data from screenshots using Gemini Vision"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
        self.model = None
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
    
    def _get_extraction_prompt(self) -> str:
        """Get the prompt for portfolio extraction"""
        return """You are an expert OCR system specialized in extracting stock portfolio data from Indonesian broker app screenshots.

Your task is to extract all stock holdings from the image and return them in a specific JSON format.

IMPORTANT RULES:
1. Extract ONLY Indonesian stock symbols (IDX stocks, usually 4 letters like BBCA, BBRI, TLKM)
2. Extract the number of shares (lot × 100 = shares, or direct share count)
3. Extract average cost/buy price per share
4. Extract current price if visible
5. Extract P/L (profit/loss) if visible
6. If a value is not clearly visible, use null

COMMON BROKER FORMATS:
- IPOT: Shows symbol, lot, avg price, market price, P/L
- Stockbit: Shows symbol, shares, avg price, current price, gain/loss %
- Ajaib: Shows symbol, lot, buy price, current price, return %
- Bibit Saham: Shows symbol, shares, avg cost, market value

OUTPUT FORMAT (return ONLY this JSON, no other text):
{
    "success": true,
    "broker_detected": "IPOT/Stockbit/Ajaib/Unknown",
    "holdings": [
        {
            "symbol": "BBCA",
            "shares": 100,
            "avg_cost": 9000,
            "current_price": 9500,
            "profit_loss": 50000,
            "profit_loss_pct": 5.56
        }
    ],
    "total_value": 950000,
    "total_profit_loss": 50000,
    "confidence": 0.95,
    "notes": "Any relevant notes about extraction quality"
}

If you cannot extract portfolio data (wrong image type, too blurry, etc.), return:
{
    "success": false,
    "error": "Description of the issue",
    "holdings": [],
    "confidence": 0
}

Be precise with numbers. Indonesian format uses period for thousands (e.g., 9.000 = 9000).
1 lot = 100 shares in Indonesian market."""
    
    def extract_portfolio_from_image(
        self,
        image_data: bytes,
        image_type: str = "image/png"
    ) -> Dict[str, Any]:
        """
        Extract portfolio data from a screenshot image.
        
        Args:
            image_data: Raw image bytes
            image_type: MIME type (image/png, image/jpeg, etc.)
        
        Returns:
            Dict with extracted holdings and metadata
        """
        if not self.model:
            return {
                "success": False,
                "error": "AI service is not configured. Please add GOOGLE_API_KEY.",
                "holdings": [],
                "confidence": 0
            }
        
        start_time = time.time()
        
        try:
            # Create image part for Gemini
            image_part = {
                "mime_type": image_type,
                "data": image_data
            }
            
            # Generate content with image
            response = self.model.generate_content(
                [self._get_extraction_prompt(), image_part],
                generation_config=genai.GenerationConfig(
                    max_output_tokens=MAX_TOKENS,
                    temperature=TEMPERATURE
                )
            )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            response_text = response.text
            
            # Parse JSON from response
            result = self._parse_extraction_response(response_text)
            result["response_time_ms"] = response_time_ms
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing image: {str(e)}",
                "holdings": [],
                "confidence": 0,
                "response_time_ms": int((time.time() - start_time) * 1000)
            }
    
    def _parse_extraction_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate the AI response"""
        try:
            # Find JSON in response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if not json_match:
                return {
                    "success": False,
                    "error": "Could not parse response from AI",
                    "holdings": [],
                    "confidence": 0,
                    "raw_response": response_text
                }
            
            result = json.loads(json_match.group())
            
            # Validate and clean holdings
            if "holdings" in result and isinstance(result["holdings"], list):
                cleaned_holdings = []
                for h in result["holdings"]:
                    cleaned = self._clean_holding(h)
                    if cleaned:
                        cleaned_holdings.append(cleaned)
                result["holdings"] = cleaned_holdings
            
            return result
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON response: {str(e)}",
                "holdings": [],
                "confidence": 0,
                "raw_response": response_text
            }
    
    def _clean_holding(self, holding: Dict) -> Optional[Dict]:
        """Clean and validate a single holding"""
        try:
            symbol = holding.get("symbol", "").upper().strip()
            
            # Validate symbol (should be 4 letters for IDX)
            if not symbol or len(symbol) < 3 or len(symbol) > 5:
                return None
            
            # Clean numeric values
            shares = self._parse_number(holding.get("shares"))
            avg_cost = self._parse_number(holding.get("avg_cost"))
            
            if shares is None or shares <= 0:
                return None
            if avg_cost is None or avg_cost <= 0:
                return None
            
            return {
                "symbol": symbol,
                "shares": int(shares),
                "avg_cost": float(avg_cost),
                "current_price": self._parse_number(holding.get("current_price")),
                "profit_loss": self._parse_number(holding.get("profit_loss")),
                "profit_loss_pct": self._parse_number(holding.get("profit_loss_pct"))
            }
            
        except Exception:
            return None
    
    def _parse_number(self, value: Any) -> Optional[float]:
        """Parse a number from various formats"""
        if value is None:
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove common formatting
            cleaned = value.strip()
            cleaned = cleaned.replace(",", "")  # Remove commas
            cleaned = cleaned.replace(" ", "")
            cleaned = cleaned.replace("Rp", "")
            cleaned = cleaned.replace("IDR", "")
            cleaned = cleaned.replace("%", "")
            cleaned = cleaned.replace("+", "")
            cleaned = cleaned.replace("(", "-").replace(")", "")  # Handle (negative)
            
            # Handle Indonesian thousands separator (period)
            # If there's a period and it's followed by 3 digits at the end, it's decimal
            # Otherwise periods are thousands separators
            if re.match(r'^[\d.]+$', cleaned):
                parts = cleaned.split('.')
                if len(parts) > 1 and len(parts[-1]) == 3 and len(parts) > 2:
                    # Multiple periods = thousands separator
                    cleaned = cleaned.replace(".", "")
                elif len(parts) == 2 and len(parts[-1]) == 3:
                    # Could be either, assume thousands separator for Indonesian
                    cleaned = cleaned.replace(".", "")
            
            try:
                return float(cleaned)
            except ValueError:
                return None
        
        return None
    
    def validate_holdings(self, holdings: List[Dict]) -> Dict[str, Any]:
        """
        Validate extracted holdings and check for issues.
        
        Args:
            holdings: List of extracted holdings
        
        Returns:
            Validation result with warnings and suggestions
        """
        warnings = []
        suggestions = []
        valid_holdings = []
        
        seen_symbols = set()
        
        for h in holdings:
            symbol = h.get("symbol", "")
            
            # Check for duplicates
            if symbol in seen_symbols:
                warnings.append(f"Duplicate symbol found: {symbol}")
                continue
            seen_symbols.add(symbol)
            
            # Validate shares
            shares = h.get("shares", 0)
            if shares < 100:
                warnings.append(f"{symbol}: Shares ({shares}) seems low. IDX minimum is 100 (1 lot)")
            
            # Validate avg_cost
            avg_cost = h.get("avg_cost", 0)
            if avg_cost < 50:
                warnings.append(f"{symbol}: Average cost (Rp {avg_cost}) seems too low")
            elif avg_cost > 1000000:
                warnings.append(f"{symbol}: Average cost (Rp {avg_cost:,.0f}) seems very high")
            
            valid_holdings.append(h)
        
        if not valid_holdings:
            suggestions.append("No valid holdings extracted. Please try with a clearer screenshot.")
        elif len(valid_holdings) < 3:
            suggestions.append("Few holdings extracted. Make sure the entire portfolio is visible in the screenshot.")
        
        return {
            "valid": len(warnings) == 0,
            "holdings_count": len(valid_holdings),
            "warnings": warnings,
            "suggestions": suggestions,
            "holdings": valid_holdings
        }
    
    def preview_import(
        self,
        image_data: bytes,
        image_type: str = "image/png"
    ) -> Dict[str, Any]:
        """
        Process image and return preview of what will be imported.
        User can review and confirm before actual import.
        
        Args:
            image_data: Raw image bytes
            image_type: MIME type
        
        Returns:
            Preview data with holdings and validation
        """
        # Extract from image
        extraction = self.extract_portfolio_from_image(image_data, image_type)
        
        if not extraction.get("success"):
            return extraction
        
        # Validate holdings
        validation = self.validate_holdings(extraction.get("holdings", []))
        
        return {
            "success": True,
            "broker_detected": extraction.get("broker_detected", "Unknown"),
            "holdings": validation["holdings"],
            "holdings_count": validation["holdings_count"],
            "warnings": validation["warnings"],
            "suggestions": validation["suggestions"],
            "total_value": extraction.get("total_value"),
            "confidence": extraction.get("confidence", 0),
            "response_time_ms": extraction.get("response_time_ms", 0),
            "ready_to_import": validation["valid"] and validation["holdings_count"] > 0
        }


# Singleton instance
image_import_service = ImageImportService()
