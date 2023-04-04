from dataclasses import dataclass
from PIL import Image
from io import BytesIO

from geoguesser_ai.etl.api import StreetViewStaticApi
from geoguesser_ai.etl.coordinate import Coordinate


@dataclass
class StreetView:
    coordinate: Coordinate
    heading: float
    image: bytes

    def load_image(self) -> Image:
        return Image.open(BytesIO(self.image))


@dataclass
class StreetPanoramic:
    coordinate: Coordinate
    street_views_list: list[StreetView, StreetView, StreetView, StreetView]

    def __setattr__(self, name, value):
        if name == 'panoramic' and (
                value[0].heading != 0 or
                value[1].heading != 90 or
                value[2].heading != 180 or
                value[3].heading != 270):
            raise ValueError(f"StreetView elements inside {name} must be in heading order [0, 90, 180, 270]")
        self.__dict__[name] = value

    def show(self):
        images = [street_view.load_image() for street_view in self.street_views_list]

        widths, heights = zip(*(img.size for img in images))
        total_width = sum(widths)
        max_height = max(heights)

        panoramic_image = Image.new('RGB', (total_width, max_height))

        x_offset = 0
        for im in images:
            panoramic_image.paste(im, (x_offset, 0))
            x_offset += im.size[0]

        panoramic_image.show()


class StreetViewer:
    fov = 90
    headings = [0, 90, 180, 270]

    def __init__(self, api_key: str, size: tuple[int, int] = (256, 256)):
        self.api = StreetViewStaticApi(api_key)
        self.size = size

    def get_random_street_view_panoramic(self) -> StreetPanoramic:
        coord = self._get_random_street_view_coordinate()
        return StreetPanoramic(
            coordinate=coord,
            street_views_list=[self._get_street_view(coord, heading) for heading in self.headings]
        )

    def _get_random_street_view_coordinate(self) -> Coordinate:
        while True:
            # Get land map coordinates
            coord = Coordinate.random_land_coordinate()
            print(f"Trying with {coord.latitude} {coord.longitude}")
            coord = self.api.has_image(coord=coord, radius=200)
            if coord:
                print(f"Hit! -> {coord.latitude} {coord.longitude}")
                return coord

    def _get_street_view(self, coord: Coordinate, heading: float) -> StreetView:
        return StreetView(
            coordinate=coord,
            heading=heading,
            image=self.api.get_image(
                coord=coord,
                size=self.size,
                fov=self.fov,
                heading=heading
            )
        )
