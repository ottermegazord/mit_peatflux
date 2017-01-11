#!/bin/bash
PKG=sungrow
NAMES=`find ${PKG} -name '*.py'`
echo "-------------------------- running pylint --------------------------"
pylint -E ${PKG}
echo "--------------------------running nosetests ------------------------"
nosetests -s $@
exit
