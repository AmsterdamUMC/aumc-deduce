#!/bin/bash
#
# Creates a release branch for an upcoming release of DEDUCE
#
# Parts of the code are based on: https://gist.github.com/pete-otaqui/4188238
# The steps performed by this scripts are:
# 1) input of the upcoming release id in the format: <MAJOR>.<MINOR>.<PATCH> based on the previous version stored in pyproject.toml
# 2) check if the correct branches are checked out in the projects
# 3) run all the tests and if failure then aborts this script
# 2) creation of a branch in the aumc-deduce project with that release id called 'release-X.Y.Z'
# 3) change of the version number in the pyproject.toml with the release id and a release candidate follow-up number of 1
#
#
#
# TODO discuss with team if we have to follow a deveop & release branching strategy for the associated projects aumc-deduce-conf and aumc-deduce-supplements
# or only use a simliar version tag across these 2 projects
# Add a separate script to create the version tags in the 3 associated projects'

TAG_VERSION=`cat /home/$USER/git/aumc-deduce/VERSION.txt`
TAG_VERSION=`echo "$TAG_VERSION"`
BRANCH_NAME=`echo "release-$TAG_VERSION"`

echo "Tag version specified in VERSION.txt: $TAG_VERSION"

# Note: git branch does support the -C ( work across directories) option
git branch --list | grep -q "$BRANCH_NAME"

IS_BRANCH_ALREADY_PRESENT=$?

if [ $IS_BRANCH_ALREADY_PRESENT == 0 ]; then
	echo "Branch $BRANCH_NAME is already present. Skipping branch creation"
	git checkout $BRANCH_NAME
else
	echo "Tag $BRANCH_NAME is not yet present. Creating branch"
	git checkout -b $BRANCH_NAME
	
fi

# Count the number of version tags present as git version tags 
# to determine the next release candidate follow-up number

RELEASE_CANDIDATE_COUNT=`git tag --list | grep "$TAG_VERSION-rc" | wc -l`
echo "Number of release candidates for version $TAG_VERSION: $RELEASE_CANDIDATE_COUNT"
RELEASE_CANDIDATE_COUNT=$((RELEASE_CANDIDATE_COUNT+1))
NEW_RELEASE_CANDIDATE_TAG=`echo $TAG_VERSION-rc$RELEASE_CANDIDATE_COUNT`
echo ""
read -p "Do you want to create a new release candidate: $NEW_RELEASE_CANDIDATE_TAG? (y/n)" ANSWER
case ${ANSWER:0:1} in
	y|Y )
		echo "Creating release candidate with tag: $NEW_RELEASE_CANDIDATE_TAG"
		# replace the release candidate tag in the pyproject file
		CURRENT_VERSION=`cat /home/$USER/git/aumc-deduce/pyproject.toml | grep 'version =' | cut -d '=' -f2| tr '"' ' ' | tr -d ' '`
		echo "Replacing $CURRENT_VERSION in pyproject.toml with: $NEW_RELEASE_CANDIDATE_TAG"
		CURRENT_VERSION="version = \"$CURRENT_VERSION\""
		NEW_RELEASE_CANDIDATE_TAG="version = \"$NEW_RELEASE_CANDIDATE_TAG\""
		sed -i -e "s/$CURRENT_VERSION/$NEW_RELEASE_CANDIDATE_TAG/g" /home/$USER/git/aumc-deduce/pyproject.toml
		
		# Run poetry install to ensure that the poetry.lock file matches the version tag specified in the pyproject.toml
		poetry install
	;;
	* )
		echo "Skipped creating release candidate ..."
NEW_RELEASE_CANDIDATE_TAG ;;
esac
#



