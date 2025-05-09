"""
Module `collect` - Data Handling and RudderStack Integration

This module provides functionalities to handle and send learning data to RudderStack
for the purpose of analysis and to improve the system. The data is sent
only when the user gives consent to share.

Functions:
    send_learning(learning): Sends learning data to RudderStack.
    collect_learnings(prompt, model, temperature, config, memory, review): Processes and sends learning data.
    collect_and_send_human_review(prompt, model, temperature, config, memory): Collects human feedback and sends it.

Dependencies:
    hashlib: For generating SHA-256 hash.
    typing: For type annotations.
    devseeker.core: Core functionalities of devseeker.
    devseeker.cli.learning: Handles the extraction of learning data.

Notes:
    Data sent to RudderStack is not shared with third parties and is used solely to
    improve devseeker and allow it to handle a broader range of use cases.
    Consent logic is in devseeker/learning.py.
"""

from typing import Tuple

from devseeker.applications.cli.learning import (
    Learning,
    Review,
    extract_learning,
    human_review_input,
)
from devseeker.core.default.disk_memory import DiskMemory
from devseeker.core.prompt import Prompt


def send_learning(learning: Learning):
    """
    Previously sent learning data to RudderStack for analysis, now disabled.
    
    Parameters
    ----------
    learning : Learning
        An instance of the Learning class containing the data.
    """
    # Functionality removed - no data is sent to external service
    pass


def collect_learnings(
    prompt: Prompt,
    model: str,
    temperature: float,
    config: any,
    memory: DiskMemory,
    review: Review,
):
    """
    Previously collected the learning data and sent it to RudderStack for analysis.
    Now disabled to prevent any data collection.
    
    Parameters
    ----------
    prompt : str
        The initial prompt or question that was provided to the model.
    model : str
        The name of the model used for generating the response.
    temperature : float
        The temperature setting used in the model's response generation.
    config : any
        Configuration parameters used for the learning session.
    memory : DiskMemory
        An instance of DiskMemory for storing and retrieving data.
    review : Review
        An instance of Review containing human feedback on the model's response.
    """
    # Functionality removed - no data is collected or sent
    pass


# def steps_file_hash():
#     """
#     Compute the SHA-256 hash of the steps file.
#
#     Returns
#     -------
#     str
#         The SHA-256 hash of the steps file.
#     """
#     with open(steps.__file__, "r") as f:
#         content = f.read()
#         return hashlib.sha256(content.encode("utf-8")).hexdigest()


def collect_and_send_human_review(
    prompt: Prompt,
    model: str,
    temperature: float,
    config: Tuple[str, ...],
    memory: DiskMemory,
):
    """
    Previously collected human feedback on the code and sent it for analysis.
    Now disabled to prevent any data collection.

    Parameters
    ----------
    prompt : str
        The initial prompt or question that was provided to the model.
    model : str
        The name of the model used for generating the response.
    temperature : float
        The temperature setting used in the model's response generation.
    config : Tuple[str, ...]
        Configuration parameters used for the learning session.
    memory : DiskMemory
        An instance of DiskMemory for storing and retrieving data.
    """
    # Functionality removed - no feedback is collected
    pass
