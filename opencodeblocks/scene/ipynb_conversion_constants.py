""" Module with the constants used to converter to ipynb and from ipynb """

from typing import Dict

MARGIN_X: float = 75
MARGIN_BETWEEN_BLOCKS_X: float = 50
MARGIN_Y: float = 60
MARGIN_BETWEEN_BLOCKS_Y: float = 5
BLOCK_MIN_WIDTH: float = 400
TITLE_MAX_LENGTH: int = 60
SOCKET_HEIGHT: float = 44.0

BLOCK_TYPE_TO_NAME: Dict[str, str] = {
    "code": "OCBCodeBlock",
    "markdown": "OCBMarkdownBlock",
}

BLOCK_TYPE_SUPPORTED_FOR_IPYG_TO_IPYNB = {"OCBCodeBlock", "OCBMarkdownBlock"}

DEFAULT_NOTEBOOK_DATA = {
    "cells": [],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.6.4",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 4,
}

DEFAULT_CODE_CELL = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {
        "_cell_guid": "b1076dfc-b9ad-4769-8c92-a6c4dae69d19",
        "_uuid": "8f2839f25d086af736a60e9eeb907d3b93b6e0e5",
        "execution": {
            "iopub.execute_input": "2021-11-23T21:43:41.246727Z",
            "iopub.status.busy": "2021-11-23T21:43:41.246168Z",
            "iopub.status.idle": "2021-11-23T21:43:41.260389Z",
            "shell.execute_reply": "2021-11-23T21:43:41.260950Z",
            "shell.execute_reply.started": "2021-11-22T18:36:28.843251Z",
        },
        "tags": [],
    },
    "outputs": [],
    "source": [],
}

DEFAULT_MARKDOWN_CELL = {
    "cell_type": "markdown",
    "metadata": {
        "papermill": {
            "duration": 0,
            "end_time": "2021-11-23T21:43:55.202848",
            "exception": False,
            "start_time": "2021-11-23T21:43:55.174774",
            "status": "completed",
        },
        "tags": [],
    },
    "source": [],
}
