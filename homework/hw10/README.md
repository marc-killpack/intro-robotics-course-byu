# HW10: learning to classify when rules fail

Complete `train_epoch`, `predict`, and `confusion_matrix` in
`homework/hw10/learning.py`. Your HW08 `find_objects` must work (it is the
rule classifier you compare against). The data generator (`dataset.py`),
the network (`model.py`), the three scripts, and a trained fallback
checkpoint (`checkpoints/cnn.pt`) are provided.

In a course-container shell at `/workspace`:

```text
python -m unittest tests.public.test_hw10_learning
python -m homework.hw10.hw10_data --save tmp/hw10_data.png
python -m homework.hw10.hw10_train
python -m homework.hw10.hw10_evaluate --save tmp/hw10_eval.png
```

The first script run generates the crops (a few seconds) and keeps them in
`tmp/hw10/`. Training runs on the CPU in a minute or two and saves
`tmp/hw10/cnn.pt`; `hw10_evaluate` uses it, or the supplied checkpoint if
you pass `--checkpoint homework/hw10/checkpoints/cnn.pt`.
