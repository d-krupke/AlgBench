AlgBench: A Python-util to run benchmarks for the empirical evaluation of algorithms.
=====================================================================================

.. image:: https://img.shields.io/pypi/v/algbench.svg
   :target: https://pypi.python.org/pypi/algbench

.. image:: https://img.shields.io/pypi/pyversions/algbench.svg
   :target: https://pypi.python.org/pypi/algbench

.. image:: https://img.shields.io/pypi/l/algbench.svg
   :target: https://pypi.python.org/pypi/algbench

.. image:: https://github.com/d-krupke/algbench/actions/workflows/pytest.yml/badge.svg
   :target: https://github.com/d-krupke/AlgBench

There are a number of challenges when performing benchmarks for
(long-running) algorithms.

-  Saving all information requires a lot of **boilerplate code** and
   often you forget something.
-  If you add some further instances or want to compare an additional
   parameter, you have to check which data is already available to
   **skip existing entries**. Same if you need to interrupt the
   benchmark.
-  Just piping the results into a file can create a **huge amount of
   data**, no longer fitting into memory.
-  Proper benchmarks often take days or even weeks to run, such that
   **parallelization** is necessary (e.g., with slurm) which requires a
   thread-safe database.
-  Many file formats and databases are **difficult to access or
   impossible to repair** once corrupted.

AlgBench tries to ease your life by

-  saving a lot of the information and data (function arguments, return
   values, runtime, environment information, stdout, etc.) automatically
   with a single line of code
-  remembering which function arguments have already run and skipping
   those
-  providing a compressible database to save memory, and saving highly
   redundant information, e.g., of the environment, only once
-  providing an NFS-compatible parallel database and compatibility to
   distribution libraries, such as slurminade
-  using a simple format based on JSON and Zip to allow simple parsing
   and even repairing broken databases by hand

There is a predecessor project, called
`AeMeasure <https://github.com/d-krupke/AeMeasure>`__. AeMeasure made
saving the data easy, but required more boilerplate code and reading the
data was more difficult and less efficient.

Other things you should know about for empirical/experimental evaluations
-------------------------------------------------------------------------

The following tools I consider essential for empirical evaluations (of
algorithms):

-  `pandas <https://pandas.pydata.org/>`__: Simple and powerful tool for
   working with data tables. Do your experiments and parse the important
   data into a pandas DataFrame.
-  `seaborn <https://seaborn.pydata.org/>`__ and
   `matplotlib <https://matplotlib.org/>`__: Creating beautiful plots
   from pandas DataFrames with little work.
-  `JupyterLab <https://jupyterlab.readthedocs.io/en/latest/>`__:
   Interactive Python+Markdown documents. Great for analyzing data and
   sharing the insights. Works great with pandas and seaborn.

AlgBench essentially takes over the part of saving the information from
the runs and allowing you to easily extract pandas DataFrames from it.
For very simple studies, you could also directly save your data into a
Pandas DataFrame but even for nearly every serious experiment, you run
into the problems mentioned in the beginning.

Note that the actual algorithms can also be written in another, more
efficient programming language. It is reasonably easy to create
Python-bindings, e.g., for C++ with
`pybind11 <https://pybind11.readthedocs.io/>`__, or just call the
binaries with Python.

Publishable evaluations often require extensive experiments that are
best performed on a cluster of shared workstations. Many institutes and
companies are using
`slurm <https://slurm.schedmd.com/documentation.html>`__ to schedule and
distribute the workloads. The data is usually shared via a network file
system (NFS), for which AlgBench is designed. While you usually also
have databases available, they are not made for just dumping all the
data you may need for analyzis and potentially debugging into. We
developed an additional tool
`slurminade <https://github.com/d-krupke/slurminade>`__ that allows you
to distribute your experiments with just a few additional lines. You can
see this in an example: `original
script <./examples/graph_coloring/02_run_benchmark.py>`__ vs `script
with
slurminade <./examples/graph_coloring/02b_run_benchmark_with_slurminade.py>`__.

