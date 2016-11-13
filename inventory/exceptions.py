class AlreadyAssigned(Exception):
    def __init__(self, helper):
        self.helper = helper
