#!/bin/bash
# Local build script that mimics GitHub Pages deployment

echo "Building MkDocs site..."
uv run mkdocs build

echo "Copying apps/ directory..."
cp -r apps/rpac site/rpac

echo ""
echo "✓ Build complete!"
echo ""
echo "To serve locally, run:"
echo "  python -m http.server 8002 --directory site"
echo ""
echo "Then visit: http://localhost:8002/"
