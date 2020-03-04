from sqlalchemy import Column, Integer, String, Text, DateTime, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
import connect as head_con

Base = declarative_base()


class HeadlinesModel(Base):
    """Data model for headlines """
    __tablename__ = 'headlines_elmostrador'

    id = Column(Integer, primary_key=True)
    raw_html_out = Column(String(150), nullable=False)
    section = Column(String(100), nullable=True)
    news_date = Column(DateTime, nullable=True)
    headline = Column(Text, nullable=True)
    scrap_date = Column(DateTime, nullable=False)

    def __repr__(self):
        return '<Example model {}>'.format(self.id)


def create_headlines_table(metadata_instance, resource_name):

    table_tmp = Table('headlines_{0}'.format(resource_name), metadata_instance,
                      Column('id', Integer, primary_key=True),
                      Column('raw_html_out', String(100), nullable=True),
                      Column('news_date', DateTime, nullable=True),
                      Column('headline', Text, nullable=True),
                      Column('scrap_date', DateTime, nullable=False))

    metadata_instance.create_all(engine)


if __name__ == "__main__":

    engine = head_con.create_engine_instance()

    # Store metadata in this object
    metadata = MetaData()

    # Create elmostrador headlines table
    create_headlines_table(metadata, "elmostrador")
