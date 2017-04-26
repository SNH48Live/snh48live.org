all: deploy

deploy:
	rsync -avP --delete root/ _site
