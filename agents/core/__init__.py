"""
Home Assistant WorldClass Dashboard Agent - Core Module
PhD-level expert system for HA dashboards, HACS, Grafana, and database management.
"""

from .agent import HAWorldClassAgent, DeploymentResult, AgentHealth
from .base_module import BaseModule, ModuleHealth, OperationResult
from .utils import setup_logging, load_config, validate_environment

__version__ = "1.0.0"

__all__ = [
    'HAWorldClassAgent',
    'DeploymentResult',
    'AgentHealth',
    'BaseModule',
    'ModuleHealth', 
    'OperationResult',
    'setup_logging',
    'load_config',
    'validate_environment',
]

