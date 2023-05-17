FONT_NAME = 0xProto
MAIN_WEIGHT = Regular
GLYPHS_FILE = $(FONT_NAME).glyphs
OUTPUT_DIR = fonts
UFO_DIR = $(FONT_NAME)-$(MAIN_WEIGHT).ufo
WOFF2_DIR = woff2

setup:
	pip install -r requirements.txt
	if [ ! -e $(WOFF2_DIR) ]; then $(MAKE) setup_woff2; fi

setup-woff2:
	git clone --recursive https://github.com/google/woff2.git
	cd $(WOFF2_DIR) && make clean all

.PHONY: build
build:
	$(MAKE) clean
	$(MAKE) ufo
	$(MAKE) compile-all

ufo:
	glyphs2ufo $(GLYPHS_FILE)

compile-otf: $(FONT_NAME)-$(MAIN_WEIGHT).ufo
	fontmake -u $(FONT_NAME)-$(MAIN_WEIGHT).ufo -o otf --output-dir $(OUTPUT_DIR)

compile-ttf: $(FONT_NAME)-$(MAIN_WEIGHT).ufo
	fontmake -u $(FONT_NAME)-$(MAIN_WEIGHT).ufo -o ttf --output-dir $(OUTPUT_DIR)

compile-woff2: $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ttf
	./woff2/woff2_compress $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ttf

compile-all: $(FONT_NAME)-$(MAIN_WEIGHT).ufo
	$(MAKE) compile-otf
	$(MAKE) compile-ttf && $(MAKE) compile-woff2

.PHONY: clean
clean:
	if [ -e $(OUTPUT_DIR) ]; then rm -rf $(OUTPUT_DIR); fi
	if [ -e $(UFO_DIR) ]; then rm -rf $(UFO_DIR); fi
	if [ -e $(FONT_NAME).designspace ]; then rm $(FONT_NAME).designspace; fi
