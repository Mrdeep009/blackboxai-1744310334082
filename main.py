#!/usr/bin/env python3

import os
import sys
from src.ui.terminal import TerminalUI
from src.core.config import load_config
from src.utils.logger import setup_logger

def main():
    """
    Main entry point for the Trade Analyzer application.
    """
    # Setup logging
    logger = setup_logger()
    logger.info("Starting Trade Analyzer...")

    try:
        # Load configuration
        config = load_config()
        
        # Initialize terminal UI
        ui = TerminalUI(config)
        
        # Start the application
        ui.run()

    except KeyboardInterrupt:
        logger.info("Application terminated by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
