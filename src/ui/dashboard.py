from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress
from datetime import datetime
from typing import Dict, Optional
from ..utils.helpers import format_price, format_percentage
from ..utils.logger import get_logger

class Dashboard:
    def __init__(self):
        self.console = Console()
        self.logger = get_logger(__name__)

    def create_analysis_dashboard(
        self,
        symbol: str,
        data: Dict
    ) -> Layout:
        """
        Create main analysis dashboard layout
        
        Args:
            symbol (str): Symbol being analyzed
            data (Dict): Analysis data
            
        Returns:
            Layout: Dashboard layout
        """
        try:
            layout = Layout()
            
            # Create header
            header = self._create_header(symbol, data)
            
            # Create main content
            main_content = Layout()
            main_content.split_row(
                self._create_price_panel(data),
                self._create_technical_panel(data),
                self._create_risk_panel(data)
            )
            
            # Create footer with signals
            footer = self._create_signals_panel(data)
            
            # Combine all sections
            layout.split(
                Layout(header, size=3),
                Layout(main_content, ratio=1),
                Layout(footer, size=3)
            )
            
            return layout
            
        except Exception as e:
            self.logger.error(f"Error creating dashboard: {str(e)}")
            return self._create_error_layout()

    def _create_header(self, symbol: str, data: Dict) -> Panel:
        """Create dashboard header"""
        title = f"[bold cyan]Analysis Dashboard - {symbol}[/bold cyan]"
        timestamp = f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return Panel(f"{title}\n{timestamp}")

    def _create_price_panel(self, data: Dict) -> Panel:
        """Create price information panel"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Price Information")
        table.add_column("Value")
        
        try:
            table.add_row(
                "Current Price",
                format_price(data.get('price', 0))
            )
            table.add_row(
                "Daily Change",
                self._format_change(data.get('change', 0))
            )
            table.add_row(
                "Volume",
                f"{data.get('volume', 0):,}"
            )
            
            return Panel(table, title="Price Information")
            
        except Exception as e:
            self.logger.error(f"Error creating price panel: {str(e)}")
            return Panel("Error loading price data")

    def _create_technical_panel(self, data: Dict) -> Panel:
        """Create technical analysis panel"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Indicator")
        table.add_column("Value")
        table.add_column("Signal")
        
        try:
            # RSI
            table.add_row(
                "RSI",
                format_price(data.get('rsi', 0)),
                self._get_rsi_signal(data.get('rsi', 50))
            )
            
            # MACD
            table.add_row(
                "MACD",
                format_price(data.get('macd', 0)),
                data.get('macd_signal', 'Neutral')
            )
            
            # Volume
            table.add_row(
                "Volume",
                data.get('volume_signal', 'Normal'),
                self._get_volume_signal(data.get('volume_trend', 'neutral'))
            )
            
            # Trend
            table.add_row(
                "Trend",
                data.get('trend', 'Neutral'),
                data.get('trend_strength', 'Weak')
            )
            
            return Panel(table, title="Technical Analysis")
            
        except Exception as e:
            self.logger.error(f"Error creating technical panel: {str(e)}")
            return Panel("Error loading technical data")

    def _create_risk_panel(self, data: Dict) -> Panel:
        """Create risk analysis panel"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Risk Metrics")
        table.add_column("Value")
        
        try:
            table.add_row(
                "Entry Price",
                format_price(data.get('entry_price', 0))
            )
            table.add_row(
                "Stop Loss",
                format_price(data.get('stop_loss', 0))
            )
            table.add_row(
                "Take Profit",
                format_price(data.get('take_profit', 0))
            )
            table.add_row(
                "Risk %",
                format_percentage(data.get('risk_percentage', 0))
            )
            table.add_row(
                "Win Rate",
                format_percentage(data.get('win_rate', 0))
            )
            
            return Panel(table, title="Risk Analysis")
            
        except Exception as e:
            self.logger.error(f"Error creating risk panel: {str(e)}")
            return Panel("Error loading risk data")

    def _create_signals_panel(self, data: Dict) -> Panel:
        """Create trading signals panel"""
        try:
            action = data.get('action', 'NEUTRAL')
            confidence = data.get('confidence', 0)
            
            signal_text = self._format_signal(action, confidence)
            return Panel(signal_text, title="Trading Signals")
            
        except Exception as e:
            self.logger.error(f"Error creating signals panel: {str(e)}")
            return Panel("Error loading signals")

    def create_recommendations_table(
        self,
        recommendations: list
    ) -> Table:
        """
        Create table for trade recommendations
        
        Args:
            recommendations (list): List of recommended trades
            
        Returns:
            Table: Recommendations table
        """
        table = Table(
            title="Trade Recommendations",
            show_header=True,
            header_style="bold magenta"
        )
        
        try:
            # Add columns
            table.add_column("Symbol")
            table.add_column("Action")
            table.add_column("Price")
            table.add_column("Win Rate")
            table.add_column("Risk %")
            table.add_column("Confidence")
            
            # Add rows
            for rec in recommendations:
                table.add_row(
                    rec['symbol'],
                    self._format_action(rec['action']),
                    format_price(rec.get('price', 0)),
                    format_percentage(rec.get('win_rate', 0)),
                    format_percentage(rec.get('risk_percentage', 0)),
                    format_percentage(rec.get('confidence', 0))
                )
                
            return table
            
        except Exception as e:
            self.logger.error(f"Error creating recommendations table: {str(e)}")
            return Table(title="Error loading recommendations")

    def _format_change(self, change: float) -> Text:
        """Format price change with color"""
        if change > 0:
            return Text(f"+{format_percentage(change)}", style="green")
        elif change < 0:
            return Text(format_percentage(change), style="red")
        return Text(format_percentage(change), style="white")

    def _get_rsi_signal(self, rsi: float) -> Text:
        """Get colored RSI signal"""
        if rsi > 70:
            return Text("Overbought", style="red")
        elif rsi < 30:
            return Text("Oversold", style="green")
        return Text("Neutral", style="yellow")

    def _get_volume_signal(self, trend: str) -> Text:
        """Get colored volume signal"""
        if trend == "increasing":
            return Text("Increasing", style="green")
        elif trend == "decreasing":
            return Text("Decreasing", style="red")
        return Text("Neutral", style="yellow")

    def _format_signal(self, action: str, confidence: float) -> Text:
        """Format trading signal with color and confidence"""
        signal_text = f"{action} (Confidence: {format_percentage(confidence)})"
        
        if action in ["STRONG BUY", "BUY"]:
            return Text(signal_text, style="bold green")
        elif action in ["STRONG SELL", "SELL"]:
            return Text(signal_text, style="bold red")
        return Text(signal_text, style="bold yellow")

    def _format_action(self, action: str) -> Text:
        """Format action with color"""
        if "BUY" in action.upper():
            return Text(action, style="green")
        elif "SELL" in action.upper():
            return Text(action, style="red")
        return Text(action, style="yellow")

    def _create_error_layout(self) -> Layout:
        """Create error layout"""
        layout = Layout()
        error_panel = Panel(
            "[red]Error creating dashboard. Please try again.[/red]"
        )
        layout.update(error_panel)
        return layout

    def show_loading(self, message: str = "Loading..."):
        """Show loading progress"""
        with Progress() as progress:
            task = progress.add_task(message, total=None)
            while not progress.finished:
                progress.update(task)

    def show_error(self, message: str):
        """Show error message"""
        self.console.print(f"[red]Error: {message}[/red]")

    def show_success(self, message: str):
        """Show success message"""
        self.console.print(f"[green]{message}[/green]")
