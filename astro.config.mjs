import { defineConfig } from 'astro/config';
import rehypeArchival from './src/lib/rehype-archival.mjs';

export default defineConfig({
  site: 'https://deseret.wiki',
  markdown: { rehypePlugins: [rehypeArchival] },
});
