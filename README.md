# AlgBench: A Python-util to run benchmarks for the empirical evaluation of algorithms.

There are a number of challenges when performing benchmarks for (long-running)
algorithms.

- Saving all information requires a lot of **boilerplate code** and often you
  forget something.
- If you add some further instances or want to compare an additional parameter,
  you have to check which data is already available to **skip existing
  entries**. Same if you need to interrupt the benchmark.
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
- providing a compressible database to save memory, and saving highly redundant
  information, e.g., of the environment, only once
- providing an NFS-compatible parallel database and compatibility to
  distribution libraries, such as slurminade
- using a simple format based on JSON and Zip to allow simple parsing and even
  repairing broken databases by hand

## Usage

There is one important class `Benchmark` to run the benchmark, and two important
functions `describe` and `read_as_pandas` to analyze the results.

<p>
<table width="100%" cellspacing=0 cellpadding=2 border=0 summary="section">
<tr bgcolor="#ffc8d8">
<td colspan=3 valign=bottom>&nbsp;<br>
<font color="#000000" face="helvetica, arial"><a name="Benchmark">class <strong>Benchmark</strong></a>(<a href="builtins.html#object">builtins.object</a>)</font></td></tr>
    
<tr bgcolor="#ffc8d8"><td rowspan=2><tt>&nbsp;&nbsp;&nbsp;</tt></td>
<td colspan=2><tt>Benchmark(path:&nbsp;str)&nbsp;-&amp;gt;&nbsp;None<br>
&nbsp;<br>
This&nbsp;is&nbsp;the&nbsp;heart&nbsp;of&nbsp;the&nbsp;library.&nbsp;It&nbsp;allows&nbsp;to&nbsp;run,&nbsp;safe,&nbsp;and&nbsp;load<br>
a&nbsp;benchmark.<br>
&nbsp;<br>
The&nbsp;function&nbsp;`add`&nbsp;will&nbsp;run&nbsp;a&nbsp;configuration,&nbsp;if&nbsp;it&nbsp;is&nbsp;not<br>
already&nbsp;in&nbsp;the&nbsp;database.&nbsp;You&nbsp;can&nbsp;also&nbsp;split&nbsp;this&nbsp;into&nbsp;`check`&nbsp;and<br>
`run`.&nbsp;This&nbsp;may&nbsp;be&nbsp;advised&nbsp;if&nbsp;you&nbsp;want&nbsp;to&nbsp;distribute&nbsp;the&nbsp;execution.<br>
&nbsp;<br>
```python<br>
benchmark&nbsp;=&nbsp;Benchmark("./test_benchmark")<br>
&nbsp;<br>
&nbsp;<br>
def&nbsp;f(x,&nbsp;_test=2,&nbsp;default="default"):<br>
&nbsp;&nbsp;&nbsp;&nbsp;print(x)&nbsp;&nbsp;#&nbsp;here&nbsp;you&nbsp;would&nbsp;run&nbsp;your&nbsp;algorithm<br>
&nbsp;&nbsp;&nbsp;&nbsp;return&nbsp;{"r1":&nbsp;x,&nbsp;"r2":&nbsp;"test"}<br>
&nbsp;<br>
&nbsp;<br>
benchmark.<a href="#Benchmark-add">add</a>(f,&nbsp;1,&nbsp;_test=None)<br>
benchmark.<a href="#Benchmark-add">add</a>(f,&nbsp;2)<br>
benchmark.<a href="#Benchmark-add">add</a>(f,&nbsp;3,&nbsp;_test=None)<br>
&nbsp;<br>
benchmark.<a href="#Benchmark-compress">compress</a>()<br>
&nbsp;<br>
for&nbsp;entry&nbsp;in&nbsp;benchmark:<br>
&nbsp;&nbsp;&nbsp;&nbsp;print(entry["parameters"],&nbsp;entry["data"])<br>
```<br>
&nbsp;<br>
The&nbsp;following&nbsp;functions&nbsp;are&nbsp;thread-safe:<br>
-&nbsp;exists<br>
-&nbsp;run<br>
-&nbsp;add<br>
-&nbsp;insert<br>
-&nbsp;front<br>
-&nbsp;__iter__<br>
&nbsp;<br>
Don't&nbsp;call&nbsp;any&nbsp;of&nbsp;the&nbsp;other&nbsp;functions&nbsp;while&nbsp;the&nbsp;benchmark&nbsp;is<br>
running.&nbsp;It&nbsp;could&nbsp;lead&nbsp;to&nbsp;data&nbsp;loss.<br>&nbsp;</tt></td></tr>
<tr><td>&nbsp;</td>
<td width="100%">Methods defined here:<br>
<dl><dt><a name="Benchmark-__init__"><strong>__init__</strong></a>(self, path: str) -&gt; None</dt></dl>

