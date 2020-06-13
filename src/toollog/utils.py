import logging

class HelfertoolDatabaseHandler(logging.Handler):
    """
    A Log handler to store logs into the database, resolving extras as foreign keys
    """

    def __init__(self, *args, **kwargs):
        super(HelfertoolDatabaseHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        """
        Store the record into the database
        will resolve the following fields from 'extras':

        - 'event': the Event used
        - 'user': the logged in User that emitted the event that created the log
        - 'helper': the helper that issued the log
        - 'shift': the relevant shift
        - 'job': the relevant job
        - 'giftset': the giftset
        - 'gift': a singluar gift type
        - 'changed_user': one user referring to another user
        - 'added_user': one user referring to another user
        - 'agreement': Useragreement


        All of the above may be suffixed with _pk to refer to only a key, not an object
        If the non-_pk version is only a string, the _pk version is preferred.
        If it is an object of the expected type the _pk version will be used to verify.
        (since it is often used to store only the name)

        It will also concatenate other, extra information as an extra-field as json.
        """
        # TODO
        pass