#!/usr/bin/env python
#
#   Authors:
#   Steve Philips -- steve@builtbyptm.com
#   AJ v Bahnken  -- aj@builtbyptm.com
#
# Requires virtualenv and virtualenvwrapper
#

import commands
import os
import random
import shutil
import string
import sys
import argparse


DPB_PATH             = '/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/'
DJANGO_FILES_PATH = DPB_PATH + 'django-files/'

# Usage message to be printed for miss use
USAGE = 'usage: %s [-h] [-v] [--path PATH] [--bootstrap]' \
    % (sys.argv[0])

# Prints the usage message if there are no args
if len(sys.argv) < 2:
    sys.exit(USAGE)

# These are the arguements for the builder.  We can extent the
# arguments as we want to add more diversity
parser = argparse.ArgumentParser(description='''ProtoType Magic presents
                                  Django Project Builder and so much more...''',
                                  version='djangbuilder.py 0.5')

# Arg to declare the path to where the project will be made
parser.add_argument('--path', action='store', dest='path',
                    help='''Specifies where the new Django project
                    should be made, including the project name at the
                    end (e.g. /home/username/code/project_name)''')
# Arg for using bootstrap rather than generic templates/media
parser.add_argument('--bootstrap', action='store_true', default=False,
                         help='''This will include Bootstrap as the template
                         base of the project..''', dest='bootstrap')

arguments = parser.parse_args()

# Checks whether a path was declared
if not arguments.path:
    sys.exit("You must declare a path! (--path /path/to/project)")

# Converts to absolute path
os.path.abspath(os.path.expanduser(arguments.path))


# This is the function used to copy all of the django_files
# and server_scripts, and replace values.
def copy_files(folderPath, file_types, pathify):
    for filename in file_types:
        # Grab *-needed filenames
        f_read = open(folderPath + filename, 'r')
        contents = f_read.read()
        f_read.close()
        # Replace %(SECRET_KEY)s, etc with new value for new project
        if filename.endswith('-needed'):
            new_filename = filename.replace('-needed', '')
        # Loop through list of locations new_filename should be placed
        for dir in pathify[new_filename]:
            # Path names include '%(PROJECT_NAME)s', etc
            file_path = dir % replacement_values
            f_write = open(PROJECT_PATH + file_path + new_filename, 'a')
            print new_filename
            new_contents = contents % replacement_values
            f_write.write(new_contents)
            f_write.close()





# FIXME Every file in django_files and *-needed should be listed
# here... or we can copy entire directories

django_pathify = {
    '.gitignore':                   [''],
    '__init__.py':                  ['', '%(PROJECT_NAME)s/'],
    'appurls.py':                   ['%(PROJECT_NAME)s/'],
    'django.wsgi':                  ['apache/'],
    'manage.py':                    [''],
    'model_forms.py':               ['%(PROJECT_NAME)s/'],
    'models.py':                    ['%(PROJECT_NAME)s/'],
    'requirements.txt':             [''],
    'settings.py':                  [''],
    'settings_local.py-local':      [''],
    'tests.py':                     ['%(PROJECT_NAME)s/'],
    'urls.py':                      [''],
    'views.py':                     ['%(PROJECT_NAME)s/'],
    'wsgi.py':                      [''],
}

HOME_DIR = os.path.expandvars('$HOME').rstrip('/') + '/'

# Trailing / may be included or excluded
PROJECT_PATH = arguments.path.rstrip('/') + '_site/'
PROJECT_NAME = PROJECT_PATH.split('/')[-2].split('_')[0] # Before the '_site/'
BASE_PATH    = '/'.join(PROJECT_PATH.split('/')[:-2]) + '/'

# TODO
# vewrapper = pbs.which('virtualenvwrapper.sh')
# vewrapper("")

SECRET_KEY = ''.join([ random.choice(string.printable[:94].replace("'", ""))
                       for _ in range(50) ])
PROJECT_PASSWORD = ''.join([ random.choice(string.printable[:67].replace("'", ""))
                             for _ in range(30) ])

