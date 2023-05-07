CACHE_DIR := .cache
BUILD_DIR := build
RESOURCES_DIR := resources
GLYPHS_DIR := $(RESOURCES_DIR)/glyphs

ERROR_LOG_FILE := error.txt

MODIFY_HACK_SCRIPT := src/modify_hack.py
MODIFY_IBMPLEX_SCRIPT := src/modify_ibm_plex_sans_jp.py
MODIFY_HACK_NERD_SCRIPT := src/modify_hack_nerd.py
MAKE_ITALIC_SCRIPT := src/make_italic.py
MERGE_SCRIPT := src/merge.py

.PHONY: all
all:
	@docker-compose up

.PHONY: generate
generate: $(CACHE_DIR) $(BUILD_DIR) \
	$(BUILD_DIR)/PleckJP-Regular.ttf $(BUILD_DIR)/PleckJP-Bold.ttf $(BUILD_DIR)/PleckJP-Italic.ttf $(BUILD_DIR)/PleckJP-BoldItalic.ttf
	@echo "Completed."

# Do not renove intermediate files
.SECONDARY: $(wildcard *.ttf)

# Merge
$(BUILD_DIR)/PleckJP-%.ttf: $(CACHE_DIR)/modified-Hack-%.ttf $(CACHE_DIR)/modified-IBMPlexSansJP-%.ttf $(CACHE_DIR)/modified-HackNerdFont.ttf $(MERGE_SCRIPT)
	@python3 $(MERGE_SCRIPT) $(word 1, $^) $(word 2, $^) $(word 3, $^) $* $@ 2>> $(ERROR_LOG_FILE)

# Italic / BoldItalic
$(CACHE_DIR)/modified-Hack-Italic.ttf: $(CACHE_DIR)/modified-Hack-Regular.ttf $(MAKE_ITALIC_SCRIPT)
	@python3 $(MAKE_ITALIC_SCRIPT) $< $@ 2>> $(ERROR_LOG_FILE)

$(CACHE_DIR)/modified-Hack-BoldItalic.ttf: $(CACHE_DIR)/modified-Hack-Bold.ttf $(MAKE_ITALIC_SCRIPT)
	@python3 $(MAKE_ITALIC_SCRIPT) $< $@ 2>> $(ERROR_LOG_FILE)

$(CACHE_DIR)/modified-IBMPlexSansJP-Italic.ttf: $(CACHE_DIR)/modified-IBMPlexSansJP-Regular.ttf $(MAKE_ITALIC_SCRIPT)
	@python3 $(MAKE_ITALIC_SCRIPT) $< $@ 2>> $(ERROR_LOG_FILE)

$(CACHE_DIR)/modified-IBMPlexSansJP-BoldItalic.ttf: $(CACHE_DIR)/modified-IBMPlexSansJP-Bold.ttf $(MAKE_ITALIC_SCRIPT)
	@python3 $(MAKE_ITALIC_SCRIPT) $< $@ 2>> $(ERROR_LOG_FILE)

# Modify Regular/Bold and Nerd-Fonts
$(CACHE_DIR)/modified-HackNerdFont.ttf: $(GLYPHS_DIR)/HackNerdFont-Regular.ttf $(MODIFY_HACK_NERD_SCRIPT)
	@python3 $(MODIFY_HACK_NERD_SCRIPT) $< $@ 2>> $(ERROR_LOG_FILE)

$(CACHE_DIR)/modified-Hack-%.ttf: $(GLYPHS_DIR)/Hack-%.ttf $(MODIFY_HACK_SCRIPT)
	@python3 $(MODIFY_HACK_SCRIPT) $< $@ 2>> $(ERROR_LOG_FILE)

$(CACHE_DIR)/modified-IBMPlexSansJP-%.ttf: $(GLYPHS_DIR)/IBMPlexSansJP-%.ttf $(MODIFY_IBMPLEX_SCRIPT)
	@python3 $(MODIFY_IBMPLEX_SCRIPT) $< $@ 2>> $(ERROR_LOG_FILE)

# Setup directory
$(CACHE_DIR) $(BUILD_DIR):
	@mkdir -p $@

.PHONY: release
release:
	@echo "Current version is" $(shell python -c "import src.properties as p; print(p.VERSION, end='')")
	@read -p "Type new version: " new_version && \
		sed -i '' 's/^VERSION =.*/VERSION = "'$$new_version'"/' src/properties.py
	@make clean
	@make
	@cp LICENSE build/
	@version=$$(python -c "import src.properties as p; print(p.VERSION, end='')") && \
		cd build && \
		zip -r PleckJP_v$$version.zip * && \
		shasum -a 256 PleckJP_v$$version.zip | awk '{print $$1}' > PleckJP_v$$version.sha256
	@rm build/LICENSE

.PHONY: clean
clean:
	@rm -f $(ERROR_LOG_FILE)
	@rm -rf $(CACHE_DIR) $(BUILD_DIR)
