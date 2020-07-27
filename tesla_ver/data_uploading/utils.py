from base64 import b64decode
from io import StringIO
from pandas import read_csv


def upload_string_to_df(content):
    """Parse a dash upload string into a single dataframe

                Args:
                    content (b64 string): string passed from the upload component
            """
    _, content_string = content.split(",")
    decoded = b64decode(content_string)
    fileish = StringIO(decoded.decode("utf-8"))
    return read_csv(fileish, sep="\t")