<dl><dt><a name="Benchmark-__iter__"><strong>__iter__</strong></a>(self) -&gt; Generator[Dict, NoneType, NoneType]</dt><dd><tt>Iterate&nbsp;over&nbsp;all&nbsp;entries&nbsp;in&nbsp;the&nbsp;benchmark.<br>
Use&nbsp;`front`&nbsp;to&nbsp;get&nbsp;a&nbsp;preview&nbsp;on&nbsp;how&nbsp;an&nbsp;entry&nbsp;looks&nbsp;like.</tt></dd></dl>

<dl><dt><a name="Benchmark-add"><strong>add</strong></a>(self, func: Callable, *args, **kwargs)</dt><dd><tt>Will&nbsp;add&nbsp;the&nbsp;function&nbsp;call&nbsp;with&nbsp;the&nbsp;arguments<br>
to&nbsp;the&nbsp;benchmark&nbsp;if&nbsp;not&nbsp;yet&nbsp;contained.<br>
&nbsp;<br>
Combination&nbsp;of&nbsp;`check`&nbsp;and&nbsp;`run`.<br>
Will&nbsp;only&nbsp;call&nbsp;`run`&nbsp;if&nbsp;the&nbsp;arguments&nbsp;are&nbsp;not<br>
yet&nbsp;in&nbsp;the&nbsp;benchmark.</tt></dd></dl>

<dl><dt><a name="Benchmark-compress"><strong>compress</strong></a>(self)</dt><dd><tt>Compress&nbsp;the&nbsp;data&nbsp;of&nbsp;the&nbsp;benchmark&nbsp;to&nbsp;take&nbsp;less&nbsp;disk&nbsp;space.<br>
&nbsp;<br>
NOT&nbsp;THREAD-SAFE!</tt></dd></dl>

<dl><dt><a name="Benchmark-delete"><strong>delete</strong></a>(self)</dt><dd><tt>Delete&nbsp;the&nbsp;benchmark.<br>
&nbsp;<br>
NOT&nbsp;THREAD-SAFE!</tt></dd></dl>

<dl><dt><a name="Benchmark-delete_if"><strong>delete_if</strong></a>(self, condition: Callable[[Dict], bool])</dt><dd><tt>Delete&nbsp;entries&nbsp;if&nbsp;a&nbsp;specific&nbsp;condition&nbsp;is&nbsp;met.<br>
This&nbsp;is&nbsp;currently&nbsp;inefficiently,&nbsp;as&nbsp;always&nbsp;a&nbsp;copy<br>
of&nbsp;the&nbsp;benchmark&nbsp;is&nbsp;created.<br>
Use&nbsp;`front`&nbsp;to&nbsp;get&nbsp;a&nbsp;preview&nbsp;on&nbsp;how&nbsp;an&nbsp;entry&nbsp;that&nbsp;is<br>
passed&nbsp;to&nbsp;the&nbsp;condition&nbsp;looks&nbsp;like.<br>
&nbsp;<br>
NOT&nbsp;THREAD-SAFE!</tt></dd></dl>

