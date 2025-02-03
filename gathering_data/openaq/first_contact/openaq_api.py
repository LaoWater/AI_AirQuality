from fetch_countries import get_country_list
from fetch_locations import get_all_locations_in_country, get_locations_near
from fetch_bounding_box import get_locations_in_bbox


def run_all():
    print("\n🔹 Fetching available countries...")
    get_country_list()

    print("\n🔹 Fetching locations in Romania...")
    get_all_locations_in_country("RO")

    print("\n🔹 Fetching locations near London...")
    get_locations_near(51.5074, -0.1278)

    print("\n🔹 Fetching locations inside bounding box for London...")
    get_locations_in_bbox("-0.2,51.4,-0.1,51.6")


if __name__ == "__main__":
    run_all()
