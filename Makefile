FONT_NAME = 0xProto
FAMILIES = Regular Italic Bold
SOURCE_DIR = sources
ROMAN_GLYPHS_FILE = $(SOURCE_DIR)/$(FONT_NAME).glyphspackage
ITALIC_GLYPHS_FILE = $(SOURCE_DIR)/$(FONT_NAME)-Italic.glyphspackage
OUTPUT_DIR = fonts
WOFF2_DIR = woff2
SCRIPTS_DIR = font-scripts/scripts

setup:
	pip install -r requirements.txt
	if [ ! -e $(WOFF2_DIR) ]; then $(MAKE) setup-woff2; fi
	if [ ! -e $(SCRIPTS_DIR) ]; then $(MAKE) setup-scripts; fi

setup-woff2:
	git clone --recursive https://github.com/google/woff2.git $(WOFF2_DIR)
	cd $(WOFF2_DIR) && make clean all

setup-scripts:
	git clone https://github.com/0xtype/font-scripts

.PHONY: build
build:
	$(MAKE) clean
	$(MAKE) compile-all
	python $(SCRIPTS_DIR)/remove_calt.py $(OUTPUT_DIR) -o $(OUTPUT_DIR)/No-Ligatures
	python $(SCRIPTS_DIR)/build_zx_fonts.py

compile-woff2-roman: $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ttf $(OUTPUT_DIR)/$(FONT_NAME)-$(BOLD_WEIGHT).ttf
	./woff2/woff2_compress $(OUTPUT_DIR)/$(FONT_NAME)-$(MAIN_WEIGHT).ttf
	./woff2/woff2_compress $(OUTPUT_DIR)/$(FONT_NAME)-$(BOLD_WEIGHT).ttf

compile-woff2-italic: $(OUTPUT_DIR)/$(FONT_NAME)-$(ITALIC).ttf
	./woff2/woff2_compress $(OUTPUT_DIR)/$(FONT_NAME)-$(ITALIC).ttf

compile-roman: $(ROMAN_GLYPHS_FILE)
	fontmake -a -g $(ROMAN_GLYPHS_FILE) -i --output-dir $(OUTPUT_DIR)

compile-italic: $(ITALIC_GLYPHS_FILE)
	fontmake -a -g $(ITALIC_GLYPHS_FILE) --output-dir $(OUTPUT_DIR)

compile-woff2: compile-roman compile-italic
	@for family in $(FAMILIES); do \
		./woff2/woff2_compress $(OUTPUT_DIR)/$(FONT_NAME)-$$family.ttf; \
	done

compile-all:
	$(MAKE) compile-woff2

.PHONY: clean
clean:
	if [ -e $(OUTPUT_DIR) ]; then rm -rf $(OUTPUT_DIR); fi

install-otf: $(OUTPUT_DIR)
	@for family in $(FAMILIES); do \
		cp $(OUTPUT_DIR)/$(FONT_NAME)-$$family.otf $(HOME)/Library/Fonts; \
	done

.PHONY: install
install:
	$(MAKE) build && $(MAKE) install-otf
