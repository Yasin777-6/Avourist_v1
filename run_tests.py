"""
Test Runner for AI Agent System
Runs all tests and generates a comprehensive report
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autouristv1.settings')
django.setup()

import pytest
from colorama import init, Fore, Style

init(autoreset=True)

def print_header(text):
    """Print colored header"""
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}{text:^80}")
    print(f"{Fore.CYAN}{'='*80}\n")

def print_success(text):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {text}")

def print_error(text):
    """Print error message"""
    print(f"{Fore.RED}✗ {text}")

def print_info(text):
    """Print info message"""
    print(f"{Fore.YELLOW}ℹ {text}")


def run_all_tests():
    """Run all test suites"""
    print_header("AUTOURIST AI AGENT SYSTEM - TEST SUITE")
    
    print_info("Running comprehensive tests...")
    print_info("Testing: Agent routing, AI selling skills, content quality, performance\n")
    
    # Run pytest with detailed output
    exit_code = pytest.main([
        'tests/test_ai_agents.py',
        '-v',                    # Verbose
        '--tb=short',           # Short traceback
        '--color=yes',          # Colored output
        '-ra',                  # Show summary of all test outcomes
        '--durations=10',       # Show 10 slowest tests
    ])
    
    print_header("TEST RESULTS SUMMARY")
    
    if exit_code == 0:
        print_success("All tests passed!")
        print_success("Multi-agent system is working correctly")
        print_success("AI selling skills validated")
        print_success("Content quality verified")
        print_success("Performance benchmarks met")
    else:
        print_error("Some tests failed. Please review the output above.")
    
    return exit_code


def run_specific_test(test_class):
    """Run specific test class"""
    print_header(f"Running {test_class}")
    
    exit_code = pytest.main([
        f'tests/test_ai_agents.py::{test_class}',
        '-v',
        '--tb=short',
        '--color=yes',
    ])
    
    return exit_code


def run_quick_smoke_test():
    """Run quick smoke test"""
    print_header("QUICK SMOKE TEST")
    
    print_info("Testing basic functionality...\n")
    
    exit_code = pytest.main([
        'tests/test_ai_agents.py::TestAgentOrchestrator',
        'tests/test_ai_agents.py::TestKnowledgeBase',
        '-v',
        '--tb=line',
        '--color=yes',
    ])
    
    if exit_code == 0:
        print_success("\nSmoke test passed! System is operational.")
    else:
        print_error("\nSmoke test failed. Check basic functionality.")
    
    return exit_code


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run AI Agent System Tests')
    parser.add_argument('--quick', action='store_true', help='Run quick smoke test only')
    parser.add_argument('--class', dest='test_class', help='Run specific test class')
    
    args = parser.parse_args()
    
    if args.quick:
        exit_code = run_quick_smoke_test()
    elif args.test_class:
        exit_code = run_specific_test(args.test_class)
    else:
        exit_code = run_all_tests()
    
    sys.exit(exit_code)
