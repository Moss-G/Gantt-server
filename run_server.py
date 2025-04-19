#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Direct run script for Gantt chart MCP server

import sys
import os

# Add project root directory to Python path
sys.path.insert(0, os.path.abspath("."))

try:
    # Try to import main function
    from src.gantt_mcp_server import main
    
    print("Starting Gantt Chart MCP Server...")
    # Run the main function
    main()
    
except Exception as e:
    print(f"Failed to start server: {str(e)}")
    print(f"Error type: {type(e)}")
    import traceback
    traceback.print_exc() 