from dataclasses import dataclass


@dataclass
class SettlementError:
    settlement_id:str
    file_id: str
    row_number: int
    errors: list[str]
    raw_data: dict