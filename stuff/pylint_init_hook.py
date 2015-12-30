import sys, os

venv = os.environ.get('VIRTUAL_ENV', None)

if venv and venv not in sys.path:
    sys.path.insert(0, venv)

#venv_dir = os.environ['VIRTUAL_ENV']
#activate_this = os.path.join(os.path.join(ve_dir, 'bin'), 'activate_this.py')
#
#execfile(activate_this, dict(__file__=activate_this))
