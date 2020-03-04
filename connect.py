import sqlalchemy as db
import yaml


def create_engine_instance(from_yaml=True):
    """Gets credentials from yaml file an creates an engine instance

    :return: sqlalchemy engine class
    """
    # Read the credentials from yaml file
    if from_yaml:
        with open(r'db_credentials.yaml') as file:
            db_info = yaml.load(file, Loader=yaml.FullLoader)

    # Set engine. Important no spaces here 'mysql+<connector>'
    db_uri = 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}'.format(db_info['user'],
                                                          db_info['passwd'],
                                                          db_info['hostname'],
                                                          db_info['port'],
                                                          db_info['dbName'])

    return db.create_engine(db_uri, echo=False)
