FONT_NAME = 0xProto
MAIN_WEIGHT = Regular
GLYPHS_FILE = $(FONT_NAME).glyphs
OUTPUT_DIR = fonts
UFO_DIR = $(FONT_NAME)-$(MAIN_WEIGHT).ufo

setup_woff2:
	git clone --recursive https://github.com/google/woff2.git
	cd woff2 && make clean all

setup:
	pipenv install
	$(MAKE) setup_woff2

ufo:
	glyphs2ufo $(GLYPHS_FILE)

build-otf: $(FONT_NAME)-$(MAIN_WEIGHT).ufo
	fontmake -u $(FONT_NAME)-$(MAIN_WEIGHT).ufo -o otf --output-dir $(OUTPUT_DIR)

build-ttf: $(FONT_NAME)-$(MAIN_WEIGHT).ufo
	fontmake -u $(FONT_NAME)-$(MAIN_WEIGHT).ufo -o ttf --output-dir $(OUTPUT_DIR)

build-woff2: $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ttf
	./woff2/woff2_compress $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ttf

build-all: $(FONT_NAME)-$(MAIN_WEIGHT).ufo
	$(MAKE) build-otf
	$(MAKE) build-ttf && $(MAKE) build-woff2

.PHONY: clean
clean:
	rm -rf $(OUTPUT_DIR)
	rm -rf $(UFO_DIR)
	rm $(FONT_NAME).designspace
