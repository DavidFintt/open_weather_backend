from openweather_sdk.exceptions import (
    APIKeyInvalidError,
    CityNotFoundError,
    InvalidCoordinatesError,
    InvalidInputError,
    NoWeatherDataError,
    OpenWeatherAPIError,
    RateLimitExceededError,
    RequestTimeoutError,
)

EXCEPTION_STATUS_MAP = {
    CityNotFoundError: 404,
    InvalidCoordinatesError: 422,
    InvalidInputError: 422,
    NoWeatherDataError: 404,
    APIKeyInvalidError: 500,
    OpenWeatherAPIError: 502,
    RateLimitExceededError: 429,
    RequestTimeoutError: 504,
}
