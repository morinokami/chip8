all: run

.PHONY: run
run:
	@cd chip8; python app.py ${ROM}

.PHONY:help
help:
	@cd chip8; python app.py -h

.PHONY: test
test:
	@cd chip8; python -m pytest
