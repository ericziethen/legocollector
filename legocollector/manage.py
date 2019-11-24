#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from utils import project_logger


def setup_logger():
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, 'management.log')
    project_logger.setup_logger(log_file)


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legocollector.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    setup_logger()
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
