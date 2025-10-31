import asyncio
import datetime
import random
import sys

CHANCES_BY_TIME_OF_DAY = {
    "low": {
        "slow_request": 0.1,
        "sluggish_request": 0.05,
    },
    "mid": {
        "slow_request": 0.1,
        "sluggish_request": 0.05,
    },
    "high": {
        "slow_request": 0.4,
        "sluggish_request": 0.1,
    },
}

TIME_RANGES_BY_REQUEST_SPEED_CATEGORY = {
    "regular": (0, 1),
    "slow": (1, 5),
    "sluggish": (5, 30),
}

HIGH_TRAFFIC_HOURS = [10, 11, 13, 14, 15]
MID_TRAFFIC_HOURS = [8, 9, 16, 17]
REQUESTS_RANGE_BY_TRAFFIC = {"high": (100, 300), "mid": (50, 100), "low": (5, 10)}
BRT = datetime.timezone(datetime.timedelta(hours=-3))


def get_chances_by_time_of_day(weekday, hour):
    if weekday < 5:
        if hour in HIGH_TRAFFIC_HOURS:
            return "high"

        if hour in MID_TRAFFIC_HOURS:
            return "mid"

    return "low"


async def send_email_via_http_request():
    await asyncio.sleep(_calculate_time_for_each_request())


def _calculate_time_for_each_request():
    now = datetime.datetime.now().astimezone(BRT)

    traffic = get_chances_by_time_of_day(now.weekday(), now.hour)
    chances = CHANCES_BY_TIME_OF_DAY[traffic]

    chance = random.uniform(0, 1)
    if chance < chances["sluggish_request"]:
        time_range = TIME_RANGES_BY_REQUEST_SPEED_CATEGORY["sluggish"]
    elif chance < chances["slow_request"]:
        time_range = TIME_RANGES_BY_REQUEST_SPEED_CATEGORY["slow"]
    else:
        time_range = TIME_RANGES_BY_REQUEST_SPEED_CATEGORY["regular"]

    return random.uniform(*time_range)


if __name__ == "__main__":
    now = datetime.datetime.now().astimezone(BRT)
    traffic = get_chances_by_time_of_day(now.weekday(), now.hour)
    no_of_requests = REQUESTS_RANGE_BY_TRAFFIC[traffic]
    print(random.randint(*no_of_requests))
    sys.exit(0)
