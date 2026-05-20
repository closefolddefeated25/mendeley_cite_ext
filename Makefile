# ------------------------------------------------------------
# Makefile for the Mendeley‑Citation extension (snap‑friendly)
# ------------------------------------------------------------

# ---------------------  CONFIGURATION  ------------------------
# Path where the snap version of LibreOffice expects user extensions
# (same path that the deb version uses)
LO_USER_EXT   := $(HOME)/.config/libreoffice/4/user/extensions/

# Name of the generated .oxt – the version is taken from description.json
OXT_NAME      := mendeley_cite_ext$(shell grep '^"version":' description.json \
                                         | sed -E 's/.*"version"\s*:\s*"([^"]+)".*/\1/')'.oxt'

# Command that creates a zip archive (Ubuntu always has `zip`)
ZIP           := zip

# LibreOffice binary supplied by the snap
LO            := libreoffice

# ------------------------------------------------------------
# Targets
# ------------------------------------------------------------
all: oxt                       # default = build the .oxt

# ---- Build the .oxt -------------------------------------------------
# It depends on `clean` so we always start with a pristine archive.
$(OXT_NAME): clean
	@echo "🔧  Creating $@ ..."
	$(ZIP) -r -x "*.git*" "__pycache__" "*.pyc" "$@" ./
	@echo "✅  $@ created"

# ---- Install the extension into the snap's user‑extension directory ----
install: $(OXT_NAME)
	@echo "🚚  Installing $< into $(LO_USER_EXT)"
	@mkdir -p $(LO_USER_EXT)
	@cp -f $(OXT_NAME) $(LO_USER_EXT)
	@echo "✅  Extension installed.  Open Writer to see it."

# ---- Remove the extension (uninstall) -------------------------------
uninstall:
	@echo "🗑️  Removing $(OXT_NAME) from $(LO_USER_EXT)"
	@rm -f $(LO_USER_EXT)$(OXT_NAME)
	@echo "✅  Extension removed."

# ---- Clean up generated artefacts ---------------------------------------
clean:
	@echo "🧹  Cleaning ..."
	@rm -f $(OXT_NAME)
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅  Clean complete."

# ---- Debug launch – open Writer with the extension loaded -------------
debug: $(OXT_NAME)
	@echo "🚀  Launching LibreOffice Writer with $(OXT_NAME) ..."
	$(LO) --writer --nologo --nofirstrun --extensions $(OXT_NAME)

# ---- List extensions currently registered in the running process -------
list-extensions:
	@echo "📋  Extensions registered in the current LibreOffice process:"
	@unopkg list | grep -i mendeley_cite || true
	@echo "📋  All extensions:"
	@unopkg list

# ------------------------------------------------------------
# Prevent make from trying to rebuild a file named "all"
# ------------------------------------------------------------
.PHONY: all oxt install uninstall clean debug list-extensions
