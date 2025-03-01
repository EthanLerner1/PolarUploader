from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Self, List

import jsonmaster
from jsonmaster import open_json

from polarsteps_data_parser import utils
from polarsteps_data_parser.utils import parse_date, find_folder_by_id, list_files_in_folder


@dataclass
class Location:
    """Location as tracked by the travel tracker."""

    lat: float
    lon: float
    time: datetime

    @classmethod
    def from_json(cls, data: dict) -> Self:
        """Parse object from JSON data."""
        return Location(lat=data["lat"], lon=data["lon"], time=parse_date(data["time"]))

    @staticmethod
    def load_locations(input_dir: Path) -> List['Location']:
        LOCATIONS_FILE: str = 'locations.json'

        locations_path: Path = Path(input_dir, LOCATIONS_FILE)

        with open_json(locations_path.__str__()) as jf:
            locations_json: dict = jf.dict()

        return [Location.from_json(x) for x in locations_json['locations']]


@dataclass
class StepLocation:
    """Location as provided by a step."""

    lat: float
    lon: float
    name: str
    country: str

    @classmethod
    def from_json(cls, data: dict) -> Self:
        """Parse object from JSON data."""
        return StepLocation(
            lat=data["lat"],
            lon=data["lon"],
            name=data["name"],
            country=data["detail"],
        )


@dataclass
class Follower:
    """Follower (can leave comments)."""

    user_id: str
    username: str
    first_name: str
    last_name: str

    @classmethod
    def from_json(cls, data: dict) -> Self:
        """Parse object from JSON data."""
        return Follower(
            user_id=data["id"],
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
        )

    @property
    def name(self) -> str:
        """Name of the follower."""
        return f"{self.first_name} {self.last_name}"


@dataclass
class StepComment:
    """Comment connected to a step."""

    comment_id: str
    text: str
    date: datetime
    follower: Follower

    @classmethod
    def from_json(cls, data: dict) -> Self:
        """Parse object from JSON data."""
        return StepComment(
            comment_id=data["id"],
            text=data["text"],
            date=parse_date(data["creation_time"]),
            follower=Follower.from_json(data["user"]),
        )


@dataclass
class Step:
    """Polarsteps Step object."""

    step_id: str
    name: str
    description: str
    location: StepLocation
    start_time: date
    creation_time: str
    timezone_id: str
    photos: list[Path]
    videos: list[Path]
    comments: list[StepComment]

    @classmethod
    def from_json(cls, data: dict, input_dir: Path) -> Self:
        """Parse object from JSON data."""
        s = Step(
            step_id=data["id"],
            name=data["name"] or data["display_name"],
            description=data["description"],
            location=StepLocation.from_json(data["location"]),
            start_time=parse_date(data["start_time"]),
            creation_time=data['creation_time'],
            photos=[],
            videos=[],
            comments=[],
            timezone_id=data['timezone_id']
        )
        s.load_media(input_dir)
        return s

    def load_media(self, input_dir: Path) -> None:
        """Load photos and videos for the step."""
        step_dir = find_folder_by_id(input_dir, self.step_id)
        if step_dir is None:
            self.photos = []
            self.videos = []
        else:
            self.photos = list_files_in_folder(step_dir / "photos", dir_has_to_exist=False)
            self.videos = list_files_in_folder(step_dir / "videos", dir_has_to_exist=False)


@dataclass
class Trip:
    """Polarsteps trip object."""

    name: str
    start_date: datetime
    end_date: datetime
    cover_photo_path: str
    steps: list[Step]
    id: int = 0

    @classmethod
    def from_path(cls, input_dir: Path) -> Self:
        TRIP_FILENAME: str = 'trip.json'
        trip_json_path: Path = input_dir / TRIP_FILENAME

        with jsonmaster.open_json(trip_json_path.__str__()) as jf:
            trip_data: dict = jf.dict()

        """Parse object from JSON data."""
        return Trip(
            name=trip_data["name"],
            start_date=parse_date(trip_data.get("start_date")),
            end_date=parse_date(trip_data.get("end_date")),
            cover_photo_path=trip_data["cover_photo_path"],
            steps=[Step.from_json(step, input_dir.parent) for step in trip_data.get("all_steps")],
        )
