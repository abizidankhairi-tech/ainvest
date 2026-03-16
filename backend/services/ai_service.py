import os
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from groq import Groq

# AI Configuration
GROQ_MODEL = "llama-3.3-70b-versatile"  # or "llama-3.1-70b-versatile"
MAX_TOKENS = 2048
TEMPERATURE = 0.7


class AIService:
    """AI Service using Groq (Llama 3.3 70B) for portfolio analysis and chat"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = None
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
    
    def _get_system_prompt(self, context: Dict = None) -> str:
        """Generate system prompt with portfolio context"""
        base_prompt = """You are InvestAI, an expert AI assistant for Indonesian stock market investing. 
You specialize in:
- IDX (Indonesia Stock Exchange) stock analysis
- Portfolio management and optimization
- Technical and fundamental analysis
- Risk assessment and diversification
- Entry and exit strategies
- Indonesian market insights

Key guidelines:
1. Always provide actionable advice with specific reasoning
2. Consider Indonesian market conditions and regulations
3. Use IDR (Indonesian Rupiah) for currency
4. Reference specific stocks by their IDX ticker (e.g., BBCA, BBRI, TLKM)
5. Be balanced - mention both opportunities and risks
6. Never guarantee returns or make definitive predictions
7. Encourage diversification and risk management
8. Be concise but thorough

When analyzing portfolios:
- Calculate key metrics (diversification, sector allocation, risk exposure)
- Identify potential issues (concentration risk, underperforming stocks)
- Suggest improvements based on user's apparent risk profile
- Provide specific entry/exit levels when relevant"""

        if context:
            portfolio_info = ""
            if context.get('holdings'):
                holdings = context['holdings']
                total_value = sum(h.get('market_value', 0) for h in holdings)
                
                portfolio_info = f"""

CURRENT PORTFOLIO CONTEXT:
- Total Holdings: {len(holdings)} stocks
- Total Portfolio Value: Rp {total_value:,.0f}

Holdings Detail:
"""
                for h in holdings:
                    symbol = h.get('symbol', 'N/A')
                    shares = h.get('shares', 0)
                    avg_cost = h.get('avg_cost', 0)
                    current_price = h.get('current_price', avg_cost)
                    market_value = h.get('market_value', shares * current_price)
                    gain_loss_pct = h.get('gain_loss_pct', 0)
                    sector = h.get('sector', 'Unknown')
                    
                    portfolio_info += f"- {symbol}: {shares} shares @ Rp {avg_cost:,.0f} avg | Current: Rp {current_price:,.0f} | Value: Rp {market_value:,.0f} | P/L: {gain_loss_pct:+.2f}% | Sector: {sector}\n"
                
                # Add sector breakdown
                sectors = {}
                for h in holdings:
                    sector = h.get('sector', 'Unknown')
                    value = h.get('market_value', 0)
                    sectors[sector] = sectors.get(sector, 0) + value
                
                if sectors and total_value > 0:
                    portfolio_info += "\nSector Allocation:\n"
                    for sector, value in sorted(sectors.items(), key=lambda x: x[1], reverse=True):
                        pct = (value / total_value) * 100
                        portfolio_info += f"- {sector}: {pct:.1f}%\n"
            
            return base_prompt + portfolio_info
        
        return base_prompt
    
    def chat(
        self,
        message: str,
        conversation_history: List[Dict] = None,
        portfolio_context: Dict = None
    ) -> Dict:
        """
        Chat with the AI about investing.
        
        Args:
            message: User's message
            conversation_history: Previous messages in the conversation
            portfolio_context: Current portfolio data for context
        
        Returns:
            Dict with response, tokens_used, response_time_ms
        """
        if not self.client:
            return {
                "response": "AI service is not configured. Please add your GROQ_API_KEY to the environment.",
                "tokens_used": 0,
                "response_time_ms": 0,
                "error": True
            }
        
        start_time = time.time()
        
        try:
            # Build messages
            messages = [
                {"role": "system", "content": self._get_system_prompt(portfolio_context)}
            ]
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                "response": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "response_time_ms": response_time_ms,
                "error": False
            }
            
        except Exception as e:
            return {
                "response": f"Error communicating with AI: {str(e)}",
                "tokens_used": 0,
                "response_time_ms": int((time.time() - start_time) * 1000),
                "error": True
            }
    
    def analyze_portfolio(self, holdings: List[Dict]) -> Dict:
        """
        Get AI analysis of the entire portfolio.
        
        Args:
            holdings: List of holdings with current prices
        
        Returns:
            Comprehensive portfolio analysis
        """
        if not holdings:
            return {
                "response": "No holdings to analyze. Add some stocks to your portfolio first!",
                "tokens_used": 0,
                "response_time_ms": 0
            }
        
        analysis_prompt = """Please provide a comprehensive analysis of my portfolio including:

1. **Portfolio Health Score** (1-10) with brief justification
2. **Diversification Analysis**
   - Sector concentration risks
   - Stock concentration risks
   - Suggestions for better diversification
