import pandas as pd

from mas.agent import Property

class Dataset:

    def __init__(self, dataframe: pd.DataFrame) -> None:
        self.df = dataframe

    def properties(self) -> dict:
        d = {}
        for col in self.df:
            d[col] = Property(self.df[col])
        return d




    