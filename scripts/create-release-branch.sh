!/bin/bash
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
# 4) create a version tag on the 3 projjects involved: aumc-deduce, aumc-deduce-conf and aumc-supplements
#
#
#
# TODO discuss with team if we have to follow a deveop & release branching strategy for the associated projects aumc-deduce-conf and aumc-deduce-supplements
# or only use a simliar version tag across these 2 projects
# Add a separate script to create the version tags in the 3 associated projects'