Let me further recommend the books `A Guide To Experimental Algorithmics
by Catherine
McGeoch <https://www.cambridge.org/core/books/guide-to-experimental-algorithmics/CDB0CB718F6250E0806C909E1D3D1082>`__
here that gives a good introduction into the big picture of performing
empirical evaluations for algorithms. If you want to know more about
actually implementing complex algorithms for difficult problems, I
recommend to read `In Pursuit of the Traveling Salesman by Bill
Cook <https://press.princeton.edu/books/paperback/9780691163529/in-pursuit-of-the-traveling-salesman>`__
or `The Traveling Salesman Problem: A Computational Study by Appelgate
et al. <https://www.math.uwaterloo.ca/tsp/book/index.html>`__ to really
go into details. The Traveling Salesman Problem is an excellent example
for this because it is probably had gotten the most attention of any
NP-hard combinatorial problems. However, it can also be intimidating as
you probably won’t have the funds to look into any problem as deep as
the Travelings Salesman Problem has been looked at. Maybe you want to
read some papers from the SIAM Symposium on Algorithm Engineering and
Experiments (ALENEX) to see how smaller studies can be performed
(though, for most papers you will find aspects that could be improved).

Before you submit any paper (or thesis) with an empirical analysis,
I also recommend to first go through `this checklist <https://blog.sigplan.org/2019/08/28/a-checklist-manifesto-for-empirical-evaluation-a-preemptive-strike-against-a-replication-crisis-in-computer-science/>`__.

Installation
------------

You can install AlgBench using pip

.. code:: bash

   pip install -U algbench

Usage
-----

There is one important class ``Benchmark`` to run the benchmark, and two
important functions ``describe`` and ``read_as_pandas`` to analyze the
results.

1. Create a function that creates an entry in the database. Name all
   arguments that should be saved and used for identifying entries
   without ``_`` in the front. They should be JSON-compatible. Name all
   arguments that provide higher objects, such as the instance database,
   with an ``_`` in the front to tell *algbench* not to try to save or
   compare them. Return everything you want to be saved for the
   benchmark, best as a dictionary.

.. code:: python

   def create_benchmark_entry(
       instance_name: str,  # instance identifier for the database
       alg_parameters: dict,  # readable parameters for the algorithm
       _instance,  # the parsed instance (not to be added to the database)
   ):
       solution = alg(_instance, **alg_parameters)
       return {"objective_value": solution.obj()}

2. Create a ``Benchmark``-object by passing it a path for the database.

.. code:: python

   from algbench import Benchmark

   benchmark = Benchmark("./my_benchmark")

   # Optionally if logging is used):
   import logging

   # Configure with logger should be captured and with which level
   benchmark.capture_logger("my_alg", logging.INFO)
   benchmark.capture_logger("my_alg.submodule", logging.WARNING)

3. Use ``Benchmark.add`` to the function for all missing entries.

.. code:: python

   for instance_name, instance in instance_db:
       for params in params_to_compare:
           benchmark.add(
               create_benchmark_entry,  # function (could also be a lambda)
               # arguments for function
               instance_name=instance_name,
               alg_parameters=params,
               _instance=instance,
           )
   benchmark.compress()  # reduce the size of the database by file compression

4. Use a for loop to iterate over all raw entries

.. code:: python

   benchmark = Benchmark("./my_benchmark")
   for entry in benchmark:
       print(entry)  # dictionary

or ``read_as_pandas`` to extract a simple pandas table

.. code:: python

   t = read_as_pandas(
       "./my_benchmark/",
       lambda result: {
           "instance": result["parameters"]["args"]["instance_name"],
           "alg_params": result["parameters"]["args"]["alg_params"],
           "obj": result["result"]["objective_value"],
           "runtime": result["runtime"],  # automatically saved
       },
   )

You can use ``describe("./my_benchmark")`` to get an overview of the
available entries.

The ``Benchmark`` class provides further functionality, e.g., for
deleting selected entries or reparing a broken database.

You can find `an example for graph
coloring <./examples/graph_coloring/>`__. The important parts are shown
below.

Running a benchmark
~~~~~~~~~~~~~~~~~~~

