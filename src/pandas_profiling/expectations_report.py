from pandas_profiling.model import expectation_algorithms
from pandas_profiling.model.handler import Handler
from pandas_profiling.model.typeset import (
    URL,
    Boolean,
    Categorical,
    DateTime,
    File,
    Image,
    Numeric,
    Path,
    ProfilingTypeSet,
    Unsupported,
)
from pandas_profiling.utils.dataframe import slugify


# Default handler
class ExpectationHandler(Handler):
    def __init__(self, typeset, *args, **kwargs):
        mapping = {
            Unsupported: [expectation_algorithms.generic_expectations],
            Categorical: [expectation_algorithms.categorical_expectations],
            Boolean: [expectation_algorithms.categorical_expectations],
            Numeric: [expectation_algorithms.numeric_expectations],
            URL: [expectation_algorithms.url_expectations],
            File: [expectation_algorithms.file_expectations],
            Path: [expectation_algorithms.path_expectations],
            DateTime: [expectation_algorithms.datetime_expectations],
            Image: [expectation_algorithms.image_expectations],
        }
        super().__init__(mapping, typeset, *args, **kwargs)


class ExpectationsReport:
    def to_expectation_suite(
        self,
        suite_name=None,
        data_context=None,
        save_suite=True,
        run_validation=True,
        build_data_docs=True,
        handler=None,
    ):
        """
        All parameters default to True to make it easier to access the full functionality of Great Expectations out of
        the box.
        Args:
            suite_name: The name of your expectation suite
            data_context: A user-specified data context
            save_suite: Boolean to determine whether to save the suite to .json as part of the method
            run_validation: Boolean to determine whether to run validation as part of the method
            build_data_docs: Boolean to determine whether to build data docs, save the .html file, and open data docs in
                your browser
            handler: The handler to use for building expectation

        Returns:
            An ExpectationSuite
        """
        try:
            import great_expectations as ge
        except ImportError:
            raise ImportError(
                "Please install great expectations before using the expectation functionality"
            )

        # Use report title if suite is empty
        if suite_name is None:
            suite_name = slugify(self.title)

        # Use the default handler if none
        if handler is None:
            handler = ExpectationHandler(ProfilingTypeSet())

        # Obtain the ge context and create the expectation suite
        if not data_context:
            data_context = ge.data_context.DataContext()

        suite = data_context.create_expectation_suite(
            suite_name, overwrite_existing=True
        )
        if save_suite:
            data_context.save_expectation_suite(suite)

        # Instantiate an in-memory pandas dataset
        batch = ge.dataset.PandasDataset(self.df, expectation_suite=suite)

        # Obtain the profiling summary
        summary = self.get_description()

        # Dispatch to expectations per semantic variable type
        for name, variable_summary in summary["variables"].items():
            handler.handle(variable_summary["type"], name, variable_summary, batch)

        # We don't actually update the suite object on the batch in place, so need
        # to get the populated suite from the batch
        suite = batch.get_expectation_suite()

        if run_validation:
            batch = ge.dataset.PandasDataset(self.df, expectation_suite=suite)

            results = data_context.run_validation_operator(
                "action_list_operator", assets_to_validate=[batch]
            )
            validation_result_identifier = results.list_validation_result_identifiers()[
                0
            ]

            # Write expectations and open data docs

            if build_data_docs:
                data_context.save_expectation_suite(suite)
                data_context.build_data_docs()
                data_context.open_data_docs(validation_result_identifier)

        if build_data_docs and not run_validation:
            data_context.save_expectation_suite(suite)
            data_context.build_data_docs()
            data_context.open_data_docs()

        return batch.get_expectation_suite()
