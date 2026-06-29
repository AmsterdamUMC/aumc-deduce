#!/bin/bash
#
# Checks if the associated projects (aumc-deduce, aumc-deduce-conf and aumc-deduce-supplemental) have 
# the correct branches checked out.
# The branches are:
# 	aumc-deduce: checks in the pyproject.toml. If it contains a release candidate (rcXXXX) the the branch must be
#                "release-X.Y.Z""
#   aumc-deduce-conf: "non-confidential"
#   aumc-deduce-supplemental: "main"
#
# returns an exit value 0 if the all the branches are as expected


EXPECTED_RELEASE_BRANCH_AUMC_DEDUCE_CONF="non-confidential"
EXPECTED_RELEASE_BRANCH_AUMC_DEDUCE_SUPPLEMENTAL="main"


function is_branch_as_expected() {
	DIRECTORY=$1
	EXPECTED_BRANCH=$2
	
	CURRENT_BRANCH=`git -C $DIRECTORY branch -a  | grep "*" | cut -d " " -f2`

	if [ $CURRENT_BRANCH == $EXPECTED_BRANCH ]; then 
		echo "Correct branch found in project: $DIRECTORY: \"$CURRENT_BRANCH\"" 
		return 0
	fi
	echo "Unexpected branch found in project: $DIRECTORY. Expected: \"$EXPECTED_BRANCH\" but branch was: \"$CURRENT_BRANCH\"."
	return 1
}

VERSION_FROM_PYPROJECT=`cat /home/$USER/git/aumc-deduce/pyproject.toml | grep 'version =' | cut -d '=' -f2| tr '"' ' ' `
BASE_LIST=(`echo $VERSION_FROM_PYPROJECT | tr '-' ' '`)
VERSION_LIST=(`echo ${BASE_LIST[0]} | tr '.' ' '`)
VER_MAJOR=${VERSION_LIST[0]}
VER_MINOR=${VERSION_LIST[1]}
VER_PATCH=${VERSION_LIST[2]}

grep -qi "rc" <<< ${BASE_LIST[1]}
IS_RC=$?

#if [ $IS_RC == 0 ]; then
EXPECTED_RELEASE_BRANCH_AUMC_DEDUCE="release-$VER_MAJOR.$VER_MINOR.$VER_PATCH"
#else
#	EXPECTED_RELEASE_BRANCH_AUMC_DEDUCE=""
#fi




EXIT_VALUE=0

is_branch_as_expected "/home/$USER/git/aumc-deduce/" $EXPECTED_RELEASE_BRANCH_AUMC_DEDUCE
EXIT_VALUE=$((EXIT_VALUE+$?))


is_branch_as_expected "/home/$USER/git/aumc-deduce-conf/" $EXPECTED_RELEASE_BRANCH_AUMC_DEDUCE_CONF
EXIT_VALUE=$((EXIT_VALUE+$?))


is_branch_as_expected "/home/$USER/git/aumc-deduce-supplements/" $EXPECTED_RELEASE_BRANCH_AUMC_DEDUCE_SUPPLEMENTAL
EXIT_VALUE=$((EXIT_VALUE+$?))



exit $EXIT_VALUE 