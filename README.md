# AlgBench: A util for benchmarking algorithms in Python

A new experimental framework to perform algorithm benchmarks

- **Parallel:** Compatibility for distributed execution, i.e., the database has
  to be robust against parallel writes.
  - Challenge: Simple files (in an NFS) are not thread-safe. Proper databases
    require a lot of setup and need to be maintained.
  - Solution: Using separate files for each thread that can easily be merged.
- **Interruptible:** Making it possible to interrupt the benchmark and continue
  it later, without having to repeat everything.
- **Extensible:** Making it possible to extend the benchmark by further
  instances and configurations, without having to rerun everything.
- **Accessible:** Usage of common data formats (e.g., JSON) to make the data
  readable even with basic libraries.
- **Less boilerplate code:** The benchmarks should require little boilerplate
  code to save all the data.
  - Challenge:
- **Compact:** The database should be reasonably compact to still be publishable
  via GitHub etc.
  - Challenge: It is difficult to simultaneously be robust against parallel
    writes and compress the data.
  - Solution: The database has a compressed read-only part, and an uncompressed
    part for concurrent input. Once the benchmark is finished (or paused), a
    compress function can be called move the uncompressed data into the
    compressed archive.

## Usage

There is one important class `Benchmark` to run the benchmark, and two important
functions `describe` and `read_as_pandas` to analyze the results.

# Version History

- **0.1.0** First complete version
