#!/bin/bash

MODULE_NAME=legocollector
SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJ_MAIN_DIR=$SCRIPT_PATH/../..
MODULE_PATH=$PROJ_MAIN_DIR/$MODULE_NAME

echo SCRIPT_PATH: $SCRIPT_PATH
echo PROJ_MAIN_DIR: $PROJ_MAIN_DIR
echo MODULE_PATH: $MODULE_PATH

export PYTHONPATH=$PYTHONPATH:$MODULE_PATH

# Pylint has an issue finding the modules since there is not __init__.py in the django root, if it were it causes issues with django test discovery
#pylint --load-plugins pylint_django "$MODULE_PATH"
find . -type f -name "*.py" | xargs pylint --load-plugins pylint_django
return_code=$?

if [[ $return_code -eq  0 ]];
then
    echo "*** No Issues Found"
else
    echo "*** Some Issues Found"
fi

echo "exit $return_code"
exit $return_code
