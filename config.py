# starting task
START_URL = "/wiki/Morgan_Freeman"
START_IS_MOVIE = False
START_IS_FILMOGRAPHY = False

# delay between each request
DELAY = 0.25

# timeout, in seconds, for the spider to close itself (set to 0 to disable timeout)
CLOSE_TIMEOUT = 0  # allow crawler to run for 10 minutes

# number of parsed item for the spider to close itself (set to 0 to disable item count)
CLOSE_ITEM_COUNT = 0

# the output file to store result as json (if None then no file is dumped)
JSON_OUTPUT_FILE = "output/out.json"

# place to stored paused file
JOBDIR = "jobdir"
