#!/bin/bash
#
# Create GIT-version tags in the associated projects from the version number as defined in pyproject.toml
#
#
function proceed_yes_no() {
	read -p "Do you want to proceed (y/n)? " ANSWER
	case ${ANSWER:0:1} in
	    y|Y )
	        echo Proceeding
	        return 0
	    ;;
	    * )
	        echo Aborting
	        return 1
	    ;;
	esac
}

function check_version_tag_present_in_project() {
	PROJECT_NAME=$1
	VERSION_TAG=$2
	echo ""
	echo "Going to delete version tag $VERSION_TAG for project $PROJECT_NAME."
	echo ""
	git -C /home/$USER/git/$PROJECT_NAME/ tag --list | grep -q $VERSION_TAG
	IS_TAG_PRESENT=$?
	
	if [ $IS_TAG_PRESENT == 0 ]; then
		return 0
	fi
	return 1
	
}


TAG_VERSION=`cat /home/$USER/git/aumc-deduce/pyproject.toml | grep 'version =' | cut -d '=' -f2 | tr -d ' ' | tr -d '"'`
TAG_VERSION=`echo "v$TAG_VERSION"`
echo "Going to delete Git version tags with the following value: $TAG_VERSION as defined in the pyproject.toml file."

if ! proceed_yes_no; then
	exit 1
fi

( "/home/$USER/git/aumc-deduce/scripts/check-correct-branch-checked-out.sh" )
BRANCHES_CORRECT=$?

echo ""
if [ $BRANCHES_CORRECT != 0 ]; then
	
	echo "Incorrect checked out branches found. Please correct this manually before attempting to delete version tags."
	echo ""
	exit 2
fi
echo "Correct branches checked out. Proceeding"
echo ""


if (check_version_tag_present_in_project "aumc-deduce" $TAG_VERSION); then
	git -C /home/$USER/git/aumc-deduce/ tag --delete $TAG_VERSION
	git -C /home/$USER/git/aumc-deduce/ push --delete origin $TAG_VERSION
fi

if (check_version_tag_present_in_project "aumc-deduce-conf" $TAG_VERSION); then
	git -C /home/$USER/git/aumc-deduce-conf/ tag --delete $TAG_VERSION
	git -C /home/$USER/git/aumc-deduce-conf/ push --delete origin $TAG_VERSION
fi

if (check_version_tag_present_in_project "aumc-deduce-supplements" $TAG_VERSION); then
	git -C /home/$USER/git/aumc-deduce-supplements/ tag --delete $TAG_VERSION
	git -C /home/$USER/git/aumc-deduce-supplements/ push --delete origin $TAG_VERSION
fi



echo "Finished deletions of the version tag"

