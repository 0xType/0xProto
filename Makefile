FONT_NAME = 0xProto
MAIN_WEIGHT = Regular
ITALIC = Italic
SOURCE_DIR = sources
MAIN_GLYPHS_FILE = $(SOURCE_DIR)/$(FONT_NAME).glyphs
ITALIC_GLYPHS_FILE = $(SOURCE_DIR)/$(FONT_NAME)-$(ITALIC).glyphs
OUTPUT_DIR = fonts
MAIN_UFO_DIR = $(SOURCE_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ufo
ITALIC_UFO_DIR = $(SOURCE_DIR)/$(FONT_NAME)-$(ITALIC).ufo
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
	$(MAKE) ufo
	$(MAKE) compile-all

ufo:
	glyphs2ufo $(MAIN_GLYPHS_FILE)
	glyphs2ufo $(ITALIC_GLYPHS_FILE)

compile-otf-main: $(SOURCE_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ufo
	fontmake -a -u $(SOURCE_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ufo -o otf --output-dir $(OUTPUT_DIR)

compile-otf-italic: $(SOURCE_DIR)/$(FONT_NAME)-$(ITALIC).ufo
	fontmake -a -u $(SOURCE_DIR)/$(FONT_NAME)-$(ITALIC).ufo -o otf --output-dir $(OUTPUT_DIR)

compile-ttf-main: $(SOURCE_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ufo
	fontmake -a -u $(SOURCE_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ufo -o ttf --output-dir $(OUTPUT_DIR)

compile-ttf-italic: $(SOURCE_DIR)/$(FONT_NAME)-$(ITALIC).ufo
	fontmake -a -u $(SOURCE_DIR)/$(FONT_NAME)-$(ITALIC).ufo -o ttf --output-dir $(OUTPUT_DIR)

compile-woff2-main: $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ttf
	./woff2/woff2_compress $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ttf

compile-woff2-italic: $(OUTPUT_DIR)/$(FONT_NAME)-$(ITALIC).ttf
	./woff2/woff2_compress $(OUTPUT_DIR)/$(FONT_NAME)-$(ITALIC).ttf

compile-main: $(SOURCE_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ufo
	$(MAKE) compile-otf-main
	$(MAKE) compile-ttf-main && $(MAKE) compile-woff2-main

compile-italic: $(SOURCE_DIR)/$(FONT_NAME)-$(ITALIC).ufo
	$(MAKE) compile-otf-italic
	$(MAKE) compile-ttf-italic && $(MAKE) compile-woff2-italic

compile-all:
	$(MAKE) compile-main
	$(MAKE) compile-italic

.PHONY: clean
clean:
	if [ -e $(OUTPUT_DIR) ]; then rm -rf $(OUTPUT_DIR); fi
	if [ -e $(MAIN_UFO_DIR) ]; then rm -rf $(MAIN_UFO_DIR); fi
	if [ -e $(ITALIC_UFO_DIR) ]; then rm -rf $(ITALIC_UFO_DIR); fi
	if [ -e $(SOURCE_DIR)/$(FONT_NAME).designspace ]; then rm $(SOURCE_DIR)/$(FONT_NAME).designspace; fi
	if [ -e $(SOURCE_DIR)/$(FONT_NAME)-$(ITALIC).designspace ]; then rm $(SOURCE_DIR)/$(FONT_NAME)-$(ITALIC).designspace; fi

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