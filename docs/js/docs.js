// Documentation Viewer
class DocsViewer {
  constructor() {
    this.currentPath = null;
    this.currentMarkdown = '';
    this.init();
  }

  async init() {
    // Load navigation
    await this.loadNavigation();

    // Get initial page from URL or show first doc
    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page') || './code/getting-started.md';
    await this.loadMarkdown(page);

    // Wire up copy button
    document.getElementById('copyMarkdown').addEventListener('click', () => {
      this.copyMarkdownSource();
    });

    // Handle browser back/forward
    window.addEventListener('popstate', (e) => {
      if (e.state && e.state.page) {
        this.loadMarkdown(e.state.page, false);
      }
    });
  }

  async loadNavigation() {
    try {
      const response = await fetch('nav.json');
      const navData = await response.json();

      const navContainer = document.getElementById('docs-nav');
      navContainer.innerHTML = '';

      navData.sections.forEach(section => {
        const sectionEl = document.createElement('div');
        sectionEl.className = 'docs-nav-section';

        const titleEl = document.createElement('h2');
        titleEl.textContent = section.title;
        sectionEl.appendChild(titleEl);

        const listEl = document.createElement('ul');
        section.items.forEach(item => {
          const liEl = document.createElement('li');
          const linkEl = document.createElement('a');
          linkEl.href = '#';
          linkEl.textContent = item.label;
          linkEl.dataset.path = item.path;
          linkEl.addEventListener('click', (e) => {
            e.preventDefault();
            this.loadMarkdown(item.path);
          });
          liEl.appendChild(linkEl);
          listEl.appendChild(liEl);
        });
        sectionEl.appendChild(listEl);

        navContainer.appendChild(sectionEl);
      });
    } catch (error) {
      console.error('Failed to load navigation:', error);
    }
  }

  async loadMarkdown(path, updateHistory = true) {
    try {
      console.log(`[DOCS] Loading: ${path}`);
      const response = await fetch(path);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      this.currentMarkdown = await response.text();
      this.currentPath = path;

      // Render markdown
      const html = marked.parse(this.currentMarkdown);
      document.getElementById('markdown-content').innerHTML = html;

      // Update URL
      if (updateHistory) {
        const url = new URL(window.location);
        url.searchParams.set('page', path);
        window.history.pushState({ page: path }, '', url);
      }

      // Update active nav link
      this.updateActiveNav(path);

      // Scroll to top
      document.querySelector('.docs-content').scrollTop = 0;

    } catch (error) {
      console.error('Failed to load markdown:', error);
      document.getElementById('markdown-content').innerHTML = `
        <div style="color: var(--sol-red); padding: 2rem;">
          <h2>Error Loading Document</h2>
          <p>Failed to load: <code>${path}</code></p>
          <p>${error.message}</p>
        </div>
      `;
    }
  }

  updateActiveNav(path) {
    document.querySelectorAll('.docs-nav-section a').forEach(link => {
      if (link.dataset.path === path) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }

  copyMarkdownSource() {
    if (!this.currentMarkdown) {
      alert('No markdown content to copy');
      return;
    }

    navigator.clipboard.writeText(this.currentMarkdown)
      .then(() => {
        // Visual feedback
        const btn = document.getElementById('copyMarkdown');
        const originalText = btn.textContent;
        btn.textContent = '✓ Copied!';
        btn.style.background = 'var(--sol-green)';

        setTimeout(() => {
          btn.textContent = originalText;
          btn.style.background = 'var(--sol-cyan)';
        }, 2000);
      })
      .catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy to clipboard');
      });
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new DocsViewer();
});
