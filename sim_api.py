# sim_api.py

import base64
import pickle
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sim_core import do_experiment_one_extra

app = FastAPI()


class SimulationRequest(BaseModel):
    champion_pickle: str
    opponent_pickle: str
    item_list_pickle: str
    buff_list_pickle: str
    t: float
    frame_rate: int


@app.post("/simulate")
def simulate(request: SimulationRequest):
    try:
        champion = pickle.loads(base64.b64decode(request.champion_pickle))
        opponent = pickle.loads(base64.b64decode(request.opponent_pickle))
        item_list = pickle.loads(base64.b64decode(request.item_list_pickle))
        buff_list = pickle.loads(base64.b64decode(request.buff_list_pickle))

        results = do_experiment_one_extra(
            champion,
            opponent,
            item_list,
            buff_list,
            request.t,
            request.frame_rate,
        )

        # Pickle the results to send back
        results_pickle = base64.b64encode(pickle.dumps(results)).decode("utf-8")
        return {"results_pickle": results_pickle}
    except Exception as e:
        # print stack trace
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}
