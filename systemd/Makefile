WWW_USER ?= www-data
ROOT := $(dir $(CURDIR))
components = schedule stats
services = $(components:%=snh48live-%.service)
timers = $(components:%=snh48live-%.timer)

.PHONY: all install reload enable start clean list $(components) $(components:%=install-%) $(components:%=enable-%) $(components:%=start-%)

all: $(components)

install: $(components:%=install-%)

reload:
	systemctl daemon-reload

enable: $(components:%=enable-%)

start: $(components:%=start-%)

clean:
	@- $(RM) $(services)

list:
	$(info all install reload enable start clean list $(components) $(components:%=install-%) $(components:%=enable-%) $(components:%=start-%))

$(components): %: snh48live-%.service

$(services): %: %.template
	sed 's:@@USER@@:${WWW_USER}:g; s:@@ROOT@@:${ROOT}:g' < $< > $@

$(components:%=install-%): install-%: snh48live-%.service snh48live-%.timer
	cp $^ /etc/systemd/system

$(components:%=enable-%): enable-%: snh48live-%.timer
	systemctl enable $<

$(components:%=start-%): start-%: snh48live-%.timer
	systemctl start $<
