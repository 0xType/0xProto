FONT_NAME = 0xProto
MAIN_WEIGHT = Regular
ITALIC = Italic
SOURCE_DIR = sources
MAIN_GLYPHS_FILE = $(SOURCE_DIR)/$(FONT_NAME).glyphspackage
ITALIC_GLYPHS_FILE = $(SOURCE_DIR)/$(FONT_NAME)-$(ITALIC).glyphspackage
OUTPUT_DIR = fonts
WOFF2_DIR = woff2

setup:
	pip install -r requirements.txt
	if [ ! -e $(WOFF2_DIR) ]; then $(MAKE) setup-woff2; fi

setup-woff2:
	git clone --recursive https://github.com/google/woff2.git $(WOFF2_DIR)
	cd $(WOFF2_DIR) && make clean all

.PHONY: build
build:
	$(MAKE) clean
	$(MAKE) compile-all

compile-otf-main: $(MAIN_GLYPHS_FILE)
	fontmake -a -g $(MAIN_GLYPHS_FILE) -o otf --output-dir $(OUTPUT_DIR)

compile-otf-italic: $(ITALIC_GLYPHS_FILE)
	fontmake -a -g $(ITALIC_GLYPHS_FILE) -o otf --output-dir $(OUTPUT_DIR)

compile-ttf-main: $(MAIN_GLYPHS_FILE)
	fontmake -a -g $(MAIN_GLYPHS_FILE) -o ttf --output-dir $(OUTPUT_DIR)

compile-ttf-italic: $(ITALIC_GLYPHS_FILE)
	fontmake -a -g $(ITALIC_GLYPHS_FILE) -o ttf --output-dir $(OUTPUT_DIR)

compile-woff2-main: $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ttf
	./woff2/woff2_compress $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ttf

compile-woff2-italic: $(OUTPUT_DIR)/$(FONT_NAME)-$(ITALIC).ttf
	./woff2/woff2_compress $(OUTPUT_DIR)/$(FONT_NAME)-$(ITALIC).ttf

compile-main: $(MAIN_GLYPHS_FILE)
	$(MAKE) compile-otf-main
	$(MAKE) compile-ttf-main && $(MAKE) compile-woff2-main

compile-italic: $(ITALIC_GLYPHS_FILE)
	$(MAKE) compile-otf-italic
	$(MAKE) compile-ttf-italic && $(MAKE) compile-woff2-italic

compile-all:
	$(MAKE) compile-main
	$(MAKE) compile-italic

.PHONY: clean
clean:
	if [ -e $(OUTPUT_DIR) ]; then rm -rf $(OUTPUT_DIR); fi

install-otf-main: $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).otf
	cp $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).otf $(HOME)/Library/Fonts

install-otf-italic: $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).otf
	cp $(OUTPUT_DIR)/$(FONT_NAME)-$(ITALIC).otf $(HOME)/Library/Fonts

install-latest:
	$(MAKE) build
	$(MAKE) install-otf-main
	$(MAKE) install-otf-italic

close-vscode:
	@osascript -e 'if application "Visual Studio Code" is running then' \
	           -e 'tell application "Visual Studio Code" to quit' \
	           -e 'end if'

debug:
	$(MAKE) close-vscode
	$(MAKE) clean
	$(MAKE) ufo
	$(MAKE) compile-otf-main
	$(MAKE) install-otf-main
	code .
