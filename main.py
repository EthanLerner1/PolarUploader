import jsonmaster

from pathlib import Path

from polarsteps_data_parser.model import Trip

TRIP_FOLDER_LOCATION: Path = Path(r'c:\Users\User\Downloads\user_data\trip\vietnam_15564385')
NEW_TRIP_ID: int = 16537211

trip: Trip = Trip.from_path(TRIP_FOLDER_LOCATION)
trip.id = NEW_TRIP_ID



print(trip)


