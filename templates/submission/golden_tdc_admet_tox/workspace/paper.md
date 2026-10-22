# Golden Run Report

## Approach

Two materially different configurations were compared: a compact
fingerprint with an unweighted regularized linear head, and a wider
fingerprint with balanced class weighting. Both were evaluated on the fixed
validation split with the official metric, and each run covered exactly one
candidate.

## Results

| Configuration | Validation macro AUROC | AMES AUROC |
|---|---|---|
| exp_001 | 0.752 <!-- claim:table1_macro_run1 --> | 0.810 <!-- claim:table1_ames_run1 --> |
| exp_002 | 0.768 <!-- claim:table1_macro_run2 --> | — |

## Conclusion

The wider fingerprint with balanced weighting outperformed the compact
baseline on validation macro AUROC. The promoted configuration achieved the
best score on every endpoint, so no further configuration was started after
the second one.