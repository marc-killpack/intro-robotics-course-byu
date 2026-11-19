# Reviewed student copies

This repository contains completed faculty masters. The current draft
manifest covers **HW01--HW05**: 53 explicitly selected files and 11 marked
answer regions (two ROS methods and nine mathematical methods). It includes
the supplied arm/drawing code and limited `tests/public` checks. It excludes
the DH adapter, camera/conveyor prototypes, instructor files/tests, LaTeX,
and generated PDFs. Faculty approval is still pending.

From the repository root, preview the current work without publishing:

```text
python -m release_tools --dry-run
```

The tool prepares every allowlisted file in memory, validates exact paired
`# BEGIN SOLUTION` / `# END SOLUTION` markers, removes answer regions from
copied Python only, parses that Python, checks local Markdown links, and
creates/discards a temporary student tree. It prints source revision, dirty
state, input hashes, file count, and removed-block count. A dirty preview is
allowed for review; it is not a publishable release record.

After faculty review, commit the intended source and confirm that
`git status --short` is empty. Create a new, separate review copy:

```text
python -m release_tools release_output/foundations-review
```

The destination must not already exist. A faculty JSON report is written
beside it, outside the student tree. Source changes are never stripped in
place. A review copy inside this repository must be under `release_output/`.
The command never publishes or modifies a remote repository.

Before publication:

1. Confirm clean source and the intended revision in the report.
2. Inspect the methods in [the faculty boundary map](../HOMEWORK_MAP.md):
   each must retain guidance and a homework-labeled `NotImplementedError`,
   with no completed answer body. Check that all 11 regions were removed.
3. Check the promoted student README, setup links, and launch-mode directions.
4. Test the completed masters separately. Confirm generated imports resolve
   to the student tree and assigned methods fail with their expected labels.
   Public checks should pass only as students implement each cumulative stage.
5. Review every handout PDF built under `docs/homework/build/hwNN/`;
   distribute the approved PDFs separately. The manifest copies no faculty PDFs.
6. Deliberately publish the inspected copy using the chosen semester workflow.

Python tests cover marker failures, input traversal, source preservation,
refusal to overwrite, the clean-source gate, the actual cumulative allowlist,
generated-tree imports, all mathematical stubs, and provided frame drawing.
Notebook release support is intentionally deferred until an assignment needs
it; `.ipynb` files are rejected rather than copied with possible answers.

Review the current supplied/assigned boundaries before publication. Apply
the same review before adding later exercises; keep the public scaffold small
and preserve the separate faculty implementation/test boundary.

