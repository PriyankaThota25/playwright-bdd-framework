## Summary

<!-- What does this PR change, and why? -->

## Self-review checklist

Tick every box before requesting review.

### Coding standards
- [ ] Code follows the existing style and naming of the surrounding files
- [ ] Locators live in page objects under `pages/`, not in step definitions
- [ ] Step definitions are thin and call page object methods
- [ ] Reusable steps and fixtures are in `conftest.py`, not duplicated
- [ ] Type hints are added to new functions
- [ ] No hardcoded credentials, URLs or test data. Test data is in `test_data/` or `config/`
- [ ] No commented-out code, debug prints or unused imports

### No impact on existing code
- [ ] Existing page objects, steps and fixtures were not changed, or any change was checked against the scenarios that use them
- [ ] The full suite passes locally (`pytest`), not just the new scenario
- [ ] New scenarios are independent and clean up after themselves (for example, delete created accounts)
- [ ] No existing feature files or scenarios were modified unintentionally

### Tests and reporting
- [ ] New scenarios are tagged correctly (`@smoke`, `@e2e`) and any new tag is registered in `pytest.ini`
- [ ] No flaky waits (`time.sleep`). Playwright auto-waiting or explicit waits are used
- [ ] `requirements.txt` is updated if a dependency was added

## Testing done

<!-- Commands you ran and the results, e.g. `pytest -m smoke` -->
