# Great Expectations

!!! note "Package versions"

    Great expectations integration is no longer supported. 
    You can recreate the integration with the following
    packages versions: 

        - ydata-profiling==2.1.0 
        - great-expectations==0.13.4

[Great Expectations](https://www.greatexpectations.io) is a Python-based
open-source library for validating, documenting, and profiling your
data. It helps you to maintain data quality and improve communication
about data between teams. With Great Expectations, you can assert what
you expect from the data you load and transform, and catch data issues
quickly -- Expectations are basically *unit tests for your data*.
`ydata-profiling` features a method to create a suite of Expectations
based on the results of your `ProfileReport`!

## About Great Expectations

*Expectations* are assertions about your data. In Great Expectations,
those assertions are expressed in a declarative language in the form of
simple, human-readable Python methods. For example, in order to assert
that you want values in a column `passenger_count` in your dataset to be
integers between 1 and 6, you can say:

> `expect_column_values_to_be_between(column="passenger_count", min_value=1, max_value=6)`

Great Expectations then uses this statement to validate whether the
column `passenger_count` in a given table is indeed between 1 and 6, and
returns a success or failure result. The library currently provides
[several dozen highly expressive built-in
Expectations](https://docs.greatexpectations.io/en/latest/reference/glossary_of_expectations.html),
and allows you to write custom Expectations.

Great Expectations renders Expectations to clean, human-readable
documentation called *Data Docs*. These HTML docs contain both your
Expectation Suites as well as your data validation results each time
validation is run -- think of it as a continuously updated data quality
report.

For more information about Great Expectations, check out the [Great
Expectations
documentation](https://docs.greatexpectations.io/en/latest/) and join
the [Great Expectations Slack
channel](https://www.greatexpectations.io/slack) for help.

## Creating Expectation Suites with ydata-profiling

An *Expectation Suite* is simply a set of Expectations. You can create
Expectation Suites by writing out individual statements, such as the one
above, or by automatically generating them based on profiler results.

`ydata-profiling` provides a simple `to_expectation_suite()` method that
returns a Great Expectations `ExpectationSuite` object which contains a
set of Expectations.

**Pre-requisites**: In order to run the `to_expectation_suite()` method,
you will need to install Great Expectations with
`pip install great_expectations`

If you would like to use the additional features such as saving the
Suite and building Data Docs, you will also need to configure a Great
Expectations Data Context by running `great_expectations init` in your
project\'s directory.

``` python linenums="1" title="Get your set of expectations"
import pandas as pd
from ydata_profiling import ProfileReport

df = pd.read_csv("titanic.csv")

profile = ProfileReport(df, title="Pandas Profiling Report", explorative=True)

# Obtain an Expectation Suite with a set of default Expectations
# By default, this also profiles the dataset, saves the suite, runs validation, and builds Data Docs
suite = profile.to_expectation_suite()
```

This assumes that the `great_expectations` Data Context directory is in
the *same path* where you run the script. In order to specify the
location of your Data Context, pass it in as an argument:

``` python linenums="1" title="Generate a suite of expectations"
import great_expectations as ge

data_context = ge.data_context.DataContext(
    context_root_dir="/Users/panda/code/my_ge_project/"
)
suite = profile.to_expectation_suite(data_context=data_context)
```

You can also configure each feature individually in the function call:

``` python linenums="1" title="Configure features"
suite = profile.to_expectation_suite(
    suite_name="titanic_expectations",
    data_context=data_context,
    save_suite=False,
    run_validation=False,
    build_data_docs=False,
    handler=handler,
)
```

See [the Great Expectations
Examples](https://github.com/ydataai/ydata-profiling/blob/master/examples/integrations/great_expectations/great_expectations_example.py)
for complete examples.

<img referrerpolicy="no-referrer-when-downgrade" src="https://static.scarf.sh/a.png?x-pxid=baa0e45f-0c03-4190-9646-9d8ea2640ba2" />