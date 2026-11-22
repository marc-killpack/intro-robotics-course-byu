# HW10 faculty reference: learning to classify when rules fail

Draft reference for the November 20 guided lab; not yet reviewed or
released. The completed functions are the marked regions of
`homework/hw10/learning.py`. Numbers are from the faculty laptop (8 CPU
threads, PyTorch 2.15.0+cpu, OpenCV 4.14); the data are deterministic.

1. **Data.**
   (a) Train 14,400 crops from 2,400 scenes; validation 1,800 from 300; test
   3,600 from 600 (6 frames per scene; 75--77% hard in each split; 241--291
   scenes per class in training). Images `(14400, 48, 48, 3)` `uint8`, 0--255.
   A batch after `to_tensor` is `(64, 3, 48, 48)` `float32` in 0--1: batch
   index, color channel (R, G, B), image row, image column. PyTorch's
   convolutions expect channels before rows and columns.
   (b) Too high. A scene's crops are near copies, so a network that has
   memorized one frame recognizes the others without having learned anything
   that transfers; the test set no longer measures performance on new scenes.
   The same applies to video in general: split by recording, not by frame.
   (c) Any three, for example: a light change or color cast moves object
   pixels outside the fixed RGB tolerance (threshold: no detection, or a
   fragment); uneven light does the same over part of the object
   (threshold); heavy noise breaks the mask into speckles (threshold and
   contour); blur rounds the corners (corner count: squares and triangles
   become circles); an occluding bar splits the object or adds straight edges
   (contour and corner count); an off-center crop can cut the object at the
   crop border (contour: `whole` rejects it, so nothing is found).
2. **Training step.**
   (a) `p = (0.705, 0.259, 0.035)`; loss `0.349` for true class 0 and
   `3.349` for true class 2. The loss grows without bound as the true class's
   probability goes to zero, so a confident mistake produces a large loss and
   large gradients, while an unsure answer costs about `ln 9 = 2.2` for 9
   classes.
   (b) `scores = model(images)`, `loss = loss_fn(scores, labels)`,
   `optimizer.zero_grad()`, `loss.backward()`, `optimizer.step()`, then
   `losses.append(loss.item())`.
   `backward` computes the gradient of the loss with respect to every weight
   (backpropagation, the chain rule through the layers) and stores it in each
   parameter's `.grad`. PyTorch *adds* new gradients to `.grad`; without
   `zero_grad` each step would use the sum of all previous batches' gradients.
   (c) Seed 0, 5 epochs (59 s here):

   | Epoch | Loss | Validation clean | Validation hard |
   | --- | --- | --- | --- |
   | 1 | 0.683 | 99.3% | 83.5% |
   | 2 | 0.138 | 100.0% | 95.1% |
   | 3 | 0.045 | 100.0% | 94.7% |
   | 4 | 0.027 | 100.0% | 96.2% |
   | 5 | 0.016 | 100.0% | 96.3% |

   14,400 / 64 = **225 optimizer steps** per epoch. The training loss keeps
   falling whether or not the network is still improving on new scenes (from
   epoch 2 to 3 the loss fell by two thirds while hard validation accuracy
   dipped); only scenes it never trained on show how it will do on new ones.
3. **Evaluation.**
   (a) `eval()` makes batch normalization use the running statistics saved
   during training instead of the current batch's (so a prediction does not
   depend on which other images share its batch). `no_grad()` skips building
   the gradient graph, which saves memory and time and guarantees nothing is
   learned from the test set.
   (b) Supplied checkpoint (the same seed-0, 5-epoch training):

   | Classifier | Clean (906 crops) | Hard (2,694 crops) |
   | --- | --- | --- |
   | Network | 100.0% | 97.0% |
   | HW08 rules | 100.0% | 40.1% (nothing found in 32.3%) |

   Retraining with seeds 1 and 2 gave 97.1% and 97.3% on hard crops, and a
   sixth epoch with seed 0 gave 96.9% (100% on clean in every case), so more
   epochs buy nothing here. The rules' largest confusions are squares and
   triangles called circles (red square as red circle, 91; yellow triangle as
   yellow circle, 85; blue square as blue circle, 72).
   (c) Color survives because the three colors are far apart in RGB: a light
   change may push pixels *out* of the right color's tolerance (nothing
   found), but rarely *into* another color's. Shape depends on a clean
   outline, which blur, noise, and occlusion destroy, and an object that
   fails the threshold is not found at all. The network's few mistakes are
   mostly an occluding bar across a square or triangle, often with dim or
   tinted light, and they come in runs from the same scene.
   (d) On S1--S3 the rules are perfect, explainable, need no training, and
   are what the reference controller uses, so they are the sensible choice;
   the network would matter if the project added lighting changes, blur,
   occlusion by the arm, or a camera with noise (a second-round option).
   Missing before a real camera: real lighting and shadows, lens distortion
   and focus, sensor noise and compression, object textures and wear, real
   backgrounds, and labeled real images to test on.

Workload target: three to four hours. Pilot the training time on student
laptops (and in the container) alongside HW11.
