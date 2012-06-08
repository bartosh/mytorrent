test:
	@rm -f torrentc
	@nosetests -v --with-coverage --cover-package ./torrent
