from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from time import sleep
from ..core.analyzer import TradeAnalyzer
from ..utils.logger import get_logger

class TerminalUI:
    def __init__(self, config):
        self.config = config
        self.console = Console()
        self.analyzer = TradeAnalyzer(config)
        self.logger = get_logger(__name__)

    def display_menu(self):
        """Display main menu options"""
        menu = """
        [bold cyan]Trade Analyzer Menu[/bold cyan]
        
        1. View Top 6 Recommended Quotes
        2. Analyze Specific Quote
        3. Analyze All Quotes
        4. Re-analyze for New Recommendations
        5. Settings
        6. Exit
        
        Enter your choice (1-6): """
        
        self.console.print(Panel(menu))

    def display_dashboard(self, symbol, data):
        """Display analysis dashboard for a specific symbol"""
        layout = Layout()
        
        # Create header
        header = Table.grid()
        header.add_row(f"[bold cyan]Analysis Dashboard - {symbol}[/bold cyan]")
        
        # Create main content tables
        price_info = Table(title="Price Information", show_header=True)
        price_info.add_column("Metric")
        price_info.add_column("Value")
        
        technical = Table(title="Technical Analysis", show_header=True)
        technical.add_column("Indicator")
        technical.add_column("Value")
        technical.add_column("Signal")
        
        risk = Table(title="Risk Analysis", show_header=True)
        risk.add_column("Metric")
        risk.add_column("Value")
        
        # Add data to tables
        if data:
            # Price Information
            price_info.add_row("Current Price", str(data.get('price', 'N/A')))
            price_info.add_row("Daily Change", str(data.get('change', 'N/A')))
            price_info.add_row("Volume", str(data.get('volume', 'N/A')))
            
            # Technical Analysis
            technical.add_row("RSI", 
                            str(data.get('rsi', 'N/A')),
                            self._get_rsi_signal(data.get('rsi', 50)))
            technical.add_row("MACD", 
                            str(data.get('macd', 'N/A')),
                            data.get('macd_signal', 'N/A'))
            technical.add_row("Trend", 
                            data.get('trend', 'N/A'),
                            data.get('trend_strength', 'N/A'))
            
            # Risk Analysis
            risk.add_row("Entry Price", str(data.get('entry_price', 'N/A')))
            risk.add_row("Stop Loss", str(data.get('stop_loss', 'N/A')))
            risk.add_row("Take Profit", str(data.get('take_profit', 'N/A')))
            risk.add_row("Win Rate", str(data.get('win_rate', 'N/A')) + '%')
            risk.add_row("Risk %", str(data.get('risk_percentage', 'N/A')) + '%')
        
        # Layout setup
        layout.split(
            Layout(header, size=3),
            Layout(name="main", ratio=1)
        )
        layout["main"].split_row(
            Layout(price_info),
            Layout(technical),
            Layout(risk)
        )
        
        return layout

    def run(self):
        """Main UI loop"""
        while True:
            try:
                self.display_menu()
                choice = input().strip()
                
                if choice == '1':
                    self._handle_top_recommendations()
                elif choice == '2':
                    self._handle_specific_analysis()
                elif choice == '3':
                    self._handle_all_quotes()
                elif choice == '4':
                    self._handle_reanalysis()
                elif choice == '5':
                    self._handle_settings()
                elif choice == '6':
                    self.logger.info("Exiting application...")
                    break
                else:
                    self.console.print("[red]Invalid choice. Please try again.[/red]")
                    
            except Exception as e:
                self.logger.error(f"UI Error: {str(e)}")
                self.console.print(f"[red]Error: {str(e)}[/red]")

    def _handle_top_recommendations(self):
        """Handle displaying top 6 recommendations"""
        with self.console.status("[bold green]Analyzing top recommendations..."):
            recommendations = self.analyzer.get_top_recommendations()
            
        table = Table(title="Top 6 Recommended Quotes")
        table.add_column("Symbol")
        table.add_column("Action")
        table.add_column("Win Rate")
        table.add_column("Risk %")
        
        for rec in recommendations:
            table.add_row(
                rec['symbol'],
                rec['action'],
                f"{rec['win_rate']}%",
                f"{rec['risk']}%"
            )
            
        self.console.print(table)

    def _handle_specific_analysis(self):
        """Handle analysis of a specific quote"""
        symbol = input("Enter symbol to analyze: ").strip().upper()
        
        with Live(self.console.status("[bold green]Analyzing..."), refresh_per_second=4) as live:
            data = self.analyzer.analyze_quote(symbol)
            dashboard = self.display_dashboard(symbol, data)
            live.update(dashboard)
            
            # Update every 5 seconds
            while True:
                sleep(self.config.SCAN_INTERVAL)
                data = self.analyzer.analyze_quote(symbol)
                dashboard = self.display_dashboard(symbol, data)
                live.update(dashboard)

    def _handle_all_quotes(self):
        """Handle analysis of all quotes"""
        with self.console.status("[bold green]Analyzing all quotes..."):
            results = self.analyzer.analyze_all_quotes()
            
        table = Table(title="All Quotes Analysis")
        table.add_column("Symbol")
        table.add_column("Action")
        table.add_column("Win Rate")
        table.add_column("Risk %")
        
        for result in results:
            table.add_row(
                result['symbol'],
                result['action'],
                f"{result['win_rate']}%",
                f"{result['risk']}%"
            )
            
        self.console.print(table)

    def _handle_reanalysis(self):
        """Handle reanalysis for new recommendations"""
        with self.console.status("[bold green]Reanalyzing..."):
            recommendations = self.analyzer.reanalyze()
            
        table = Table(title="New Recommendations")
        table.add_column("Symbol")
        table.add_column("Action")
        table.add_column("Win Rate")
        table.add_column("Risk %")
        
        for rec in recommendations:
            table.add_row(
                rec['symbol'],
                rec['action'],
                f"{rec['win_rate']}%",
                f"{rec['risk']}%"
            )
            
        self.console.print(table)

    def _handle_settings(self):
        """Handle settings menu"""
        settings_menu = """
        [bold cyan]Settings[/bold cyan]
        
        1. Risk Management
        2. Technical Indicators
        3. Data Sources
        4. Back to Main Menu
        
        Enter your choice (1-4): """
        
        self.console.print(Panel(settings_menu))
        choice = input().strip()
        
        if choice == '1':
            self._handle_risk_settings()
        elif choice == '2':
            self._handle_indicator_settings()
        elif choice == '3':
            self._handle_data_source_settings()
        elif choice == '4':
            return
        else:
            self.console.print("[red]Invalid choice.[/red]")

    def _get_rsi_signal(self, rsi):
        """Get RSI signal based on value"""
        if rsi is None:
            return "N/A"
        if rsi > self.config.RSI_OVERBOUGHT:
            return "[red]Overbought[/red]"
        elif rsi < self.config.RSI_OVERSOLD:
            return "[green]Oversold[/green]"
        return "[yellow]Neutral[/yellow]"

    def _handle_risk_settings(self):
        """Handle risk management settings"""
        pass  # To be implemented

    def _handle_indicator_settings(self):
        """Handle technical indicator settings"""
        pass  # To be implemented

    def _handle_data_source_settings(self):
        """Handle data source settings"""
        pass  # To be implemented
