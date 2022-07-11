import logging
import sys
from time import sleep

import guilogger

@guilogger.app(level=logging.INFO, title="testing", max_steps=10)
def main(args=sys.argv[1:], *, log_handler):
    logger = logging.getLogger(__name__)
    logger.level = logging.INFO
    logger.addHandler(log_handler)
    logger.propagate = True

    for arg in args:
        sleep(2)
        logger.info(f"Processing: {arg}")
    guilogger.log_done(logger)


if __name__ == '__main__':
    main()
