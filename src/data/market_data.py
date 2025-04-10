from typing import Dict, List, Optional
from .web_scraper import WebScraper
from ..utils.logger import get_logger

class MarketData:
    def __init__(self):
        self.scraper = WebScraper()
        self.logger = get_logger(__name__)

    def get_stock_data(self, symbol: str) -> Optional[Dict]:
        """
        Get comprehensive stock data
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Optional[Dict]: Stock data or None if failed
        """
        try:
            # Get basic stock data
            stock_data = self.scraper.get_stock_data(symbol)
            if not stock_data:
                return None

            # Get technical indicators
            indicators = self.scraper.get_technical_indicators(symbol)
            if indicators:
                stock_data.update(indicators)

            return stock_data

        except Exception as e:
            self.logger.error(f"Error getting stock data for {symbol}: {str(e)}")
            return None

    def get_market_overview(self) -> Dict:
        """
        Get comprehensive market overview
        
        Returns:
            Dict: Market overview data
        """
        try:
            # Get market movers
            movers = self.scraper.get_market_movers()
            
            # Get market news
            news = self.scraper.get_market_news()
            
            # Get major indices data
            indices = ['SPY', 'QQQ', 'DIA']  # S&P 500, NASDAQ, Dow Jones
            indices_data = {}
            
            for symbol in indices:
                data = self.scraper.get_stock_data(symbol)
                if data:
                    indices_data[symbol] = {
                        'price': data.get('price'),
                        'change': data.get('change'),
                        'volume': data.get('volume')
                    }

            return {
                'movers': movers,
                'news': news,
                'indices': indices_data
            }

        except Exception as e:
            self.logger.error(f"Error getting market overview: {str(e)}")
            return {
                'movers': {'gainers': [], 'losers': []},
                'news': [],
                'indices': {}
            }

    def analyze_stock(self, symbol: str) -> Dict:
        """
        Perform comprehensive stock analysis
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Dict: Analysis results
        """
        try:
            # Get stock data
            data = self.get_stock_data(symbol)
            if not data:
                return self._get_empty_analysis()

            # Analyze technical indicators
            technical_analysis = self._analyze_technical_indicators(data)

            # Analyze price action
            price_analysis = self._analyze_price_action(data)

            # Generate trading signals
            signals = self._generate_signals(technical_analysis, price_analysis)

            return {
                'data': data,
                'technical_analysis': technical_analysis,
                'price_analysis': price_analysis,
                'signals': signals
            }

        except Exception as e:
            self.logger.error(f"Error analyzing stock {symbol}: {str(e)}")
            return self._get_empty_analysis()

    def _analyze_technical_indicators(self, data: Dict) -> Dict:
        """Analyze technical indicators"""
        analysis = {
            'trend': 'neutral',
            'strength': 'weak',
            'signals': []
        }

        # Analyze RSI
        rsi = data.get('rsi')
        if rsi is not None:
            if rsi > 70:
                analysis['signals'].append('overbought')
            elif rsi < 30:
                analysis['signals'].append('oversold')

        # Analyze MACD
        macd = data.get('macd', {})
        if macd:
            macd_line = macd.get('macd')
            signal_line = macd.get('signal')
            if macd_line is not None and signal_line is not None:
                if macd_line > signal_line:
                    analysis['signals'].append('bullish_macd')
                else:
                    analysis['signals'].append('bearish_macd')

        return analysis

    def _analyze_price_action(self, data: Dict) -> Dict:
        """Analyze price action"""
        return {
            'trend': self._determine_trend(data),
            'volatility': self._calculate_volatility(data),
            'support_resistance': self._find_support_resistance(data)
        }

    def _determine_trend(self, data: Dict) -> str:
        """Determine price trend"""
        change = data.get('change', 0)
        if change > 1:
            return 'uptrend'
        elif change < -1:
            return 'downtrend'
        return 'sideways'

    def _calculate_volatility(self, data: Dict) -> str:
        """Calculate price volatility"""
        high = data.get('52w_high', 0)
        low = data.get('52w_low', 0)
        if high and low and high > low:
            volatility = (high - low) / low * 100
            if volatility > 50:
                return 'high'
            elif volatility > 25:
                return 'medium'
        return 'low'

    def _find_support_resistance(self, data: Dict) -> Dict:
        """Find support and resistance levels"""
        return {
            'support': data.get('52w_low'),
            'resistance': data.get('52w_high')
        }

    def _generate_signals(self, technical_analysis: Dict, price_analysis: Dict) -> List[str]:
        """Generate trading signals"""
        signals = []
        
        # Combine technical and price signals
        signals.extend(technical_analysis['signals'])
        
        # Add trend signals
        if price_analysis['trend'] == 'uptrend':
            signals.append('trend_following_buy')
        elif price_analysis['trend'] == 'downtrend':
            signals.append('trend_following_sell')
            
        # Add volatility signals
        if price_analysis['volatility'] == 'high':
            signals.append('high_volatility')
            
        return signals

    def _get_empty_analysis(self) -> Dict:
        """Get empty analysis structure"""
        return {
            'data': {},
            'technical_analysis': {
                'trend': 'neutral',
                'strength': 'weak',
                'signals': []
            },
            'price_analysis': {
                'trend': 'sideways',
                'volatility': 'low',
                'support_resistance': {
                    'support': None,
                    'resistance': None
                }
            },
            'signals': []
        }
