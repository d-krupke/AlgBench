This example guides you through converting a simple benchmark script
to using AlgBench and Slurminade.

1. `run_evaluation_v0.py` just runs the solver for all instances but does not save anything.
2. `run_evaluation_v1.py` saves the results using AlgBench.
3. `run_evaluation_v2.py` uses Slurminade to run the experiments on a cluster.
4. `run_evaluation_v3.py` bundles jobs to save some overhead of starting jobs.