3. **Performance Analysis**
   - Top performers and why they're doing well
   - Underperformers and potential reasons
   - Overall portfolio momentum
4. **Risk Assessment**
   - Key risks in current holdings
   - Market condition considerations
   - Hedging suggestions if needed
5. **Actionable Recommendations**
   - Stocks to consider adding (with brief reasoning)
   - Positions to consider reducing (with brief reasoning)
   - Rebalancing suggestions
6. **Key Metrics Summary**
   - Estimated portfolio beta
   - Dividend yield estimate
   - Growth vs value tilt

Please be specific and actionable in your analysis."""

        return self.chat(
            message=analysis_prompt,
            portfolio_context={"holdings": holdings}
        )
    
    def get_stock_analysis(self, symbol: str, holdings: List[Dict] = None) -> Dict:
        """
        Get AI analysis for a specific stock.
        
        Args:
            symbol: Stock ticker symbol
            holdings: Current portfolio for context
        
        Returns:
            Stock analysis with buy/sell/hold recommendation
        """
        analysis_prompt = f"""Please analyze {symbol} stock and provide:

1. **Quick Overview**
   - What the company does
   - Key business segments
   - Market position in Indonesia

2. **Investment Thesis**
   - Bull case (reasons to buy)
   - Bear case (reasons to avoid)
   - Key catalysts to watch

3. **Technical Levels** (approximate based on your knowledge)
   - Key support levels
   - Key resistance levels
   - Suggested entry zones

4. **Recommendation**
   - BUY / HOLD / SELL rating
   - Confidence level (High/Medium/Low)
   - Suggested position size (as % of portfolio)
   - Time horizon (short/medium/long term)

5. **Risk Factors**
   - Company-specific risks
   - Sector risks
   - Macro risks

Please be specific and actionable."""

        context = {"holdings": holdings} if holdings else None
        return self.chat(message=analysis_prompt, portfolio_context=context)
    
    def get_entry_strategy(self, symbol: str, capital: float, holdings: List[Dict] = None) -> Dict:
        """
        Get AI-suggested entry strategy for a stock.
        
        Args:
            symbol: Stock ticker symbol
            capital: Amount to invest (in IDR)
            holdings: Current portfolio for context
        
        Returns:
            Entry strategy with buy zones
        """
        strategy_prompt = f"""I want to invest Rp {capital:,.0f} in {symbol}. Please provide an entry strategy:

1. **Entry Strategy Type**
   - Lump sum vs Dollar Cost Averaging recommendation
   - Reasoning for the approach

2. **Buy Zones** (3 zones recommended)
   - Zone 1 (Aggressive): Price range and allocation %
   - Zone 2 (Moderate): Price range and allocation %
   - Zone 3 (Conservative): Price range and allocation %

3. **Position Sizing**
   - Recommended number of shares per zone
   - Total position as % of my portfolio

4. **Timing Considerations**
   - Best time/conditions to enter
   - Events to wait for or avoid

5. **Stop Loss**
   - Suggested stop loss level
   - Maximum acceptable loss %

6. **Exit Targets**
   - Take profit level 1 (partial exit)
   - Take profit level 2 (partial exit)
   - Ultimate target

Please provide specific price levels and actionable advice."""

        context = {"holdings": holdings} if holdings else None
        return self.chat(message=strategy_prompt, portfolio_context=context)
    
    def get_quick_insights(self, holdings: List[Dict]) -> List[Dict]:
        """
        Get quick AI insights for dashboard display.
        
        Args:
            holdings: Current portfolio holdings
        
        Returns:
            List of insight objects with type, title, description
        """
        if not holdings:
            return [{
                "type": "info",
                "title": "Get Started",
                "description": "Add holdings to your portfolio to receive AI-powered insights and recommendations."
            }]
        
        insights_prompt = """Based on my current portfolio, provide exactly 3 quick insights in JSON format.
Each insight should have: type (warning/opportunity/info), title (max 5 words), description (max 20 words).

Example format:
[
  {"type": "warning", "title": "High Concentration Risk", "description": "BBCA is 45% of portfolio. Consider diversifying to reduce risk."},
  {"type": "opportunity", "title": "Banking Sector Strong", "description": "Your banking stocks are outperforming. Consider adding more exposure."},
  {"type": "info", "title": "Dividend Season Coming", "description": "Several holdings announce dividends in Q2. Hold for income."}
]

Return ONLY the JSON array, no other text."""

        result = self.chat(
            message=insights_prompt,
            portfolio_context={"holdings": holdings}
        )
        
        try:
            # Try to parse JSON from response
            response_text = result.get("response", "[]")
            # Find JSON array in response
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start != -1 and end > start:
                json_str = response_text[start:end]
                insights = json.loads(json_str)
                return insights[:3]  # Return max 3 insights
        except:
            pass
        
        # Fallback if JSON parsing fails
        return [{
            "type": "info",
            "title": "Analysis Available",
            "description": "Click 'Get AI Analysis' for detailed portfolio insights."
        }]


# Singleton instance
ai_service = AIService()
