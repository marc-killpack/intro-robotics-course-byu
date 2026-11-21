# HW10 faculty draft: learning to classify when rules fail

Built November 20 (TASKS.md D3: a short guided lab, about three to four
hours). Students inspect generated 48 by 48 object crops from the project's
fixed camera, complete the training step (`train_epoch`), `predict`, and a
confusion matrix, train a small CNN on the CPU (5 epochs, about a minute),
and compare it on held-out scenes with their HW08 rule classifier. Three
quarters of the scenes are deliberately *hard* (light level and color cast,
uneven light, blur, heavy noise, an occluding bar, off-center crops), so
learning matters: the rules score 100% on clean crops but 40% on hard ones,
the network 100% and about 97%. Scenes are six consecutive frames, and splits
are by scene; the handout asks why.

Student files: `homework/hw10/` (`learning.py` with three marked answers;
supplied `dataset.py`, `model.py`, `hw10_data.py`, `hw10_train.py`,
`hw10_evaluate.py`, `checkpoints/cnn.pt`, README). Public check:
`tests/public/test_hw10_learning.py` (tiny synthetic data); instructor
checks: `tests/instructor/test_hw10_learning.py` (repeatable data and
disjoint splits, the rule-versus-network gap with the supplied checkpoint,
one epoch of training with the key, stripped stubs). Key:
[HW10 reference](../../../instructor/HW10_REFERENCE.md).

Release note: needs the learning packages (in the course image since Nov
20) and what HW08 already released: `vision.py`, the project's `scenario`
and `simulator` modules, and `homework/hw08/hw08_scenario.toml` (the
generator reads its camera and colors there, so the project scenario folder
stays unreleased). The supplied checkpoint is 0.7 MB.

Build: `python docs/homework/build_pdfs.py hw10 --render`. Pilot the
training time on student laptops with HW11.
