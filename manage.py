#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# === PARCHE PYTHONPORTABLE ===
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# =============================


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(...)
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()