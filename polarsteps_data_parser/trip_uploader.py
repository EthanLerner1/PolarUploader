import requests

from polarsteps_data_parser.model import Step, Trip


class TripUploader:
    URL: str = 'https://www.polarsteps.com/api/steps'

    def __init__(self, trip: Trip) -> None:
        self.__trip: Trip = trip


    def upload(self, step: Step, location_id: int):
        BODY = {
            "trip_id": self.__trip.id,
            "location_id": location_id,
            "name": step.name,
            "description": step.description,
            "start_time": step.start_time,
            "creation_time": step.creation_time,
            "timezone_id": step.timezone_id,
            "type": 1
        }

        response = requests.post(url=self.URL, json=BODY)
