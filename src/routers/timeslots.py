from src.internals.timeslots import ValidationError, prettify_timeslots
from fastapi import APIRouter, Request, HTTPException


router = APIRouter()


@router.post("/prettify")
async def prettify(request: Request):
    """
    Prettify a json body representing opening hours in the "ugly format".

    The ugly format is defined as a dictionary with the following format
        weekday: [
            {
                "status": "open"/"close"
                "value": int
            }
            ...
        ]
    where value is the number of seconds from the midnight of the day. 
    Days which are missing or where there are no entries are considered days where the restaurant is closed.

    The prettified output is in a dictionary with the following format
        weekday: "time_opening_1 - time_closing_1, ..., time_opening_n - time_closing_n"
    where both time_opening and time_closing are in the 12h clock format. 
    Minutes and seconds are displayed only if needed. 

    Parameters
    ----------
    request : Request
        The HTTP request that fastAPI receives

    Returns
    -------
    Dict[str, str]: the prettify JSON


    Raises
    ------
    HTTPException
        422: If it is impossible to process the JSON file
    """

    body = await request.body()

    try:
        preatty_timeslots = prettify_timeslots(body.decode('utf-8'))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return preatty_timeslots
