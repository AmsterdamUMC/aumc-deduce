### Release management AmsterdamUMC
This document describes the steps needed to ensure consistent release management across the 3 project of the AmsterdamUMC
version of DEDUCE: `aumc-deduce`, `aumc-deduce-conf` and `aumc-deduce-supplements`. For privacy and information security
reasons only the aumc-deduce is a public project on Github. Please contact the developers (Tom Welter or Jacob Rousseau) in case you
want information on the other projects.
The intended audience of this document are the AmsterdamUMC developers, technical and functional administrators involved in the maintenance 
and running of the applications

### Branch based development
AmsterdamUMC Deduce uses a branch based development strategy with the following branch types: main, develop, feature and release.
This strategy is described in the document: [A successful Git branching model](https://nvie.com/posts/a-successful-git-branching-model/) by Vincent Driessen.

The main branch is a fork of the original Deduce code made by Vincent Menger. [Menger, V.J., Scheepers, F., van Wijk, L.M., Spruit, M. (2017). DEDUCE: A pattern matching method for automatic de-identification of Dutch medical text, Telematics and Informatics, 2017, ISSN 0736-5853](http://www.sciencedirect.com/science/article/pii/S0736585316307365).

The develop branch contains the non released code. From the development branch individual developers must split off feature branch which will contain the
change needed to implement a feature. The naming of feature branches must contain the JIRA ID of the item which describes the functionality, reason of the
feature, for example `RDMD-99-Version-Administration`. Once a feature is complete it is merged back into the development branch.

A release branch is split of from the development branch at the moment a new release is about to be released. At this moment a new version tag is created with
a released candidate post fix. E.g. **v4.5.6-rc1**. Any changes stemming from issues found while testing the new release are performed in the release candidate branch
and not in the development branch. This allows parallel development by different team members. Once these issues are resolved a new release candidate is produced with and increment in the ordinal of the version tag of the release candidate.
The release branch is merged back into the development branch only when a release is finalized and deployed on the production environment.

### DTAP environments (Development, Test, Acceptance, Production)
Similarly to industry standards a strict segregation of environments is used in an attempt to safeguard information. Python env files are used to
denote the environments and to describe the environment specific setting needed to start and monitor Deduce runs.

The main python sscript which starts the various run types is called **rundeduce.py** and is found in the aumc-deduce-supplements project. This scripts makes use of an command-line parameter **--dtap** to set the environment type. The currently allowed values are: **dev**, **test**, **accept** or **prod**. Additional environments can be added later on.
Specific sets of enviroment files are loaded depending on the environment type and run-type:

Development: sf_tables.env

The environment parameters in each of these scripts are:
<table>
<tr><th>Parameter</th><th>Description</th></tr>
<tr><td>SF_USER</td><td> User account for the connection between Snowflake and Deduce, for use see the method InitEnvs in deducerun.py</td></tr>
<tr><td>SF_WAREHOUSE</td><td> The Snowflake warehouse used</td></tr>
<tr><td>SF_SECRETSDIR</td><td> A directory containing a RSA key with which the connection is secured. Development environments the developers home directory is used</td></tr>
<tr><td>SF_ROLE</td><td> The Snowflake role specific for the DTAP environment</td></tr>
<tr><td>SF_PLAINDB</td><td>  **TODO Ask Tom**</td></tr>
<tr><td>SF_PLAINSCHEMA</td><td>  **TODO Ask Tom**</td></tr>
<tr><td>SF_PLAINTABLE</td><td> **TODO Ask Tom**</td></tr>|
<tr><td>SF_DEDUCEDDB</td><td> **TODO Ask Tom**</td></tr>
<tr><td>SF_DEDUCEDSCHEMA</td><td>  **TODO Ask Tom**</td></tr>
<tr><td>SF_DEDUCEDTABLE</td><td> **TODO Ask Tom**</td></tr>
<tr><td>DEDUCE_CONFDIR</td><td> Path where the configuration files for the run can be found (aumc_deduce.conf)</td></tr>s
</table>

afasd