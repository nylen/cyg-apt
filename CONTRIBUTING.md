Contributing
------------

Cyg-apt is an open source, community-driven project. All code contributions - including those of people having commit access - must go through a pull request and approved by a core developer before being merged. This is to ensure proper review of all the code.

If you would like to help take a look at the [list of issues](https://github.com/nylen/cyg-apt/issues).

Fork the project from [github.com/nylen/cyg-apt][0], create a feature branch, and send us a pull request.

Please follow the guidelines:

  - To ensure a consistent code base, you should make sure the code follows the [Coding Standards](CONVENTIONS.md);

  - Add unit tests to prove that the bug is fixed or that the new feature actually works;

  - Try hard to not break backward compatibility (if you must do so, try to provide a compatibility layer to support the old way) -- patches that break backward compatibility have less chance to be merged;

  - Never fix coding standards in some existing code as it makes the code review more difficult;

  - The pull request description must include the following checklist at the top to ensure that contributions may be reviewed without needless feedback loops and that your contributions can be included into cyg-apt as quickly as possible:

    ```
    | Q               | A
    | --------------- | ---
    | Bug fix?        | [yes|no]
    | New feature?    | [yes|no]
    | BC breaks?      | [yes|no]
    | Deprecations?   | [yes|no]
    | Tests pass?     | [yes|no]
    | Related tickets | [comma separated list of tickets related by the PR]
    | License         | GNU GPL v3

    ```

    If the code is not finished yet because you don't have time to finish it or because you want early feedback on your work, add an item to todo-list:

    ```
    - [ ] finish the code
    - [ ] gather feedback for my changes
    ```

    As long as you have items in the todo-list, please prefix the pull request title with `[WIP]`.


Thank you.


[0]: https://github.com/nylen/cyg-apt
