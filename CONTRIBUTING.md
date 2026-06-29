# Contributing

Thanks for considering making an addition to this project! These contributing guidelines should help make your life easier. 

Before starting, some things to consider:
* For larger features, it would be helpful to get in touch first (through issue/email)
* A lot of the logic is in `docdeid`, please consider making a PR there for things that are not specific to `deduce`.
* `deduce` is a rule-based de-identifier
* In case you would like to see any rules added/removed/changed, a decent substantiation (with examples) of the potential improvement is useful

## Setting up the environment

* This project uses poetry for package management. Install it with ```pip install poetry```
* Set up the environment is easy, just use ```poetry install```
* The makefile contains some useful commands when developing:
  * `make format` formats the package code
  * `make lint` runs the linters (check the output)
  * `make clean` removes build/test artifacts, etc
* And for docs:
  * `make build-docs` builds the docs

## Runing the tests
### Unit tests
The command below runs all the unit tests including line coverage. The expected coverage percentage can be specified in `pyproject.toml` in the `[tool.pytest.ini_options]` section. Please ensure that this coverage is maintained or even better improved.
```bash pytest .```
### Regression tests
Two files contain regression tests. These files checks if the text in raw unaonynimised clinical notes matches the expected output after
`deduce` anonymisation. The two files are: `input-output-test.tsv` and `input-output-test.tsv`. In the `scripts` directory there is a bash script
which runs both the unit and the regression test. This script ought to be run prior to commiting any code modifications.
```bash ./scripts/run-dev-test.sh```

Both files include dummy patient personal data which allows testing combination of clinical note text in combination with personal data provided
to `deduce`. 

## Version & branch mangement
A number of scripts are available for version and branch admistration. These are located in the `scipts` directory. The branch managment strategy
in `deduce` is based on [A successful Git branching model](https://nvie.com/posts/a-successful-git-branching-model/). Separate feature and release 
branches are used to allow parallel development with in a team of developers. Each feature branch when finished must be merged back into the `develop` 
branch. Once that branch is ready to be released / promoted to another envionment a separte `release` branch should be created. The steps needed are 
describe below.

### Release branch creation
1. Edit the file VERSION.txt and bump the version numbers.
2.  

## PR checlist

* Verify that tests are passing
* Verify that tests are updated/added according to changes
* Run the formatters (`make format`)
* Run the linters (`make lint`)
* Add a section to the changelog
* Add a description to your PR

If all the steps above are followed, this ensures a quick review and release of your contribution. 

## Releasing
* Readthedocs has a webhook connected to pushes on the main branch. It will trigger and update automatically. 
* Create a [release on github](https://github.com/vmenger/docdeid/releases/new), create a tag with the right version, manually copy and paste from the changelog
* Build pipeline and release to PyPi trigger automatically on release

Any other questions/issues not covered here? Please just get in touch!