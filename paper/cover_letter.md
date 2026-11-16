# Cover letter (draft)

[DATE]

To the Editors, Computers & Geosciences

Dear Editors,

We submit the manuscript "Identifiability before interpretation: an inverse-crime test of
physics-informed petrophysical inversion across 625 wells of Mississippian chat" for
consideration as a research paper.

Physics-informed neural networks are increasingly proposed for well-log interpretation without
core labels. We built such a method, a spatial neural field of rock-physics parameters trained
by joint log reconstruction, and then tested it with decision rules fixed in advance. The
outcome is negative and, we believe, useful to the community:

1. On synthetic data, the recovery of a spatially varying cementation exponent succeeded only
   when the benchmark shared the model family of the inversion and vanished otherwise; null
   controls showed invented structure. Two further parameters were never identifiable.
2. On real data (378 producers and 47 dry holes in spatially held-out blocks) the neural-field
   pay indicator scored an AUC of 0.643 against 0.780 for the best baseline, and was also below
   the same inversion applied well by well and fixed-parameter Archie analysis.
3. The full pipeline, the timestamped decision log, all result files and the figure scripts are
   openly available, built only on public Kansas Geological Survey data.

We think the paper fits the journal because its contribution is methodological and
computational: a reproducible way of testing what label-free geoscientific inversions can
recover, with open code. Negative results of this kind are rarely published, which biases the
literature towards demonstrations that have not been stress-tested.

The manuscript is original, is not under consideration elsewhere, and the author has approved
it. Generative AI was used extensively in this work; its use is declared in the manuscript and
the author takes full responsibility for the content.

Sincerely,
Abrar Mahir
Department of Petroleum and Mining Engineering, Shahjalal University of Science and Technology, Sylhet, Bangladesh
abrar31@student.sust.edu | ORCID 0009-0003-0658-0667
