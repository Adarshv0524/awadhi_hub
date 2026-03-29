// @ts-check
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

import tailwindcss from '@tailwindcss/vite';

import svelte from '@astrojs/svelte';

// https://astro.build/config
export default defineConfig({
  site: 'https://awadhi.new',
  output: 'server',
  adapter: node({ mode: 'standalone' }),
  
  vite: {
    plugins: [tailwindcss()],
    build: {
      chunkSizeWarningLimit: 700,
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (id.includes('node_modules/echarts-gl')) return 'vendor-echarts-gl';
            if (id.includes('node_modules/echarts/lib/chart/')) return 'vendor-echarts-chart';
            if (id.includes('node_modules/echarts/lib/component/')) return 'vendor-echarts-component';
            if (id.includes('node_modules/echarts/lib/renderer/')) return 'vendor-echarts-renderer';
            if (id.includes('node_modules/echarts/lib/core/')) return 'vendor-echarts-core';
            if (id.includes('node_modules/echarts')) return 'vendor-echarts';
            if (id.includes('node_modules/svelte')) return 'vendor-svelte';
            if (id.includes('node_modules')) return 'vendor';
          },
        },
      },
    },
  },

  integrations: [svelte()]
});