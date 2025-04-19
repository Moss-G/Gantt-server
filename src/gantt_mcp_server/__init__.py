#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Gantt Chart MCP Server
# This file marks src/gantt_mcp_server as a Python package and defines entry points

from .server import run_server, mcp

def main():
    """
    Main entry point to start the Gantt Chart MCP server.
    Referenced by the [project.scripts] entry in pyproject.toml.
    """
    run_server()

# Export important items for other Python code to import
__all__ = ["main", "mcp", "run_server"] 