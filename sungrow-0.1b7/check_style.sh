#!/bin/bash
PKG=sungrow
NAMES=`find ${PKG} -name '*.py'`
echo "--------------------------- running pylint -------------------------"
pylint ${PKG} --rcfile=.pylintrc
echo "--------------------------- running pep8 ---------------------------"
pep8 --repeat --statistics ${NAMES}
echo "------------------ running nosetests --with-coverage ---------------"
nosetests --cover-erase --with-coverage --cover-package=${PKG} $@
echo "------------ displaying html coverage results using firefox --------"
coverage html --omit='/usr/*,test/*' && firefox file://`pwd`/htmlcov/index.html
exit
