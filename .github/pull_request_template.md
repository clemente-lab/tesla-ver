---
name: Pull Request Form
about: Fill this out for your pull request

---

## Issues Addressed
Link to any issues this pull request addresses

## What has changed
Include each file that was changed, how it was changed (in broad terms), and why it was changed.
Example:
    mmeds/server.py:
        upload_metadata(): Added additional parameter to allow for uploading partial metadata

## Checklist of pre-requisites
All of these need to be checked in order to request a review on the Pull Request
-   [ ] Does the code run?  
-   [ ] Does the code follow the repository style?  
-   [ ] Is the code tested?  
-   [ ] Has Black been run on all the python files in the repository (with line length 120 `black -l 120 *`)?


## If the user interface was modified include screenshots here

## Additional notes

## Pull Request Types
The following sections are specific to the three types of PRs. Enhancement, Bug Fix, and Design Change after determining the type of your PR delete the questions related to the other two.

# Bug Fix

## Describe or link to the issue that was fixed.

## What is the new behavior?
Example: Only numeric columns appear as options for selecting the size of the dots

# Enhancement

## How to use the feature
Example: To do X run new function Y with parameters A, B, and C which gives result Z.

## If the user interface was modified include screenshots here

# Design Change

## How has the design changed?
Example: Functions A, B, and C are now all methods of Class D.

## Why that change was necessary?
Example: Previously 5 different functions were passing around A, B, and C as inputs. Changing these to methods reduced complexity.
