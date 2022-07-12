import logging
import sys
from time import sleep

import guilogger

FORMATTER = logging.Formatter(
    fmt="%(levelname)1s | %(asctime)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@guilogger.app(
    level=logging.INFO,
    formatter=FORMATTER,
    title="testing",
    max_steps=len(sys.argv) - 1,
    close_after=True,
)
def main(args=sys.argv[1:], *, log_handler):
    logger = logging.getLogger(__name__)
    logger.level = logging.INFO
    logger.addHandler(log_handler)
    logger.propagate = True

    try:
        for arg in args:
            sleep(1)
            logger.info(f"Processing: {arg}")
        logger.warning("watch out! ")
        raise ValueError("Boom! ")
    except Exception as e:
        logger.exception(e)
        raise e

    logger.done()


if __name__ == "__main__":
    main()
