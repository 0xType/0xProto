FONT_NAME = 0xProto
MAIN_WEIGHT = Regular
BOLD_WEIGHT = Bold
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

compile-woff2-roman: $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ttf $(OUTPUT_DIR)/$(FONT_NAME)-$(BOLD_WEIGHT).ttf
	./woff2/woff2_compress $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ttf
	./woff2/woff2_compress $(OUTPUT_DIR)/$(FONT_NAME)-$(BOLD_WEIGHT).ttf

compile-woff2-italic: $(OUTPUT_DIR)/$(FONT_NAME)-$(ITALIC).ttf
	./woff2/woff2_compress $(OUTPUT_DIR)/$(FONT_NAME)-$(ITALIC).ttf

compile-roman: $(MAIN_GLYPHS_FILE)
	fontmake -a -g $(MAIN_GLYPHS_FILE) -i --output-dir $(OUTPUT_DIR) && $(MAKE) compile-woff2-roman

compile-italic: $(ITALIC_GLYPHS_FILE)
	fontmake -a -g $(ITALIC_GLYPHS_FILE) --output-dir $(OUTPUT_DIR) && $(MAKE) compile-woff2-italic

compile-all:
	$(MAKE) compile-roman
	$(MAKE) compile-italic

.PHONY: clean
clean:
	if [ -e $(OUTPUT_DIR) ]; then rm -rf $(OUTPUT_DIR); fi

install-otf-roman: $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).otf $(OUTPUT_DIR)/$(FONT_NAME)-$(BOLD_WEIGHT).otf
	cp $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).otf $(HOME)/Library/Fonts
	cp $(OUTPUT_DIR)/$(FONT_NAME)-$(BOLD_WEIGHT).otf $(HOME)/Library/Fonts

install-otf-italic: $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).otf
	cp $(OUTPUT_DIR)/$(FONT_NAME)-$(ITALIC).otf $(HOME)/Library/Fonts

.PHONY: install
install:
	$(MAKE) build
	$(MAKE) install-otf-roman
	$(MAKE) install-otf-italic

close-vscode:
	@osascript -e 'if application "Visual Studio Code" is running then' \
	           -e 'tell application "Visual Studio Code" to quit' \
	           -e 'end if'

debug:
	$(MAKE) close-vscode
	$(MAKE) build
	$(MAKE) install
	code .
