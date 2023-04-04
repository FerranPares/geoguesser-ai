from typing import Optional

import requests
from geoguesser_ai.etl.coordinate import Coordinate


class StreetViewStaticApi:
    endpoint = "https://maps.googleapis.com/maps/api/streetview"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def has_image(self, coord: Coordinate, radius: int) -> Optional[Coordinate]:

        response = requests.get(
            f"{self.endpoint}/metadata",
            params={
                "location": f"{coord.latitude},{coord.longitude}",
                "key": self.api_key,
                "radius": radius,
            },
        ).json()

        if response["status"] == "OVER_QUERY_LIMIT":
            raise Exception("You have exceeded your daily quota or per-second quota for this API.")
        if response["status"] == "REQUEST_DENIED":
            raise Exception("Your request was denied by the server. Check your API key.")
        if response["status"] == "UNKNOWN_ERROR":
            raise Exception("An unknown error occurred on the server.")

        if response["status"] == "OK" and "location" in response:
            return Coordinate(
                latitude=response["location"]["lat"],
                longitude=response["location"]["lng"]
            )

    def get_image(
            self,
            coord: Coordinate,
            size: tuple[int, int],
            heading: float = 0.0,
            pitch: float = 0.0,
            fov: float = 90.0
    ) -> bytes:
        if max(size) > 640:
            raise ValueError(f"{max(size)} > 640 Maximum size exceeded.")
        return requests.get(
            self.endpoint,
            params={
                "location": f"{coord.latitude},{coord.longitude}",
                "size": f"{size[0]}x{size[1]}",
                "heading": heading,
                "pitch": pitch,
                "fov": fov,
                "key": self.api_key,
            },
        ).content
