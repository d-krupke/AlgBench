# AlgBench: A util for benchmarking algorithms in Python

There are a number of challenges when performing benchmarks for (long-running)
algorithms.

- Saving all information requires a lot of **boilerplate code** and often you
  forget something.
- If you add some further instances or want to compare an additional parameter,
  you have to check which data is already available to **skip existing
  entries**. Same if you need to interupt the benchmark.
- Just piping the results into a file can create a **huge amount of data**, no
  longer fitting into memory.
- Proper benchmarks often take days or even weeks to run, such that
  **parallelization** is necessary (e.g., with slurm) which requires a
  thread-safe database.
- Many file formats and databases are **difficult to access or impossible to
  repair** once corrupted.

AlgBench tries to ease your life by

- saving a lot of the information and data (function arguments, return values,
  runtime, environment information, stdout, etc.) automatically with a single
  line of code
- remembering which function arguments have already run and skipping those
- providing a compressable database to save memory, and saving highly redundant
  information, e.g., of the environment, only once
- providing an NFS-compatible parallel database and compatibility to
  distribution libraries, such as slurminade
- using a simple format based on JSON and Zip to allow simple parsing and even
  repairing broken databases by hand

## Usage

There is one important class `Benchmark` to run the benchmark, and two important
functions `describe` and `read_as_pandas` to analyze the results.

## On doing good emperical evaluations of algorithms

To get a feeling on the interesting instances and parameters, or generally on
where to look deeper, you should first perform an explorative study. For such an
explorative study, you should select some random parameters and instances, and
just look how the numbers look. Iteratively change the parameters and instances,
until you know what to evaluate properly. At that point, you can state some
research questions and design corresponding workhorse studies to answer them.

Here are some general hints:

- Create a separate folder for every study.
- Add a README.md into each folder that describes the study. At least describe
  in a sentence, who created this study when in which context.
- Have separated, numerated files for preparing, runing, processing, checking,
  and evaluating the study.
- Extract a simplified pandas table from the database with only the important
  data (e.g., stdout or environment information are only necessary for debugging
  and don't need to be shared for evaluation). You can save pandas tables as
  `.json.zip` such that they are small and can simply be added to your Git, even
  when the full data is too large.
- The file for checking the generated data should also describe it.
- Use a separate Jupyter-notebook for each family of plots you want to generate.
- Save the plots into files whose name you can easily trace back to the
  generating notebook. You will probably copy them later into some paper and
  half a year later, when you recieve the reviews and want to do some changes,
  you have to find the code that generated them.

# Version History

- **0.1.0** First complete version
