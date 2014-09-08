Contributing
------------

Cyg-apt is an open source, community-driven project. All code contributions -
including those of people having commit access - must go through a pull request
and be approved by a core developer before being merged. This is to ensure
proper review of all the code.

If you would like to help, take a look at the
[list of issues](https://github.com/nylen/cyg-apt/issues).

Fork the project from
[github.com/nylen/cyg-apt](https://github.com/nylen/cyg-apt), create a feature
branch, and send us a pull request.

Please follow these guidelines for any contributions:

  - To ensure a consistent code base, you should make sure the code follows the
    [Coding Standards](CONVENTIONS.md) for the project;

  - Add unit tests to prove that the bug is fixed or that the new feature
    actually works;

  - Try hard not to break backward compatibility (if you must do so, try to
    provide a compatibility layer to support the old way) -- patches that break
    backward compatibility have less chance to be merged;

  - Patches to fix coding standards in existing code are welcome, but don't fix
    coding standards along with other changes because it makes the code review
    more difficult;

  - The pull request description must include the following checklist at the
    top to ensure that contributions may be reviewed without needless feedback
    loops and that your contributions can be included into cyg-apt as quickly
    as possible:

    ```
    | Q               | A
    | --------------- | ---
    | Bug fix?        | [yes|no]
    | New feature?    | [yes|no]
    | BC breaks?      | [yes|no]
    | Deprecations?   | [yes|no]
    | Tests pass?     | [yes|no]
    | Related tickets | [comma separated list of tickets related by the PR]
    | License         | GNU GPLv3

    ```

    If the code is not finished yet because you don't have time to finish it or
    because you want early feedback on your work, add a
    [task list](https://help.github.com/articles/writing-on-github#task-lists):

    ```
    - [ ] finish the code
    - [ ] gather feedback for my changes
    ```

    As long as you have unfinished items in the task list, please prefix the
    pull request title with `[WIP]`.


Thank you for contributing.
