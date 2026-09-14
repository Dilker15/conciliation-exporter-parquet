from shared_layer.repositories.settlement_repository import SettlementRepository



class SettlementService:


    def __init__(self,repository:SettlementRepository)->None:
        self._repository = repository


    def get_settlements_paginated(self,file_id:str,limit:int,page:int)->tuple[list[dict], dict | None]:
        return self._repository.get_settlements_paginated(file_id=file_id,limit=limit,last_evaluated_key=page)