.. code:: python

   from _utils import InstanceDb
   from algbench import Benchmark
   import networkx as nx

   benchmark = Benchmark("03_benchmark_data")
   instances = InstanceDb("./01_instances.zip")


   def load_instance_and_run(instance_name: str, alg_params):
       # load the instance outside the actual measurement
       g = instances[instance_name]

       def eval_greedy_alg(instance_name: str, alg_params, _instance: nx.Graph):
           # arguments starting with `_` are not saved.
           coloring = nx.coloring.greedy_coloring.greedy_color(_instance, **alg_params)
           return {  # the returned values are saved to the database
               "num_vertices": _instance.number_of_nodes(),
               "num_edges": _instance.number_of_edges(),
               "coloring": coloring,
               "n_colors": max(coloring.values()) + 1,
           }

       benchmark.add(eval_greedy_alg, instance_name, alg_params, g)


   alg_params_to_evaluate = [
       {"strategy": "largest_first", "interchange": True},
       {"strategy": "largest_first", "interchange": False},
       {"strategy": "random_sequential", "interchange": True},
       {"strategy": "random_sequential", "interchange": False},
       {"strategy": "smallest_last", "interchange": True},
       {"strategy": "smallest_last", "interchange": False},
       {"strategy": "independent_set"},
       {"strategy": "connected_sequential_bfs", "interchange": True},
       {"strategy": "connected_sequential_bfs", "interchange": False},
       {"strategy": "connected_sequential_dfs", "interchange": True},
       {"strategy": "connected_sequential_dfs", "interchange": False},
       {"strategy": "saturation_largest_first"},
   ]

   if __name__ == "__main__":
       for instance_name in instances:
           print(instance_name)
           for conf in alg_params_to_evaluate:
               load_instance_and_run(instance_name, conf)
       benchmark.compress()

Analyzing the data
~~~~~~~~~~~~~~~~~~

.. code:: python

   from algbench import describe, read_as_pandas, Benchmark

   describe("./03_benchmark_data/")


Output:

