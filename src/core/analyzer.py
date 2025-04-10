from typing import Dict, List, Optional
from ..utils.logger import get_logger
from ..data.market_data import MarketData

class TradeAnalyzer:
    def __init__(self, config: Dict):
        """
        Initialize Trade Analyzer
        
        Args:
            config (Dict): Configuration settings
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.market_data = MarketData()

    def analyze_quote(self, symbol: str) -> Optional[Dict]:
        """
        Analyze a specific stock quote
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            Optional[Dict]: Analysis results
        """
        try:
            # Get comprehensive analysis from market data
            analysis = self.market_data.analyze_stock(symbol)
            if not analysis:
                return None

            # Extract relevant data
            data = analysis['data']
            technical = analysis['technical_analysis']
            price = analysis['price_analysis']
            signals = analysis['signals']

            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(data, technical, price)

            # Generate recommendation
            recommendation = self._generate_recommendation(technical, price, signals)

            return {
                'symbol': symbol,
                'price': data.get('price'),
                'change': data.get('change'),
                'volume': data.get('volume'),
                'rsi': data.get('rsi'),
                'macd': data.get('macd', {}).get('macd'),
                'macd_signal': data.get('macd', {}).get('signal'),
                'trend': price['trend'],
                'trend_strength': technical['strength'],
                'entry_price': risk_metrics['entry_price'],
                'stop_loss': risk_metrics['stop_loss'],
                'take_profit': risk_metrics['take_profit'],
                'win_rate': risk_metrics['win_rate'],
                'risk_percentage': risk_metrics['risk_percentage'],
                'recommendation': recommendation
            }

        except Exception as e:
            self.logger.error(f"Error analyzing quote {symbol}: {str(e)}")
            return None

    def get_top_recommendations(self) -> List[Dict]:
        """
        Get top trading recommendations
        
        Returns:
            List[Dict]: List of recommendations
        """
        try:
            # Get market movers
            market_overview = self.market_data.get_market_overview()
            movers = market_overview['movers']
            
            recommendations = []
            
            # Analyze top gainers and losers
            symbols = movers['gainers'][:3] + movers['losers'][:3]
            
            for symbol in symbols:
                analysis = self.analyze_quote(symbol)
                if analysis:
                    recommendations.append({
                        'symbol': symbol,
                        'action': analysis['recommendation'],
                        'win_rate': analysis['win_rate'],
                        'risk': analysis['risk_percentage']
                    })
            
            # Sort by win rate
            recommendations.sort(key=lambda x: x['win_rate'], reverse=True)
            
            return recommendations[:6]  # Return top 6

        except Exception as e:
            self.logger.error(f"Error getting top recommendations: {str(e)}")
            return []

    def analyze_all_quotes(self) -> List[Dict]:
        """
        Analyze all available quotes
        
        Returns:
            List[Dict]: Analysis results for all quotes
        """
        try:
            # Get market movers
            market_overview = self.market_data.get_market_overview()
            movers = market_overview['movers']
            
            results = []
            
            # Analyze all symbols from gainers and losers
            symbols = movers['gainers'] + movers['losers']
            
            for symbol in symbols:
                analysis = self.analyze_quote(symbol)
                if analysis:
                    results.append({
                        'symbol': symbol,
                        'action': analysis['recommendation'],
                        'win_rate': analysis['win_rate'],
                        'risk': analysis['risk_percentage']
                    })
            
            return results

        except Exception as e:
            self.logger.error(f"Error analyzing all quotes: {str(e)}")
            return []

    def reanalyze(self) -> List[Dict]:
        """
        Reanalyze for new recommendations
        
        Returns:
            List[Dict]: New recommendations
        """
        return self.get_top_recommendations()

    def _calculate_risk_metrics(
        self,
        data: Dict,
        technical: Dict,
        price: Dict
    ) -> Dict:
        """Calculate risk management metrics"""
        try:
            current_price = data.get('price', 0)
            
            # Calculate entry price based on trend
            if price['trend'] == 'uptrend':
                entry_price = current_price * 0.99  # 1% below current price
            elif price['trend'] == 'downtrend':
                entry_price = current_price * 1.01  # 1% above current price
            else:
                entry_price = current_price
            
            # Calculate stop loss and take profit
            volatility = price['volatility']
            if volatility == 'high':
                stop_loss_pct = 0.05  # 5%
                take_profit_pct = 0.15  # 15%
            elif volatility == 'medium':
                stop_loss_pct = 0.03  # 3%
                take_profit_pct = 0.09  # 9%
            else:
                stop_loss_pct = 0.02  # 2%
                take_profit_pct = 0.06  # 6%
            
            stop_loss = entry_price * (1 - stop_loss_pct)
            take_profit = entry_price * (1 + take_profit_pct)
            
            # Calculate win rate based on technical signals
            base_win_rate = 50
            for signal in technical['signals']:
                if signal in ['oversold', 'bullish_macd']:
                    base_win_rate += 5
                elif signal in ['overbought', 'bearish_macd']:
                    base_win_rate += 5
            
            # Adjust win rate based on trend strength
            if technical['strength'] == 'strong':
                base_win_rate += 10
            elif technical['strength'] == 'moderate':
                base_win_rate += 5
            
            # Cap win rate at 90%
            win_rate = min(base_win_rate, 90)
            
            return {
                'entry_price': round(entry_price, 2),
                'stop_loss': round(stop_loss, 2),
                'take_profit': round(take_profit, 2),
                'win_rate': win_rate,
                'risk_percentage': round(stop_loss_pct * 100, 2)
            }

        except Exception as e:
            self.logger.error(f"Error calculating risk metrics: {str(e)}")
            return {
                'entry_price': 0,
                'stop_loss': 0,
                'take_profit': 0,
                'win_rate': 0,
                'risk_percentage': 0
            }

    def _generate_recommendation(
        self,
        technical: Dict,
        price: Dict,
        signals: List[str]
    ) -> str:
        """Generate trading recommendation"""
        try:
            # Count bullish and bearish signals
            bullish_signals = len([s for s in signals if 'buy' in s or 'bullish' in s])
            bearish_signals = len([s for s in signals if 'sell' in s or 'bearish' in s])
            
            # Consider trend
            if price['trend'] == 'uptrend':
                bullish_signals += 1
            elif price['trend'] == 'downtrend':
                bearish_signals += 1
            
            # Generate recommendation
            if bullish_signals > bearish_signals:
                if technical['strength'] == 'strong':
                    return 'Strong Buy'
                return 'Buy'
            elif bearish_signals > bullish_signals:
                if technical['strength'] == 'strong':
                    return 'Strong Sell'
                return 'Sell'
            return 'Hold'

        except Exception as e:
            self.logger.error(f"Error generating recommendation: {str(e)}")
            return 'Hold'
