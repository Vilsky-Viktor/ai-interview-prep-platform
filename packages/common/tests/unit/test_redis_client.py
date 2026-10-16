from prepza_common.constants import REDIS_HEALTH_CHECK_SECONDS, REDIS_RETRIES
from prepza_common.redis_client import redis_client
from redis.exceptions import ConnectionError, TimeoutError


def test_a_dropped_connection_is_retried_instead_of_failing_the_request():
    connection = redis_client("redis://localhost:6379").connection_pool.make_connection()

    assert connection.retry._retries == REDIS_RETRIES
    assert ConnectionError in connection.retry._supported_errors
    assert TimeoutError in connection.retry._supported_errors
    assert connection.health_check_interval == REDIS_HEALTH_CHECK_SECONDS