::

    result:
   | num_vertices: 68
   | num_edges: 697
   | coloring:
   || 0: 7
   || 1: 8
   || 2: 2
   || 3: 5
   || 4: 3
   || 5: 7
   || 6: 7
   || 7: 6
   || 8: 5
   || 9: 4
   || 10: 5
   || 11: 4
   || 12: 0
   || 13: 6
   || 14: 0
   || 15: 3
   || 16: 5
   || 17: 5
   || 18: 7
   || 19: 0
   || ...
   | n_colors: 9
    timestamp: 2023-05-25T21:58:39.201553
    runtime: 0.002952098846435547
    stdout:
    stderr:
    env_fingerprint: 53ad3b5b29d082d7e2bca6881ec9fe35fe441ae1
    args_fingerprint: 10ce65b7a61d5ecbfcb1f4e390d72122f7a1f6ec
    parameters:
   | func: eval_greedy_alg
   | args:
   || instance_name: graph_0
   || alg_params:
   ||| strategy: largest_first
   ||| interchange: True
    argv: ['02_run_benchmark.py']
    env:
   | hostname: workstation-r7
   | python_version: 3.10.9 (main, Jan 11 2023, 15:21:40) [GCC 11.2.0]
   | python: /home/krupke/anaconda3/envs/mo310/bin/python3
   | cwd: /home/krupke/Repositories/AlgBench/examples/graph_coloring
   | environment: [{'name': 'virtualenv', 'path': '/home/krupke/.local/lib/python3.10/site-pack...
   | git_revision: 5357426feb4b49174c313ffa33e2cadf6a83e226
   | python_file: /home/krupke/Repositories/AlgBench/examples/graph_coloring/02_run_benchmark.py




.. code:: python

   # we can also see the raw data of the first entry using `front`
   Benchmark("./03_benchmark_data/").front()



Output:

::

   {'result': {'num_vertices': 68,
     'num_edges': 697,
     'coloring': {'0': 7,
      '1': 8,
      '2': 2,
      '3': 5,
      '4': 3,
      '5': 7,
      '6': 7,
      '7': 6,
      '8': 5,
      '9': 4,
      '10': 5,
      '11': 4,
      '12': 0,
      '13': 6,
      '14': 0,
      '15': 3,
      '16': 5,
      '17': 5,
      '18': 7,
      '19': 0,
      '20': 2,
      '21': 3,
       ...},
     'n_colors': 9},
    'timestamp': '2023-05-25T21:58:39.201553',
    'runtime': 0.002952098846435547,
    'stdout': '',
    'stderr': '',
    'env_fingerprint': '53ad3b5b29d082d7e2bca6881ec9fe35fe441ae1',
    'args_fingerprint': '10ce65b7a61d5ecbfcb1f4e390d72122f7a1f6ec',
    'parameters': {'func': 'eval_greedy_alg',
     'args': {'instance_name': 'graph_0',
      'alg_params': {'strategy': 'largest_first', 'interchange': True}}},
    'argv': ['02_run_benchmark.py'],
    'env': {'hostname': 'workstation-r7',
     'python_version': '3.10.9 (main, Jan 11 2023, 15:21:40) [GCC 11.2.0]',
     'python': '/home/krupke/anaconda3/envs/mo310/bin/python3',
     'cwd': '/home/krupke/Repositories/AlgBench/examples/graph_coloring',
     'environment': [{'name': 'virtualenv',
       'path': '/home/krupke/.local/lib/python3.10/site-packages',
       'version': '20.14.1'},
      {'name': 'cfgv',
       'path': '/home/krupke/.local/lib/python3.10/site-packages',
       'version': '3.3.1'},
     ...],
     'git_revision': '5357426feb4b49174c313ffa33e2cadf6a83e226',
     'python_file': '/home/krupke/Repositories/AlgBench/examples/graph_coloring/02_run_benchmark.py'}}


.. code:: python

   # we can extract a full pandas tables using `read_as_pandas`
   t = read_as_pandas(
       "./03_benchmark_data/",
       lambda result: {
           "instance": result["parameters"]["args"]["instance_name"],
           "strategy": result["parameters"]["args"]["alg_params"]["strategy"],
           "interchange": result["parameters"]["args"]["alg_params"].get(
               "interchange", None
           ),
           "colors": result["result"]["n_colors"],
           "runtime": result["runtime"],
           "num_vertices": result["result"]["num_vertices"],
           "num_edges": result["result"]["num_edges"],
       },
   )
   print(t)

Output:

::

          instance                  strategy interchange  colors   runtime ...
   0       graph_0             largest_first        True       9  0.002952
   1       graph_0             largest_first       False      10  0.000183
   2       graph_0         random_sequential        True       9  0.003562
   3       graph_0         random_sequential       False      12  0.000173
   4       graph_0             smallest_last        True       9  0.003813
   ...         ...                       ...         ...     ...       ...
   5995  graph_499  connected_sequential_bfs        True       3  0.000216
   5996  graph_499  connected_sequential_bfs       False       3  0.000132
   5997  graph_499  connected_sequential_dfs        True       3  0.000231
   5998  graph_499  connected_sequential_dfs       False       4  0.000132
   5999  graph_499  saturation_largest_first        None       3  0.000202


   [6000 rows x 7 columns]


Which information is saved?
---------------------------

The following information is saved automatically:

-  function name
-  all arguments that do not begin with “\_” (use this to pass parsed
   instances etc.)
-  the returned values
-  runtime
-  current date and time
-  hostname
-  Python version
-  Python binary path
-  current working directory
-  stdout and stderr
-  all installed modules and their versions
-  git revision
-  path of the python file

Things to be aware of
---------------------

-  Only function name and arguments not starting with “\_” are used to
   compare entries. If an argument (or part of it) is not
   JSON-compatible, the string of it is used.
-  Arguments and return values that cannot be translated to json are
   converted to string in the database. The default string conversion
   may not be very useful.
-  The stdout/strerr capturing only works if Python’s stdout/stderr are
   used. E.g., C++ write by default to the system’s stdout/stderr and
   cannot be captured (if you have been wondering, why C++-modules have
   a bad output it Jupyter-notebooks: this is the reason). PyBind11
   allows you `to change that
   behavior <https://pybind11.readthedocs.io/en/stable/advanced/pycpp/utilities.html#using-python-s-print-function-in-c>`__.
-  Global variables are not saved. Try to pass all important parameters
   as function arguments, as they can also alter the benchmark and are
   important to distinguish entries (e.g., you would want to recompute
   an entry if the timelimit has been changed. This is only possible if
   you tell algbench this by making it an argument).
-  ‘sys.argv’ and the filename are saved, but not used for
   distinguishing entries.

On doing good empirical evaluations of algorithms
-------------------------------------------------

To get a feeling on the interesting instances and parameters, or
generally on where to look deeper, you should first perform an
explorative study. For such an explorative study, you should select some
random parameters and instances, and just look how the numbers look.
Iteratively change the parameters and instances, until you know what to
evaluate properly. At that point, you can state some research questions
and design corresponding workhorse studies to answer them.

Here are some general hints:

-  Do not mix algorithm code and experiment code, even if it saves you
   rebuilding your package after every change. Such a mixed setup may
   save you a command line, but it is harder to log and many problems
   may remain unnoticed until you try to publish your algorithm. The
   little overhead is worth it in the long run.
-  Create a separate folder for every study. Don’t mix too much because
   you want to reduce redundancies: Once things become complicated, you
   may draw conclusions from the wrong data without noticing.
-  Add a README.md into each folder that describes the study. At least
   describe in a sentence, who created this study when in which context.
-  Have separated, numerated files for preparing, running, processing,
   checking, and evaluating the study.
-  Extract a simplified pandas table from the database with only the
   important data (e.g., stdout or environment information are only
   necessary for debugging and don’t need to be shared for evaluation).
   You can save pandas tables as ``.json.zip`` such that they are small
   and can simply be added to your Git, even when the full data is too
   large.
-  The file for checking the generated data should also describe it.
-  Use a separate Jupyter-notebook for each family of plots you want to
   generate.
-  Save the plots into files whose name you can easily trace back to the
   generating notebook. You will probably copy them later into some
   paper and half a year later, when you receive the reviews and want to
   do some changes, you have to find the code that generated them.


On gaining more insights using logging
---------------------------------------

If you develop complex algorithms, you often want to not only measure
the runtime of thw whole algorithm, but also of its parts, as well as
other information, such as the number of iterations, the current
solution, etc. You can use the Python logging framework for this. The
logging framework allows you to create loggers that can be configured
individually. You can also create a logger for each module and
submodule, and configure them individually. You can also configure
handlers for the loggers, e.g., to write them to a file or to the
console. You can also configure the level of the loggers and handlers,
such that you can easily switch between different levels of logging.
AlgBench allows you to capture the loggers and save them to the
database. You can then extract them and analyze them.

You can also use simple ``print`` statements, but they are not as
flexible as the logging framework. While AlgBench can actually
add the runtime to the print statements, it is not as easy to
configure the output as with the logging framework. There is no
way to disable the output for individual parts of your algorithm,
or to change the level of the output. The logging framework is
as easy to use as print statements, but much more flexible.
It can be more expensive, but ``print`` statements are also not
free and should be used with care.

Here is an example for using the logging framework:

.. code:: python

   import logging


   def my_alg():
       logger = logging.getLogger("my_alg")
       logger.info("Starting my_alg")
       # do something
       logger.info("Finished my_alg")


   logger = logging.getLogger("my_alg")
   logger.setLevel(logging.INFO)
   logger.addHandler(logging.StreamHandler())
   my_alg()

A further advantage of the logging framework is that you can separate
the message structure from the data. This allows you to easily query
for specific events and directly extract the data you want to analyze.

.. code:: python

   logger.info("Submodule X needed %d iterations", 42)

Will be saved as a dictionary with a separate field for the message and
the data:

::

   {
       "msg": "Submodule X needed %d iterations",
       "args": [42],
   }

A further alternative is to use a dedicated class for stats that you
pass around. This is generally a good idea, but takes more work and
requires you to change the code. The logging framework is a good
compromise between flexibility and ease of use.

If your algorithm may be run in parallel or different contexts, you may want to allow
to pass a logger to the algorithm. This allows you to create a
separate logger for each context to separate the logs.

::

   Note that AlgBench v2 automatically adds the runtime to print statments and log entries.

Using Git LFS for the data
--------------------------

The data are large binary files. Use Git LFS to add them to your
repository more efficiently.

You can find a guide `here <https://git-lfs.com/>`__ on how to install
Git LFS.

Run

.. code:: bash

   git lfs install

to set up git LFS and

.. code:: bash

   git lfs track "*.zip"

to manage all zips via LFS.

Alternatively, you can also just edit ``.gitattributes`` by hand

::

   *.zip filter=lfs diff=lfs merge=lfs -text

Finally, add ``.gitattributes`` to git via

.. code:: bash

   git add .gitattributes

Version History
===============

- **2.2.2** Fixing problem with Jupyter notebooks, because they may not have a ``__file__`` attribute.
- **2.2.1** Should be able to deal with corrupt zip files now.
- **2.2.0** Allowing to skip entries in ``read_as_pandas`` by returning a None for the row.
- **2.1.0** More flexible stream handling. You can now disable the output saving and hidding. The default behavior still is to save the output with time stamps and hide it from the console.
- **2.0.0** Extensive change of stdout/stderr handling and new logging functionality.
   By default, stdout and stderr will now be saved with the runtime of the function.
   Additionally, you can now capture loggers of the Python logging framework and save them to the database.
   This is especially useful if you use a library that uses the logging framework. Prefere ``logging`` over ``print`` for logging information.
-  **1.1.0** Some changes for efficiency turned out to be less robust in
   case of, e.g., keyboard interrupt. Fixed that.
-  **1.0.0** Changing the database layout, making it more efficient
   (breaking change!).
-  **0.2.0** Changing database slightly to contain meta data and doing
   more caching. Saving some more information.
-  **0.1.3** Fixed bug in arg fingerprint set.
-  **0.1.2** Fixed bug with empty rows in pandas table.
-  **0.1.1** Fixed bug with ``delete_if``.
-  **0.1.0** First complete version
