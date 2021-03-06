"""CherryPy File Details object class."""
from cherrypy import tools, HTTPError, request
from metadata.orm import Files, Transactions
from metadata.rest.reporting_queries.query_base import QueryBase
from peewee import fn

# pylint: disable=too-few-public-methods


class EarliestLatestFiles(QueryBase):
    """Retrieves earliest and latest file entries for a set of metadata specifiers."""

    exposed = True

    @staticmethod
    def _get_earliest_latest(item_type, item_list, time_basis):
        accepted_item_types = list(
            set(QueryBase.object_type_mappings.keys() + QueryBase.object_type_mappings.values())
        )
        accepted_time_basis_types = [
            'submitted', 'modified', 'created',
            'submit', 'modified', 'create',
            'submit_time', 'modified_time', 'create_time',
            'submitted_date', 'modified_date', 'created_date',
        ]
        item_type = QueryBase.object_type_mappings.get(item_type)
        time_basis = time_basis.lower()
        if item_type not in accepted_item_types or time_basis not in accepted_time_basis_types:
            raise HTTPError('400 Invalid Query')

        short_time_basis = time_basis[:5]

        time_basis = {
            'submi': lambda x: 'submitted',
            'modif': lambda x: 'modified',
            'creat': lambda x: 'created'
        }[short_time_basis](short_time_basis)

        search_field = getattr(Transactions, '{0}_id'.format(item_type))
        if time_basis == 'submitted':
            query = Transactions().select(
                fn.Min(Transactions.updated).alias('earliest'),
                fn.Max(Transactions.updated).alias('latest'),
            )
        if time_basis in ['modified', 'created']:
            time_basis_field = getattr(Files, '{0}time'.format(time_basis[:1]))
            query = Files().select(
                fn.Min(time_basis_field).alias('earliest'),
                fn.Max(time_basis_field).alias('latest'),
            ).join(Transactions)

        query = query.where(search_field << item_list)
        row = query.get()
        if row.earliest is None or row.latest is None:
            message = ''
            raise HTTPError('404 Not Found', message)

        return {
            'earliest': row.earliest.strftime('%Y-%m-%d %H:%M:%S'),
            'latest': row.latest.strftime('%Y-%m-%d %H:%M:%S')
        }

    # Cherrypy requires these named methods.
    # pylint: disable=invalid-name
    @staticmethod
    @tools.json_in()
    @tools.json_out()
    def POST(item_type, time_basis):
        """Return file details for the list of file id's."""
        id_list = request.json
        return EarliestLatestFiles._get_earliest_latest(item_type, id_list, time_basis)
