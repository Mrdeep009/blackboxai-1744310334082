import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time
import random
from ..utils.logger import get_logger

class WebScraper:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Add delay between requests to be respectful to websites
        self.min_delay = 1
        self.max_delay = 3

    def _get_random_delay(self) -> float:
        """Get random delay between requests"""
        return random.uniform(self.min_delay, self.max_delay)

    def _make_request(self, url: str) -> Optional[str]:
        """
        Make HTTP request with error handling and retries
        
        Args:
            url (str): URL to request
            
        Returns:
            Optional[str]: HTML content if successful, None otherwise
        """
        try:
            time.sleep(self._get_random_delay())
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def get_stock_data(self, symbol: str) -> Optional[Dict]:
        """
        Get stock data from multiple sources
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Optional[Dict]: Stock data if successful, None otherwise
        """
        try:
            # Get data from Yahoo Finance
            yahoo_data = self._scrape_yahoo_finance(symbol)
            if not yahoo_data:
                return None

            # Get data from MarketWatch
            market_watch_data = self._scrape_market_watch(symbol)

            # Combine data from different sources
            return {
                "price": yahoo_data.get("price"),
                "change": yahoo_data.get("change"),
                "volume": yahoo_data.get("volume"),
                "market_cap": market_watch_data.get("market_cap") if market_watch_data else None,
                "pe_ratio": market_watch_data.get("pe_ratio") if market_watch_data else None,
                "52w_high": yahoo_data.get("52w_high"),
                "52w_low": yahoo_data.get("52w_low")
            }

        except Exception as e:
            self.logger.error(f"Error getting stock data for {symbol}: {str(e)}")
            return None

    def _scrape_yahoo_finance(self, symbol: str) -> Optional[Dict]:
        """
        Scrape stock data from Yahoo Finance
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Optional[Dict]: Stock data if successful, None otherwise
        """
        try:
            url = f"https://finance.yahoo.com/quote/{symbol}"
            html = self._make_request(url)
            if not html:
                return None

            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract price
            price_element = soup.find('fin-streamer', {'data-symbol': symbol, 'data-field': 'regularMarketPrice'})
            price = float(price_element['value']) if price_element else None

            # Extract change
            change_element = soup.find('fin-streamer', {'data-symbol': symbol, 'data-field': 'regularMarketChangePercent'})
            change = float(change_element['value']) if change_element else None

            # Extract volume
            volume_element = soup.find('fin-streamer', {'data-symbol': symbol, 'data-field': 'regularMarketVolume'})
            volume = int(volume_element['value']) if volume_element else None

            # Extract 52 week range
            range_pattern = re.compile(r'52 Week Range')
            range_row = soup.find('td', text=range_pattern)
            if range_row:
                range_text = range_row.find_next_sibling('td').text
                low, high = map(float, range_text.split(' - '))
            else:
                low, high = None, None

            return {
                "price": price,
                "change": change,
                "volume": volume,
                "52w_high": high,
                "52w_low": low
            }

        except Exception as e:
            self.logger.error(f"Error scraping Yahoo Finance for {symbol}: {str(e)}")
            return None

    def _scrape_market_watch(self, symbol: str) -> Optional[Dict]:
        """
        Scrape stock data from MarketWatch
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Optional[Dict]: Stock data if successful, None otherwise
        """
        try:
            url = f"https://www.marketwatch.com/investing/stock/{symbol}"
            html = self._make_request(url)
            if not html:
                return None

            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract market cap
            market_cap_element = soup.find('div', text=re.compile('Market Cap'))
            market_cap = market_cap_element.find_next_sibling('div').text.strip() if market_cap_element else None

            # Extract P/E ratio
            pe_element = soup.find('div', text=re.compile('P/E Ratio'))
            pe_ratio = float(pe_element.find_next_sibling('div').text.strip()) if pe_element else None

            return {
                "market_cap": market_cap,
                "pe_ratio": pe_ratio
            }

        except Exception as e:
            self.logger.error(f"Error scraping MarketWatch for {symbol}: {str(e)}")
            return None

    def get_market_movers(self) -> Dict[str, List[str]]:
        """
        Get market movers (top gainers and losers)
        
        Returns:
            Dict[str, List[str]]: Dictionary containing gainers and losers
        """
        try:
            url = "https://finance.yahoo.com/gainers"
            html = self._make_request(url)
            if not html:
                return {"gainers": [], "losers": []}

            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract gainers
            gainers_table = soup.find('table', {'class': 'W(100%)'})
            gainers = []
            if gainers_table:
                for row in gainers_table.find_all('tr')[1:]:  # Skip header row
                    symbol = row.find('a')
                    if symbol:
                        gainers.append(symbol.text.strip())

            # Get losers
            url = "https://finance.yahoo.com/losers"
            html = self._make_request(url)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract losers
            losers_table = soup.find('table', {'class': 'W(100%)'})
            losers = []
            if losers_table:
                for row in losers_table.find_all('tr')[1:]:  # Skip header row
                    symbol = row.find('a')
                    if symbol:
                        losers.append(symbol.text.strip())

            return {
                "gainers": gainers[:10],  # Top 10 gainers
                "losers": losers[:10]     # Top 10 losers
            }

        except Exception as e:
            self.logger.error(f"Error getting market movers: {str(e)}")
            return {"gainers": [], "losers": []}

    def get_market_news(self) -> List[Dict]:
        """
        Get latest market news
        
        Returns:
            List[Dict]: List of news articles
        """
        try:
            url = "https://finance.yahoo.com/news/"
            html = self._make_request(url)
            if not html:
                return []

            soup = BeautifulSoup(html, 'html.parser')
            news_list = []

            # Find news articles
            articles = soup.find_all('h3')
            for article in articles[:10]:  # Get top 10 news
                link = article.find('a')
                if link:
                    news_list.append({
                        "title": link.text.strip(),
                        "url": f"https://finance.yahoo.com{link['href']}"
                    })

            return news_list

        except Exception as e:
            self.logger.error(f"Error getting market news: {str(e)}")
            return []

    def get_technical_indicators(self, symbol: str) -> Optional[Dict]:
        """
        Calculate technical indicators from scraped data
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Optional[Dict]: Technical indicators if successful, None otherwise
        """
        try:
            url = f"https://finance.yahoo.com/quote/{symbol}/history"
            html = self._make_request(url)
            if not html:
                return None

            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract historical prices
            prices = []
            table = soup.find('table', {'data-test': 'historical-prices'})
            if table:
                for row in table.find_all('tr')[1:]:  # Skip header row
                    cols = row.find_all('td')
                    if len(cols) >= 5:  # Ensure row has enough columns
                        try:
                            close_price = float(cols[4].text.replace(',', ''))
                            prices.append(close_price)
                        except ValueError:
                            continue

            if not prices:
                return None

            # Calculate RSI
            rsi = self._calculate_rsi(prices)

            # Calculate MACD
            macd, signal, hist = self._calculate_macd(prices)

            # Calculate SMA
            sma = self._calculate_sma(prices)

            return {
                "rsi": rsi,
                "macd": {
                    "macd": macd,
                    "signal": signal,
                    "hist": hist
                } if macd is not None else None,
                "sma": sma
            }

        except Exception as e:
            self.logger.error(f"Error getting technical indicators for {symbol}: {str(e)}")
            return None

    def _calculate_rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        """Calculate RSI"""
        try:
            if len(prices) < period + 1:
                return None

            # Calculate price changes
            changes = [prices[i] - prices[i+1] for i in range(len(prices)-1)]
            
            # Separate gains and losses
            gains = [max(0, change) for change in changes]
            losses = [max(0, -change) for change in changes]

            # Calculate average gains and losses
            avg_gain = sum(gains[:period]) / period
            avg_loss = sum(losses[:period]) / period

            # Calculate RS and RSI
            if avg_loss == 0:
                return 100.0

            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            return round(rsi, 2)

        except Exception:
            return None

    def _calculate_macd(self, prices: List[float]) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Calculate MACD"""
        try:
            if len(prices) < 26:
                return None, None, None

            # Calculate EMAs
            ema12 = self._calculate_ema(prices, 12)
            ema26 = self._calculate_ema(prices, 26)

            if ema12 is None or ema26 is None:
                return None, None, None

            # Calculate MACD line
            macd_line = ema12 - ema26

            # Calculate signal line
            signal_line = self._calculate_ema([macd_line], 9)

            if signal_line is None:
                return None, None, None

            # Calculate histogram
            histogram = macd_line - signal_line

            return round(macd_line, 2), round(signal_line, 2), round(histogram, 2)

        except Exception:
            return None, None, None

    def _calculate_ema(self, prices: List[float], period: int) -> Optional[float]:
        """Calculate EMA"""
        try:
            if len(prices) < period:
                return None

            multiplier = 2 / (period + 1)
            ema = sum(prices[:period]) / period

            for price in prices[period:]:
                ema = (price * multiplier) + (ema * (1 - multiplier))

            return ema

        except Exception:
            return None

    def _calculate_sma(self, prices: List[float], period: int = 20) -> Optional[float]:
        """Calculate SMA"""
        try:
            if len(prices) < period:
                return None

            return round(sum(prices[:period]) / period, 2)

        except Exception:
            return None
