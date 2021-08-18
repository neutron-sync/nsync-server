#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    ppath = os.environ.get('PYTHONPATH', '')
    print('NARF', ppath)
    if os.getcwd() not in ppath:
        if ppath:
            os.environ['PYTHONPATH'] = ppath + ':' + os.getcwd()
        else:
            os.environ['PYTHONPATH'] = os.getcwd()

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nsync_server.nsync.settings.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
