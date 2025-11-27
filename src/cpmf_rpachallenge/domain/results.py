"""Results page selectors for rpachallenge.com"""

import re
from dataclasses import dataclass


class Results:
    """Selectors for the results displayed after completing the challenge."""

    # Container for all result messages
    CONTAINER = ".congratulations"

    # Individual message elements
    MESSAGE_TITLE = "div.message1"  # "Congratulations!"
    MESSAGE_DETAILS = "div.message2"  # "Your success rate is X% ..."

    @staticmethod
    def parse_results(message2_text: str) -> "ResultData":
        """Parse the results message into structured data.

        Args:
            message2_text: Text from div.message2, e.g.,
                "Your success rate is 85% ( 60 out of 70 fields) in 4149 milliseconds"

        Returns:
            ResultData with parsed values
        """
        match = re.search(
            r"(\d+)%.*?(\d+)\s+out\s+of\s+(\d+).*?(\d+)\s+milliseconds",
            message2_text,
        )
        if match:
            return ResultData(
                success_rate=int(match.group(1)),
                fields_correct=int(match.group(2)),
                total_fields=int(match.group(3)),
                time_ms=int(match.group(4)),
                raw_message=message2_text,
            )
        return ResultData(raw_message=message2_text)


@dataclass
class ResultData:
    """Parsed result data from the challenge."""

    success_rate: int = 0
    fields_correct: int = 0
    total_fields: int = 70  # 7 fields x 10 rounds
    time_ms: int = 0
    raw_message: str = ""

    @property
    def fields_incorrect(self) -> int:
        return self.total_fields - self.fields_correct

    @property
    def time_seconds(self) -> float:
        return self.time_ms / 1000.0
