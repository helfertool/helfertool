import string
import re
import openpyxl


def cleanName(name):
    """ Cleans the name to be a valid sheet name in excel.

    The characters [ ] : * ? / \\ are removed.
    """
    return re.sub(r'[\[\]:*?\\\/]', '', name)


def escape(payload):
    if not payload:
        return ""

    # http://blog.zsec.uk/csv-dangers-mitigations/
    if payload[0] in ('@', '+', '-', '=', '|'):
        payload = payload.replace("|", "\\|")
        payload = "'" + payload + "'"
    return payload


class CellIterator():
    def __init__(self, worksheet):
        self.__cols = 1
        self.__rows = 1
        self.worksheet = worksheet

    def right(self) -> str:
        self.__cols += 1
        return self.get()

    def down(self, column_return=True) -> str:
        self.__rows += 1
        if column_return:
            self.column_return()
        return self.get()

    def column_return(self) -> str:
        self.__cols = 1
        return self.get()

    def _int_to_column(self, colnum):
        colstr = ''
        while colnum != 0:
            colstr += chr((colnum % 26) + ord('A') - 1)
            colnum = colnum // 26
        return colstr

    @property
    def column(self) -> str:
        return self._int_to_column(self.__cols)

    @property
    def colint(self) -> int:
        return self.__cols

    @property
    def row(self) -> int:
        return self.__rows

    def get(self) -> str:
        return "{}{}".format(self.column, self.row)

    @property
    def cell(self) -> openpyxl.cell.Cell:
        return self.worksheet.cell(self.__rows, self.__cols)

    def write(self, data, style=None):
        self.cell.value = data

        if style is not None:
            if not isinstance(style, (list, tuple)):
                style = [style]

            for s in style:
                if isinstance(s, openpyxl.styles.Font):
                    self.cell.font = s
                elif isinstance(s, openpyxl.styles.PatternFill):
                    self.cell.fill = s
                elif isinstance(s, openpyxl.styles.Border):
                    self.cell.border = s
                elif isinstance(s, openpyxl.styles.Alignment):
                    self.cell.alignment = s
                elif isinstance(s, openpyxl.styles.Protection):
                    self.cell.protection = s

        return self

    def range_to(self, column, row):
        """ generate a excel range definition in the form A1:B2

        for the iterator currently pointing to A1 and column=B and row=2

        if column or row is None, set it to the value of the iterator.
        if column or row is -1, set it to this dimensions max value
        """

        if column is None:
            column = self.column
        if row is None:
            row = self.row
        if column == -1:
            column = self._int_to_column(openpyxl.xml.constants.MAX_COLUMN)
        if row == -1:
            row = openpyxl.xml.constants.MAX_ROW

        return "{}:{}{}".format(self.get(), column, row)

    def load(self, cell):
        column = 0
        while cell and cell[0] in string.ascii_uppercase:
            column = column * 26 + (ord(cell[0]) - ord('A') + 1)
            cell = cell[1:]

        row = int(cell)
        self.__cols = column
        self.__rows = row
        return self.get()
