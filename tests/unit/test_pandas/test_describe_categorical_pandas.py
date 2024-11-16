import pandas as pd
import pytest
from ydata_profiling.model.pandas.describe_categorical_pandas import word_summary_vc

value_counts_w_words = pd.Series(index=["The dog", "is hungry"], data=[2, 1])

# Test the basic word summary function
def test_word_summary_vc():
    assert (
        word_summary_vc(vc=value_counts_w_words, remove_default_stopwords=False)["word_counts"].to_dict()
        == pd.Series(index=["the", "dog", "is", "hungry"], data=[2, 2, 1, 1]).to_dict()
    )

# Test word summary function with custom stop words
@pytest.mark.parametrize("stop_words", [["the"], ["the", "a"]])
def test_word_summary_vc_with_stop_words(stop_words):
    assert (
        word_summary_vc(vc=value_counts_w_words, stop_words=stop_words, remove_default_stopwords=False)[
            "word_counts"
        ].to_dict()
        == pd.Series(index=["dog", "is", "hungry"], data=[2, 1, 1]).to_dict()
    )

# Test word summary function with default stopwords removed
def test_word_summary_vc_with_default_stopwords():
    assert (
        word_summary_vc(vc=value_counts_w_words, remove_default_stopwords=True)["word_counts"].to_dict()
        == pd.Series(index=["dog", "hungry"], data=[2, 1]).to_dict()
    )

# Test word summary function with both custom and default stop words
@pytest.mark.parametrize(
    "stop_words, expected",
    [
        (["dog"], {"hungry": 1}),  # Custom stop word "dog", "is" removed as a default stopword
        (["the", "is"], {"dog": 2, "hungry": 1}),  # Custom stop words "the" and "is"
    ],
)
def test_word_summary_vc_with_custom_and_default_stop_words(stop_words, expected):
    result = word_summary_vc(vc=value_counts_w_words, stop_words=stop_words, remove_default_stopwords=True)["word_counts"].to_dict()
    assert result == expected

# Test word summary function with keep_stopwords
def test_word_summary_vc_with_keep_stopwords():
    assert (
        word_summary_vc(vc=value_counts_w_words, remove_default_stopwords=True, keep_stopwords=["is"])["word_counts"].to_dict()
        == pd.Series(index=["dog", "is", "hungry"], data=[2, 1, 1]).to_dict()
    )
