PY := python3.13
BUILD_DIR := build

.PHONY: clean fc-build fc-zip

clean:
	rm -rf $(BUILD_DIR) dist.zip

# Build a slim package for Function Compute (serverless)
fc-build: clean
	mkdir -p $(BUILD_DIR)
	# Install runtime deps into build dir (no cache metadata)
	pip install --no-cache-dir -r requirements.txt -t $(BUILD_DIR)
	# Copy sources and runners
	cp -R src $(BUILD_DIR)/
	cp serve.py $(BUILD_DIR)/
	cp mcp-sse.py $(BUILD_DIR)/
	# Prune unneeded files to shrink size
	$(PY) scripts/prune_package.py $(BUILD_DIR)

fc-zip: fc-build
	cd $(BUILD_DIR) && zip -r ../dist.zip . -9