<dl><dt><a name="Benchmark-exists"><strong>exists</strong></a>(self, func: Callable, *args, **kwargs) -&gt; bool</dt><dd><tt>Use&nbsp;this&nbsp;function&nbsp;to&nbsp;check&nbsp;if&nbsp;an&nbsp;entry&nbsp;already&nbsp;exist&nbsp;and&nbsp;thus<br>
does&nbsp;not&nbsp;have&nbsp;to&nbsp;be&nbsp;run&nbsp;again.&nbsp;If&nbsp;you&nbsp;want&nbsp;to&nbsp;have&nbsp;multiple<br>
samples,&nbsp;add&nbsp;a&nbsp;sample&nbsp;index&nbsp;argument.<br>
Caveat:&nbsp;This&nbsp;function&nbsp;may&nbsp;have&nbsp;false&nbsp;negatives.&nbsp;i.e.,&nbsp;says&nbsp;that&nbsp;it<br>
&nbsp;&nbsp;does&nbsp;not&nbsp;exist&nbsp;despite&nbsp;it&nbsp;existing&nbsp;(only&nbsp;for&nbsp;fresh&nbsp;data).</tt></dd></dl>

<dl><dt><a name="Benchmark-front"><strong>front</strong></a>(self) -&gt; Optional[Dict]</dt><dd><tt>Return&nbsp;the&nbsp;first&nbsp;entry&nbsp;of&nbsp;the&nbsp;benchmark.<br>
Useful&nbsp;for&nbsp;checking&nbsp;its&nbsp;content.</tt></dd></dl>

<dl><dt><a name="Benchmark-insert"><strong>insert</strong></a>(self, entry: Dict)</dt><dd><tt>Insert&nbsp;a&nbsp;raw&nbsp;entry,&nbsp;as&nbsp;returned&nbsp;by&nbsp;`__iter__`&nbsp;or&nbsp;`front`.</tt></dd></dl>

<dl><dt><a name="Benchmark-repair"><strong>repair</strong></a>(self)</dt><dd><tt>Repairs&nbsp;the&nbsp;benchmark&nbsp;in&nbsp;case&nbsp;it&nbsp;has&nbsp;some&nbsp;broken&nbsp;entries.<br>
&nbsp;<br>
NOT&nbsp;THREAD-SAFE!</tt></dd></dl>

<dl><dt><a name="Benchmark-run"><strong>run</strong></a>(self, func: Callable, *args, **kwargs)</dt><dd><tt>Will&nbsp;add&nbsp;the&nbsp;function&nbsp;call&nbsp;with&nbsp;the&nbsp;arguments<br>
to&nbsp;the&nbsp;benchmark.</tt></dd></dl>

<hr>
Data descriptors defined here:<br>
<dl><dt><strong>__dict__</strong></dt>
<dd><tt>dictionary&nbsp;for&nbsp;instance&nbsp;variables&nbsp;(if&nbsp;defined)</tt></dd>
</dl>
<dl><dt><strong>__weakref__</strong></dt>
<dd><tt>list&nbsp;of&nbsp;weak&nbsp;references&nbsp;to&nbsp;the&nbsp;object&nbsp;(if&nbsp;defined)</tt></dd>
</dl>
</td></tr></table>

## On doing good empirical evaluations of algorithms

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
- Have separated, numerated files for preparing, running, processing, checking,
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
  half a year later, when you receive the reviews and want to do some changes,
  you have to find the code that generated them.


## Using Git LFS for the data

The data are large binary files. Use Git LFS to add them to your repository more efficiently.

You can find a guide [here](https://git-lfs.com/) on how to install Git LFS.

Run
```bash
git lfs install
```
to set up git LFS and
```bash
git lfs track "*.zip"
```
to manage all zips via LFS.

Alternatively, you can also just edit `.gitattributes` by hand
```
*.zip filter=lfs diff=lfs merge=lfs -text
```

Finally, add `.gitattributes` to git via
```bash
git add .gitattributes
``` 

# Version History

- **0.1.3** Fixed bug in arg fingerprint set.
- **0.1.2** Fixed bug with empty rows in pandas table.
- **0.1.1** Fixed bug with `delete_if`.
- **0.1.0** First complete version