# Defines key: value pairs so that
#   '%(PROJECT_NAME)s' % replacement_values
# evaluates to the value of the `PROJECT_NAME` variable, such as
#   'my_project_name'
replacement_values = {
    'PROJECT_NAME':     PROJECT_NAME,
    'PROJECT_PASSWORD': PROJECT_PASSWORD,
    'BASE_PATH':        BASE_PATH,
    'SECRET_KEY':       SECRET_KEY,
    'PROJECT_PATH':     PROJECT_PATH,
}

# Doing it this way so DPB can add 'extra_settings' on the fly.
needed_dirs = ['static', 'apache', '%(PROJECT_NAME)s']

print "Creating directories..."

# Let 'git init' create the PROJECT_PATH directory and turn it into a
# git repo with one command
cmd = 'bash -c "git init %s"' % PROJECT_PATH
_, output = commands.getstatusoutput(cmd)
print '\n', output, '\n'

# Create all other dirs (each a sub-(sub-?)directory) of PROJECT_PATH
for dir_name in needed_dirs:
    os.mkdir(PROJECT_PATH + dir_name % replacement_values)

# Build list of all django-specific files to be copied into new project.
django_files = [x for x in os.listdir(DJANGO_FILES_PATH)
                 if x.endswith('-needed')]

# Oddly-placed '%' in weird_files screws up our string interpolation,
# so copy these files verbatim

print "Creating django files..."
copy_files(DJANGO_FILES_PATH, django_files, django_pathify)

print "Copying directories..."
# Add directory names here
generic_dirs = ['media', 'templates']
generic_dirs = [DPB_PATH + d for d in generic_dirs]

for dirname in generic_dirs:
    # cp -r media-generic $PROJECT_PATH/media && cp -r templates-generic ...
    if arguments.bootstrap:
        shutil.copytree(dirname + '-bootstrap',
                        PROJECT_PATH + dirname.split('/')[-1])
    else:
        shutil.copytree(dirname + '-generic',
                        PROJECT_PATH + dirname.split('/')[-1])


## Making the virtualenv here

print "Making virtualenv..."
cmd = ''
# FIXME Shouldn't assume the location of virtualenvwrapper.sh
cmd = 'bash -c "source /usr/local/bin/virtualenvwrapper.sh &&'
cmd += ' mkvirtualenv %s --no-site-packages"' % PROJECT_NAME

_, output = commands.getstatusoutput(cmd)
print '\n', output, '\n'

## The below part is made much fast with a small requirements.txt.
## We have the opitions to include more packages, which in turn
## will take long, but of course is needed. This allows for making
## projects which need only the basic's, and ones that need a lot.

cmd = ''
print "Running 'pip install -r requirements.txt'. This could take a while..."
# FIXME Shouldn't assume the location of virtualenvwrapper.sh
cmd  = 'bash -c "source /usr/local/bin/virtualenvwrapper.sh && workon'
cmd += ' %(PROJECT_NAME)s && cd %(PROJECT_PATH)s' % replacement_values
cmd += ' && pip install -r requirements.txt"'

_, output = commands.getstatusoutput(cmd)
print '\n', output, '\n'

# Now virtualenv exists

# Run 'cpvirtualenv PROJECT_NAME default' ?
#if ask_to_copy_default_virtualenv:
#    q = "Create a default virtualenv to speed this up next time? " % PROJECT_NAME
#    answer = raw_input(q)
#    if answer and answer.lower()[0] == 'y':
#        print "Copying virtualenv..."
#        cmd  = 'bash -c "source /usr/local/bin/virtualenvwrapper.sh && workon '
#        cmd += '%(PROJECT_NAME)s && cpvirtualenv %(PROJECT_NAME)s default --no-site-packages"' % \
#            replacement_values
#        _, output = commands.getstatusoutput(cmd)
#        print '\n', output, '\n'

print "Creating git repo..."
cmd  = 'bash -c "cd %s &&' % PROJECT_PATH
cmd += ' git add . && git commit -m \'First commit\'"'
_, output = commands.getstatusoutput(cmd)
print '\n', output, '\n'

print "Done! Now run\n"
print "    cd %(PROJECT_PATH)s && workon %(PROJECT_NAME)s &&" % replacement_values,
print "python manage.py syncdb\n\nGet to work!"
