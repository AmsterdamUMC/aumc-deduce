#!/bin/bash
#
# Script to run all the unit- and regression-tests of DEDCUE.

# The unit tested have the coverage turned on per default. The coverage
# can be turned off by adding --no-cov
#
# This script must be run prior to any commit in all the related projects:
# aumc-deduce, aumc-deduce-conf and aumce-deduce-supplemental. In the future
# a pre-commit hook can be added to these projects which calls this script.

RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET_COLOUR=`tput sgr0`

function return_message_pytest() {
	echo "$1 = "
	case $1 in	
		0)
			echo -n "${GREEN}Passed${RESET_COLOUR}"
			;;
		1)
			echo -n "${RED}Failed${RESET_COLOUR}"
			;;
		2)
			echo -n "Aborted by user"
			;;
		3)
			echo -n "Internal error happend while executing tests"
			;;
		4)
			echo -n "Pytest commandline usage error"
			;;
		5)
			echo -n "No tests collected"
			;;
		*)
			echo -n "${RED}Other failure${RESET_COLOUR}"
			;;
	esac
}

pytest --verbosity 3  --cache-clear /home/$USER/git/aumc-deduce/tests
UNIT_TEST_RESULT=$?


pytest --cache-clear --no-cov -s -vv /home/$USER/git/aumc-deduce/tests/validation.py::TestValidationFile::test_prefix_names
PREFIX_TEST_RESULT=$?

pytest --cache-clear --no-cov -s -vv /home/$USER/git/aumc-deduce/tests/validation.py::TestValidationFile::test_with_validation_file
REGRESSION_TEST_RESULT=$?

echo "===================================="
echo ""
echo "Overall test-result"
echo ""
echo "Unit-tests     : " `return_message_pytest $UNIT_TEST_RESULT`
echo "Prefix-test    : " `return_message_pytest $PREFIX_TEST_RESULT`
echo "Regression-test: " `return_message_pytest $REGRESSION_TEST_RESULT`
echo ""
echo "===================================="
