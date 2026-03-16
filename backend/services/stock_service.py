import yfinance as yf
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import redis
import json
import os
import time

# Cache settings
CACHE_TTL = 60  # 1 minute for prices
CACHE_TTL_FALLBACK = 300  # 5 minutes for fallback

# TradingView API
TRADINGVIEW_URL = "https://scanner.tradingview.com/indonesia/scan"


class StockService:
    """Service for fetching Indonesian stock prices using TradingView"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        try:
            self.redis_client = redis.from_url(self.redis_url)
        except:
            self.redis_client = None
        
        # Session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def _get_cache_key(self, symbol: str) -> str:
        """Generate cache key for a symbol"""
        return f"stock_price:{symbol.upper()}"
    
    def _get_from_cache(self, symbol: str) -> Optional[Dict]:
        """Get price data from cache"""
        if not self.redis_client:
            return None
        try:
            data = self.redis_client.get(self._get_cache_key(symbol))
            if data:
                return json.loads(data)
        except:
            pass
        return None
    
    def _set_cache(self, symbol: str, data: Dict, ttl: int = CACHE_TTL):
        """Set price data in cache"""
        if not self.redis_client:
            return
        try:
            self.redis_client.setex(
                self._get_cache_key(symbol),
                ttl,
                json.dumps(data)
            )
        except:
            pass
    
    def _fetch_from_tradingview(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Fetch prices from TradingView Scanner API.
        This is the most reliable free source for IDX stocks.
        """
        results = {}
        
        # Format symbols for TradingView (IDX:BBCA format)
        tv_symbols = [f"IDX:{s.upper().replace('.JK', '')}" for s in symbols]
        
        payload = {
            "symbols": {"tickers": tv_symbols},
            "columns": [
                "close",           # Current/Last price
                "change",          # Change percentage
                "open",            # Open price
                "high",            # Day high
                "low",             # Day low
                "volume",          # Volume
                "Perf.W",          # Weekly performance
                "Perf.1M",         # Monthly performance
                "name",            # Company name
                "sector"           # Sector
            ]
        }
        
        try:
            response = self.session.post(
                TRADINGVIEW_URL,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('data', []):
                    # Parse symbol (IDX:BBCA -> BBCA)
                    raw_symbol = item.get('s', '')
                    symbol = raw_symbol.replace('IDX:', '')
                    
                    # Parse data columns
                    d = item.get('d', [])
                    if len(d) >= 6:
                        close = d[0] if d[0] else 0
                        change_pct = d[1] if d[1] else 0
                        open_price = d[2] if d[2] else close
                        high = d[3] if d[3] else close
                        low = d[4] if d[4] else close
                        volume = int(d[5]) if d[5] else 0
                        
                        # Calculate change from percentage
                        prev_close = close / (1 + change_pct/100) if change_pct != -100 else close
                        change = close - prev_close
                        
                        company_name = d[8] if len(d) > 8 and d[8] else symbol
                        sector = d[9] if len(d) > 9 and d[9] else "Unknown"
                        
                        results[symbol] = {
                            "symbol": symbol,
                            "price": round(close, 2),
                            "open": round(open_price, 2) if open_price else None,
                            "high": round(high, 2) if high else None,
                            "low": round(low, 2) if low else None,
                            "close": round(prev_close, 2),
                            "volume": volume,
                            "change": round(change, 2),
                            "change_pct": round(change_pct, 2),
                            "timestamp": datetime.now().isoformat(),
                            "source": "TradingView",
                            "company_name": company_name,
                            "sector": sector
                        }
            
        except Exception as e:
            print(f"TradingView API error: {e}")
        
        return results
    
    def _fetch_from_yfinance(self, symbol: str) -> Optional[Dict]:
        """
        Fallback to yfinance for historical data.
        """
        base_symbol = symbol.upper().replace(".JK", "")
        idx_symbol = f"{base_symbol}.JK"
        
        try:
            ticker = yf.Ticker(idx_symbol)
            hist = ticker.history(period="5d")
            
            if not hist.empty:
                latest = hist.iloc[-1]
                prev_close = hist.iloc[-2]['Close'] if len(hist) > 1 else latest['Close']
                current_price = float(latest['Close'])
                
                change = current_price - prev_close
                change_pct = (change / prev_close * 100) if prev_close else 0
                
                return {
                    "symbol": base_symbol,
                    "price": round(current_price, 2),
                    "open": round(float(latest['Open']), 2),
                    "high": round(float(latest['High']), 2),
                    "low": round(float(latest['Low']), 2),
                    "close": round(float(prev_close), 2),
                    "volume": int(latest['Volume']),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                    "timestamp": datetime.now().isoformat(),
                    "source": "yfinance",
                    "company_name": base_symbol
                }
            
            return None
            
        except Exception as e:
            print(f"yfinance error for {symbol}: {e}")
            return None
    
    def get_stock_price(self, symbol: str, force_refresh: bool = False) -> Optional[Dict]:
        """
        Get current stock price for an Indonesian stock.
        Uses TradingView as primary source.
        """
        base_symbol = symbol.upper().replace(".JK", "")
        
        # Check cache first
        if not force_refresh:
            cached = self._get_from_cache(base_symbol)
            if cached:
                return cached
        
        # Try TradingView first
        results = self._fetch_from_tradingview([base_symbol])
        
        if base_symbol in results:
            result = results[base_symbol]
            self._set_cache(base_symbol, result, CACHE_TTL)
            return result
        
        # Fallback to yfinance
        result = self._fetch_from_yfinance(base_symbol)
        
        if result:
            self._set_cache(base_symbol, result, CACHE_TTL_FALLBACK)
            return result
        
        return None
    
    def get_multiple_prices(self, symbols: List[str], force_refresh: bool = False) -> Dict[str, Dict]:
        """
        Get prices for multiple stocks efficiently.
        Uses batch request to TradingView.
        """
        results = {}
        symbols_to_fetch = []
        
        # Clean symbols
        clean_symbols = [s.upper().replace(".JK", "") for s in symbols]
        
        # Check cache first
        if not force_refresh:
            for symbol in clean_symbols:
                cached = self._get_from_cache(symbol)
                if cached:
                    results[symbol] = cached
                else:
                    symbols_to_fetch.append(symbol)
        else:
            symbols_to_fetch = clean_symbols
        
        # Fetch missing from TradingView (batch request)
        if symbols_to_fetch:
            tv_results = self._fetch_from_tradingview(symbols_to_fetch)
            
            for symbol, data in tv_results.items():
                self._set_cache(symbol, data, CACHE_TTL)
                results[symbol] = data
            
            # For any still missing, try yfinance
            still_missing = [s for s in symbols_to_fetch if s not in tv_results]
            for symbol in still_missing:
                yf_result = self._fetch_from_yfinance(symbol)
                if yf_result:
                    self._set_cache(symbol, yf_result, CACHE_TTL_FALLBACK)
                    results[symbol] = yf_result
        
        return results
    
    def refresh_all_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """Force refresh prices for all symbols."""
        return self.get_multiple_prices(symbols, force_refresh=True)
    
    def get_stock_history(self, symbol: str, period: str = "1mo") -> Optional[List[Dict]]:
        """
        Get historical price data for a stock.
        Uses yfinance for historical data.
        """
        base_symbol = symbol.upper().replace(".JK", "")
        idx_symbol = f"{base_symbol}.JK"
        
        try:
            ticker = yf.Ticker(idx_symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            result = []
            for date, row in hist.iterrows():
                result.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(row['Open'], 2),
                    "high": round(row['High'], 2),
                    "low": round(row['Low'], 2),
                    "close": round(row['Close'], 2),
                    "volume": int(row['Volume'])
                })
            
            return result
            
        except Exception as e:
            print(f"Error fetching history for {symbol}: {e}")
            return None
    
    def search_stocks(self, query: str) -> List[Dict]:
        """Search for Indonesian stocks by symbol or name."""
        idx_stocks = {
            "ACES": "Ace Hardware Indonesia",
            "ADRO": "Adaro Energy",
            "AKRA": "AKR Corporindo",
            "AMMN": "Amman Mineral Internasional",
            "ANTM": "Aneka Tambang",
            "ASII": "Astra International",
            "BBCA": "Bank Central Asia",
            "BBNI": "Bank Negara Indonesia",
            "BBRI": "Bank Rakyat Indonesia",
            "BMRI": "Bank Mandiri",
            "BREN": "Barito Renewables Energy",
            "BRPT": "Barito Pacific",
            "BUKA": "Bukalapak",
            "CPIN": "Charoen Pokphand Indonesia",
            "CPRO": "Central Proteinaprima",
            "CUAN": "Petrindo Jaya Kreasi",
            "EMTK": "Elang Mahkota Teknologi",
            "ERAA": "Erajaya Swasembada",
            "EXCL": "XL Axiata",
            "GGRM": "Gudang Garam",
            "GOTO": "GoTo Gojek Tokopedia",
            "HMSP": "HM Sampoerna",
            "ICBP": "Indofood CBP",
            "INCO": "Vale Indonesia",
            "INDF": "Indofood Sukses Makmur",
            "INKP": "Indah Kiat Pulp & Paper",
            "ISAT": "Indosat Ooredoo",
            "KLBF": "Kalbe Farma",
            "MAPI": "Mitra Adiperkasa",
            "MDKA": "Merdeka Copper Gold",
            "MEDC": "Medco Energi Internasional",
            "PGAS": "Perusahaan Gas Negara",
            "PTBA": "Bukit Asam",
            "SCMA": "Surya Citra Media",
            "SMGR": "Semen Indonesia",
            "TBIG": "Tower Bersama Infrastructure",
            "TLKM": "Telkom Indonesia",
            "TOWR": "Sarana Menara Nusantara",
            "TPIA": "Chandra Asri Pacific",
            "ULTJ": "Ultra Jaya Milk Industry",
            "UNTR": "United Tractors",
            "UNVR": "Unilever Indonesia",
        }
        
        query = query.upper()
        results = []
        
        for symbol, name in idx_stocks.items():
            if query in symbol or query.lower() in name.lower():
                results.append({
                    "symbol": symbol,
                    "name": name,
                    "exchange": "IDX"
                })
        
        return results[:10]


# Singleton instance
stock_service = StockService()
