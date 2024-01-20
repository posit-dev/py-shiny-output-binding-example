# Example of building a custom output binding for Shiny. This example
# demonstrates the use of HTMLDependency to include external javascript and css
# files directly in the output element instead of requiring them to be included
# in the ui head everytime

from pathlib import Path

import pandas as pd
from htmltools import HTMLDependency

from shiny import App, Inputs, ui
from shiny.module import resolve_id
from shiny.render.renderer import Jsonifiable, Renderer


class render_tabulator(Renderer[pd.DataFrame]):
    """
    Render a pandas dataframe as a tabulator table.
    """

    def auto_output_ui(self):
        """
        Express UI for the tabulator renderer
        """
        return ui.output_tabulator(self.output_name)

    async def transform(self, value: pd.DataFrame) -> Jsonifiable:
        """
        Transform a pandas dataframe into a JSONifiable object that can be
        passed to the tabulator HTML dependency.
        """
        if not isinstance(value, pd.DataFrame):
            # Throw an error if the value is not a dataframe
            raise TypeError(f"Expected a pandas.DataFrame, got {type(value)}. ")

        # Get data from dataframe as a list of lists where each inner list is a
        # row, column names as array of strings and types of each column as an
        # array of strings
        return {
            "data": value.values.tolist(),
            "columns": value.columns.tolist(),
            "type_hints": value.dtypes.astype(str).tolist(),
        }


tabulator_dep = HTMLDependency(
    "tabulator",
    "5.5.2",
    source={"subdir": "tabulator"},
    script={"src": "tableComponent.js", "type": "module"},
    stylesheet={"href": "tabulator.min.css"},
    all_files=True,
)


def output_tabulator(id, height="200px"):
    """
    A shiny output that renders a tabulator table. To be paired with
    `render.data_frame` decorator.
    """
    return ui.div(
        tabulator_dep,
        # Use resolve_id so that our component will work in a module
        id=resolve_id(id),
        class_="shiny-tabulator-output",
        style=f"height: {height}",
    )


app_ui = ui.page_fluid(
    ui.input_slider("n", "Number of rows to show", 1, 20, 10),
    output_tabulator("tabulatorTable"),
)


def server(input: Inputs):
    @render_tabulator
    def tabulatorTable():
        csv_path = Path(__file__).parent / "mtcars.csv"
        return pd.read_csv(csv_path).head(input.n())


app = App(app_ui, server)
