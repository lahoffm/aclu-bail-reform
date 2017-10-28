# Called by batchfile to generate timestamped log file name.
# Requires 1 command line argument

from datetime import datetime
import os
import sys

timestamp = datetime.now().strftime('%Y-%m-%d_time_%H-%M-%S')
county = sys.argv[1].replace('\\','-') # in case we're given subfolders like bibb\jailCrawler - must be in Windows file format \
print(os.path.abspath(os.curdir) + '\\logs' + '\\' + county + '_' + timestamp + '.log')