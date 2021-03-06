#!/usr/bin/python
"""Core interface for the summaryInfo metadata objects to interface with CherryPy."""
from metadata.rest.reporting_queries.summarize_by_date import SummarizeByDate
from metadata.rest.reporting_queries.detailed_transactions_list import DetailedTransactionList


# pylint: disable=too-few-public-methods
class SummaryInfoAPI(object):
    """SummaryInfo API."""

    exposed = True

    def __init__(self):
        """Create local objects for subtree items."""
        self.by_date = SummarizeByDate()
        self.transaction_details = DetailedTransactionList
