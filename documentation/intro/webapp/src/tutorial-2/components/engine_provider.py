
import sqlalchemy

__all__ = ['EngineProvider']


class EngineProvider:
    """ `SQLAlchemy`_ support provider.

    This component provide support for use the ``SQLAlchemy`` library to
    connect to one database. The `get_engine` method is the only exposed
    service.

    The source database is configured using the `dsn` component attribute.

    If you need different database connections in the same application you
    can create multiple instances of this component and distribute them as
    needed.

    .. _SQLAlchemy: http://www.sqlalchemy.org/
    """

    dsn = 'sqlite:///application.db'

    def __init__(self, dsn=None):
        self._engine = sqlalchemy.create_engine(dsn or self.dsn)

    def get_engine(self) -> sqlalchemy.engine.Engine:
        """ Return an :class:`sqlalchemy.engine.Engine` object.
        :return: a ready to use :class:`sqlalchemy.engine.Engine` object.
        """
        return self._engine
