# Limited public checks

These checks provide a few debugging checkpoints, not complete verification.
Derive results, test your own cases, and explain frames, shapes, and units.
Each homework builds on your implementations from earlier homework.

From a course-container shell in `/workspace`, run just the current stage:

```text
python -m unittest discover -s tests/public -p "test_hw02_*.py" -v
```

Replace `02` with `03`, `04`, or `05`. The activity modules run the same
stage's checks and can open a supplied visualization; see STUDENT_GUIDE.md.
The initial scaffold intentionally raises homework-labeled
`NotImplementedError` exceptions. Later-stage checks remain incomplete until
those assignments and their prerequisites are implemented. A passing public
check is not a substitute for a hand derivation or additional cases.
