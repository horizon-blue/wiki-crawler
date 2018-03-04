import os

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

# starting task
START_URL = "/wiki/Morgan_Freeman"
START_IS_MOVIE = False
START_IS_FILMOGRAPHY = False

# delay between each request
DELAY = 0.25

# timeout, in seconds, for the spider to close itself (set to 0 to disable timeout)
CLOSE_TIMEOUT = 0

# number of parsed item for the spider to close itself (set to 0 to disable item count)
CLOSE_ITEM_COUNT = 0

# decide whether or not to resume from previous work
RESUME = True

# the output file to store result as json (if None then no file is dumped)
# this will be the recover file if RESUME is True
JSON_OUTPUT_FILE = "output/out.json"

# place to stored paused file
# this will be the recover file if RESUME is True
JOBDIR = "jobdir"

# name of the database file.
DATABASE_FILE = "output/external.sqlite3"
