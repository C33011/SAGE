"""
Utility functions for SAGE tests.

This module provides helper functions to make testing more robust
when dealing with components that may not be fully implemented yet.
"""

import unittest
import inspect
import sys
import importlib
from types import ModuleType
from typing import Optional, Callable, Any, Dict, List, Union, Type

def ensure_class_exists(module_path: str, class_name: str) -> Optional[Type]:
    """
    Try to import a class from a module path, returning None if not available.
    
    Args:
        module_path: Dot-separated path to the module
        class_name: Name of the class to import
        
    Returns:
        The class object if available, otherwise None
    """
    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name) if hasattr(module, class_name) else None
    except (ImportError, AttributeError):
        return None

def ensure_function_exists(module_path: str, function_name: str) -> Optional[Callable]:
    """
    Try to import a function from a module path, returning None if not available.
    
    Args:
        module_path: Dot-separated path to the module
        function_name: Name of the function to import
        
    Returns:
        The function object if available, otherwise None
    """
    try:
        module = importlib.import_module(module_path)
        return getattr(module, function_name) if hasattr(module, function_name) else None
    except (ImportError, AttributeError):
        return None

def require_implementation(test_case: unittest.TestCase, obj: Any, required_attrs: List[str]) -> bool:
    """
    Check if an object has the required attributes, skip the test if not.
    
    Args:
        test_case: The unittest.TestCase instance
        obj: The object to check
        required_attrs: List of attribute names that should exist
        
    Returns:
        True if all attributes exist, otherwise calls skipTest and returns False
    """
    missing_attrs = [attr for attr in required_attrs if not hasattr(obj, attr)]
    if missing_attrs:
        test_case.skipTest(f"Implementation missing required attributes: {', '.join(missing_attrs)}")
        return False
    return True

def mock_if_missing(module_path: str, name: str, mock_implementation: Any = None) -> Any:
    """
    Try to import an object from a module, using a mock implementation if not available.
    
    Args:
        module_path: Dot-separated path to the module
        name: Name of the object to import
        mock_implementation: Mock to use if the object is not available
        
    Returns:
        The imported object or the mock implementation
    """
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, name):
            return getattr(module, name)
    except ImportError:
        pass
    
    return mock_implementation

def describe_object(obj: Any) -> str:
    """
    Generate a description of an object for debugging.
    
    Args:
        obj: The object to describe
        
    Returns:
        A string description of the object
    """
    if obj is None:
        return "None"
    
    result = f"Type: {type(obj).__name__}\n"
    
    if inspect.isclass(obj):
        result += "Class Attributes:\n"
        for attr in dir(obj):
            if not attr.startswith('__'):
                result += f"  - {attr}\n"
    elif inspect.isfunction(obj) or inspect.ismethod(obj):
        result += f"Function Signature: {inspect.signature(obj)}\n"
    elif isinstance(obj, dict):
        result += "Dict Contents:\n"
        for k, v in obj.items():
            result += f"  - {k}: {type(v).__name__}\n"
    elif isinstance(obj, (list, tuple)):
        result += f"Collection Length: {len(obj)}\n"
        if obj:
            result += f"First Item Type: {type(obj[0]).__name__}\n"
    else:
        result += "Attributes:\n"
        for attr in dir(obj):
            if not attr.startswith('__'):
                result += f"  - {attr}\n"
    
    return result

class ConditionalTestCase(unittest.TestCase):
    """A TestCase that can conditionally skip based on implementation status."""
    
    def require_implementation(self, obj: Any, required_attrs: List[str]) -> bool:
        """Check if required implementation exists."""
        return require_implementation(self, obj, required_attrs)
    
    def assert_attribute_exists(self, obj: Any, attr_name: str, msg: Optional[str] = None):
        """Assert that an attribute exists on the object."""
        if not hasattr(obj, attr_name):
            raise AssertionError(msg or f"Attribute '{attr_name}' does not exist on {obj}")
