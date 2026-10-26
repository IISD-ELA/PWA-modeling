# Contributors page

⚠️ Under Construction ⚠️

If you are interested in contributing to this project, please contact Thomas Saleh at tsaleh@iisd-ela.org or the ELA Data team at eladata@iisd-ela.org with PWA-CODE-CONTRIBUTION in the e-mail title.

Workflow for adding a feature or fixing a bug:

1. **Create a feature branch** off the default branch in the relevant repo (`main` for pwa-tools and the orchestrator, `master` for PWA). Use `feat/<short-name>` for features and `fix/<short-name>` for bug fixes — never commit directly to the default branch.
2. **Write a failing test first** that describes the desired behavior. Run `python -m pytest -q` to confirm the new test fails. For bug fixes, the test should reproduce the bug.
3. **Write code to make the test pass.** Run the suite again and confirm green.
4. **Commit incrementally** with focused commit messages that explain *why* (the motivation, the problem, the trade-off) rather than just *what* (the diff is the *what*).
5. **Open a pull request** against the default branch. Tag the relevant reviewer. The PR description should include a short summary, a test plan, and links to any related issues.

Practical notes:

- New features should ship with corresponding tests. If a unit test is hard to write, that's often a signal the design needs refactoring.
- Avoid disabling, skipping, or commenting out tests to make builds pass — investigate the root cause and fix it properly.
- Keep commits small and atomic. If you find yourself making unrelated changes in the same commit, split them.
- Don't add features beyond what the issue/PR scope requires. YAGNI — build for the current need, refactor later when a second use case emerges.
