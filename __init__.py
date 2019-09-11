__copyright__ = "Copyright (C) 2019 NXP Semiconductors"
__license__ = "MIT"

# logger config is done here and applyes to the entire current module
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.ERROR) # Make sure to keep level as ERROR for release. For debug purposes in can be manually set to DEBUG or INFO.