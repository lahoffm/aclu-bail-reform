# Called by batchfile to generate timestamped log file name.
# Requires 1 command line argument

from datetime import datetime
import os
import sys

timestamp = datetime.now().strftime('%Y-%m-%d_time_%H-%M-%S')
print(os.path.abspath(os.curdir) + '\\logs' + '\\' + sys.argv[1] + '_' + timestamp + '.log')