## Optimizer Card
verdict_MIPROv2:
  - datasets:
    - size: train 1002, val 500, test 498
    - source: generated from HotPotQA
    - quality: low
  - optimizer: MIPROv2
  - compile:
    - model: mistralai/Mistral-Nemo-Instruct-2407
    - init_temperature: 1
    - num_candidates: 20
    - num_batches: 120
    - max_bootstrapped_demos: 4
    - max_labeled_demos: 4
  - version:
    - dspy-ai==2.4.13