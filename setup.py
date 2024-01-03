from distutils.core import setup
import py2exe
import sys

sys.argv.append("py2exe")
setup(	options={"py2exe":{"dist_dir":"dist"}},
        windows=[ {"script":'anathema.py'}]
	)


