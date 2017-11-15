import urllib2
import os

urls = ["http://www.mpia.de/homes/GEMS/GEMS_readme_20090807.pdf", "http://www.mpia.de/homes/GEMS/gems_20090807.fits"]

for url in urls:
	file_name = url.split('/')[-1]
	u = urllib2.urlopen(url)
	f = open(os.path.join("..", "thrid_party_data", file_name), 'wb')
	meta = u.info()
	print "Downloading: %s..." % (file_name)
	
	file_size_dl = 0
	block_sz = 8192
	while True:
		buffer = u.read(block_sz)
		if not buffer:
			break
	
		file_size_dl += len(buffer)
		f.write(buffer)
	
	f.close()
