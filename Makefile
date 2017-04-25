all: deploy

deploy:
	rsync -avP --delete src/ _site
