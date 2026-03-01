---
name: content-graph
description: Build semantic content graphs that map relationships between pages, topics, and entities to power intelligent navigation, recommendations, and content strategy. Use when building "content graphs", "semantic networks", "content relationships", or "topic mapping".
---

# Content Graph

## Quick Reference
| Category | Trigger | Complexity | Source |
|----------|---------|------------|--------|
| data-intelligence | "content graph", "semantic network", "content relationships", "topic mapping" | High | 4 projects |

Build a structured graph of content nodes and relationship edges from a site's content index, then analyze the graph to surface strategic insights: orphan pages with no inbound links, hub pages that anchor topic clusters, content gaps where expected connections are missing, and natural topic groupings. The output is both a queryable data structure and an interactive visualization powered by D3.js force-directed layout.

## When to Use

- Mapping the full content architecture of a website to understand what exists and how it connects
- Identifying orphan pages that have no inbound links and are effectively invisible to users
- Finding hub pages that serve as high-centrality nodes anchoring entire topic areas
- Detecting natural topic clusters to inform information architecture or navigation redesign
- Running content gap analysis to find topics that are mentioned but have no dedicated page
- Building recommendation engines that suggest related content based on graph proximity
- Preparing for a site migration where you need to understand content dependencies before restructuring

## Instructions

### Step 1: Parse the Content Index

Start from a structured content index. This is typically a `query-index.json`, a sitemap, or a CMS export that lists every page with its metadata.

```javascript
// Expected input: array of page records from query-index.json or similar
const contentIndex = [
  {
    path: '/products/running-shoes',
    title: 'Running Shoes Collection',
    description: 'Explore our full range of running shoes...',
    tags: ['running', 'footwear', 'athletic'],
    category: 'products',
    author: 'content-team',
    lastModified: '2025-11-15',
    body: '...'  // Full page body text for link extraction
  }
  // ... hundreds or thousands of pages
];
```

If the content index does not include full body text, fetch it separately. You need the body to extract internal links (page-to-page edges). If only metadata is available, you can still build a topic-based graph, but page-to-page link edges will be missing.

Load and normalize the index:

```javascript
function loadContentIndex(indexPath) {
  const raw = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));

  // Normalize: ensure every record has required fields
  return raw.map(item => ({
    path: item.path.replace(/\/+$/, ''),  // Strip trailing slashes
    title: item.title || item.path.split('/').pop(),
    description: item.description || '',
    tags: Array.isArray(item.tags) ? item.tags : (item.tags || '').split(',').map(t => t.trim()).filter(Boolean),
    category: item.category || inferCategoryFromPath(item.path),
    author: item.author || 'unknown',
    lastModified: item.lastModified || null,
    body: item.body || ''
  }));
}

function inferCategoryFromPath(path) {
  const segments = path.split('/').filter(Boolean);
  return segments.length > 1 ? segments[0] : 'root';
}
```

### Step 2: Extract Entities (Graph Nodes)

Build four types of nodes from the content index. Each node type serves a different analytical purpose.

```javascript
function extractNodes(pages) {
  const nodes = [];
  const topicSet = new Set();
  const categorySet = new Set();
  const authorSet = new Set();

  // Page nodes — one per content page
  for (const page of pages) {
    nodes.push({
      id: `page:${page.path}`,
      type: 'page',
      title: page.title,
      path: page.path,
      metadata: {
        description: page.description,
        lastModified: page.lastModified,
        wordCount: page.body ? page.body.split(/\s+/).length : 0
      }
    });

    // Collect unique topics from tags
    for (const tag of page.tags) {
      topicSet.add(tag.toLowerCase());
    }
    categorySet.add(page.category);
    authorSet.add(page.author);
  }

  // Topic nodes — one per unique tag/topic
  for (const topic of topicSet) {
    nodes.push({
      id: `topic:${topic}`,
      type: 'topic',
      title: topic,
      path: null,
      metadata: {}
    });
  }

  // Category nodes — one per content category
  for (const cat of categorySet) {
    nodes.push({
      id: `category:${cat}`,
      type: 'category',
      title: cat,
      path: null,
      metadata: {}
    });
  }

  // Author nodes — one per content author
  for (const author of authorSet) {
    nodes.push({
      id: `author:${author}`,
      type: 'author',
      title: author,
      path: null,
      metadata: {}
    });
  }

  return nodes;
}
```

### Step 3: Build Edges (Graph Relationships)

Extract four types of edges. Each edge has a source, target, weight, and type.

```javascript
function extractEdges(pages, baseUrl) {
  const edges = [];

  for (const page of pages) {
    const pageId = `page:${page.path}`;

    // 1. page → topic edges (from tags)
    for (const tag of page.tags) {
      edges.push({
        source: pageId,
        target: `topic:${tag.toLowerCase()}`,
        weight: 1.0,
        type: 'tagged'
      });
    }

    // 2. page → category edges
    edges.push({
      source: pageId,
      target: `category:${page.category}`,
      weight: 1.0,
      type: 'categorized'
    });

    // 3. page → author edges
    edges.push({
      source: pageId,
      target: `author:${page.author}`,
      weight: 1.0,
      type: 'authored'
    });

    // 4. page → page edges (from internal links in body)
    if (page.body) {
      const internalLinks = extractInternalLinks(page.body, baseUrl);
      for (const targetPath of internalLinks) {
        edges.push({
          source: pageId,
          target: `page:${targetPath}`,
          weight: 1.0,
          type: 'links_to'
        });
      }
    }
  }

  // 5. topic → topic co-occurrence edges
  const topicCooccurrence = computeTopicCooccurrence(pages);
  for (const [pair, count] of Object.entries(topicCooccurrence)) {
    const [topicA, topicB] = pair.split('|');
    edges.push({
      source: `topic:${topicA}`,
      target: `topic:${topicB}`,
      weight: count,
      type: 'co_occurs'
    });
  }

  return edges;
}

function extractInternalLinks(body, baseUrl) {
  const linkRegex = /href=["'](\/[^"'#?]+|https?:\/\/[^"'#?]+)["']/g;
  const links = [];
  let match;

  while ((match = linkRegex.exec(body)) !== null) {
    let href = match[1];
    // Normalize to relative path
    if (href.startsWith(baseUrl)) {
      href = href.replace(baseUrl, '');
    }
    if (href.startsWith('/')) {
      links.push(href.replace(/\/+$/, ''));
    }
  }

  return [...new Set(links)];  // Deduplicate
}

function computeTopicCooccurrence(pages) {
  const cooccurrence = {};
  for (const page of pages) {
    const topics = page.tags.map(t => t.toLowerCase()).sort();
    for (let i = 0; i < topics.length; i++) {
      for (let j = i + 1; j < topics.length; j++) {
        const key = `${topics[i]}|${topics[j]}`;
        cooccurrence[key] = (cooccurrence[key] || 0) + 1;
      }
    }
  }
  return cooccurrence;
}
```

### Step 4: Compute Graph Metrics

Calculate centrality, clustering, and connectivity metrics to identify structural patterns.

```javascript
function computeGraphMetrics(nodes, edges) {
  // Build adjacency list
  const adjacency = {};
  for (const node of nodes) {
    adjacency[node.id] = { inbound: [], outbound: [] };
  }
  for (const edge of edges) {
    if (adjacency[edge.source]) adjacency[edge.source].outbound.push(edge.target);
    if (adjacency[edge.target]) adjacency[edge.target].inbound.push(edge.source);
  }

  // Degree centrality: (inbound + outbound) / (total_nodes - 1)
  const totalNodes = nodes.length;
  const centrality = {};
  for (const node of nodes) {
    const adj = adjacency[node.id];
    const degree = adj.inbound.length + adj.outbound.length;
    centrality[node.id] = {
      degree,
      inDegree: adj.inbound.length,
      outDegree: adj.outbound.length,
      normalizedCentrality: degree / (totalNodes - 1)
    };
  }

  // Graph-level metrics
  const totalEdges = edges.length;
  const maxPossibleEdges = totalNodes * (totalNodes - 1);
  const density = maxPossibleEdges > 0 ? totalEdges / maxPossibleEdges : 0;
  const degrees = Object.values(centrality).map(c => c.degree);
  const avgDegree = degrees.reduce((a, b) => a + b, 0) / degrees.length;

  return {
    totalNodes,
    totalEdges,
    density: Math.round(density * 10000) / 10000,
    avgDegree: Math.round(avgDegree * 100) / 100,
    centrality
  };
}
```

### Step 5: Detect Clusters

Group related nodes into topic clusters using co-occurrence strength and shared connections.

```javascript
function detectClusters(nodes, edges, metrics) {
  // Simple connected-component clustering on topic co-occurrence
  const topicNodes = nodes.filter(n => n.type === 'topic');
  const topicEdges = edges.filter(e => e.type === 'co_occurs' && e.weight >= 2);

  const visited = new Set();
  const clusters = [];

  function bfs(startId) {
    const queue = [startId];
    const cluster = [];
    visited.add(startId);

    while (queue.length > 0) {
      const current = queue.shift();
      cluster.push(current);

      const neighbors = topicEdges
        .filter(e => e.source === current || e.target === current)
        .map(e => e.source === current ? e.target : e.source)
        .filter(n => !visited.has(n));

      for (const neighbor of neighbors) {
        visited.add(neighbor);
        queue.push(neighbor);
      }
    }
    return cluster;
  }

  for (const node of topicNodes) {
    if (!visited.has(node.id)) {
      const clusterNodes = bfs(node.id);
      if (clusterNodes.length >= 2) {
        clusters.push({
          id: `cluster-${clusters.length + 1}`,
          label: clusterNodes[0].replace('topic:', ''),
          nodes: clusterNodes
        });
      }
    }
  }

  return clusters;
}
```

### Step 6: Identify Strategic Insights

Run the following analyses against the completed graph. These are the actionable outputs that drive content strategy decisions.

**Orphan Pages** (pages with zero or one inbound links):

```javascript
function findOrphanPages(nodes, metrics) {
  return nodes
    .filter(n => n.type === 'page')
    .filter(n => metrics.centrality[n.id].inDegree <= 1)
    .sort((a, b) => metrics.centrality[a.id].inDegree - metrics.centrality[b.id].inDegree);
}
```

Orphan pages are effectively invisible. They receive no link equity and users cannot navigate to them except via direct URL or search. Recommend adding internal links from related hub pages.

**Hub Pages** (pages with highest centrality scores):

```javascript
function findHubPages(nodes, metrics, topN = 10) {
  return nodes
    .filter(n => n.type === 'page')
    .sort((a, b) => metrics.centrality[b.id].degree - metrics.centrality[a.id].degree)
    .slice(0, topN);
}
```

Hub pages anchor topic clusters. They should be high-quality, regularly updated, and serve as entry points for their topic area. If a hub page is thin or outdated, the entire cluster suffers.

**Content Gaps** (topics mentioned in tags but with fewer than 2 dedicated pages):

```javascript
function findContentGaps(nodes, edges) {
  const topicPageCounts = {};
  for (const edge of edges.filter(e => e.type === 'tagged')) {
    topicPageCounts[edge.target] = (topicPageCounts[edge.target] || 0) + 1;
  }

  return Object.entries(topicPageCounts)
    .filter(([_, count]) => count < 2)
    .map(([topicId, count]) => ({
      topic: topicId.replace('topic:', ''),
      pageCount: count,
      recommendation: 'Create additional content pages for this topic'
    }));
}
```

### Step 7: Assemble the Graph Data Structure

Combine all components into the final output format.

```javascript
const graph = {
  nodes: extractNodes(pages),
  edges: extractEdges(pages, baseUrl),
  clusters: [],  // Populated after detection
  metrics: {},   // Populated after computation
  insights: {
    orphanPages: [],
    hubPages: [],
    contentGaps: [],
    isolatedTopics: []
  },
  generatedAt: new Date().toISOString()
};

graph.metrics = computeGraphMetrics(graph.nodes, graph.edges);
graph.clusters = detectClusters(graph.nodes, graph.edges, graph.metrics);
graph.insights.orphanPages = findOrphanPages(graph.nodes, graph.metrics);
graph.insights.hubPages = findHubPages(graph.nodes, graph.metrics);
graph.insights.contentGaps = findContentGaps(graph.nodes, graph.edges);
```

Write the graph to `content-graph.json` for downstream consumption by visualization and reporting tools.

### Step 8: Generate the Interactive Visualization

Build a single-page HTML file with an embedded D3.js force-directed graph.

Key visualization features:
- **Node sizing**: Proportional to centrality score. Hub pages appear larger.
- **Node coloring**: By type (page=blue, topic=green, category=orange, author=purple) or by cluster membership.
- **Edge rendering**: Thicker edges for higher weights. Dashed edges for weak connections (weight < 2).
- **Tooltips**: On hover, show node title, type, centrality score, and connected nodes count.
- **Cluster highlighting**: Click a cluster label to highlight all nodes in that cluster and dim others.
- **Search**: Text input to find and zoom to a specific node by title or path.
- **Layout controls**: Adjust force strength, link distance, and charge to tune the layout for different graph sizes.

Force simulation parameters tuned for content graphs:

```javascript
const simulation = d3.forceSimulation(nodes)
  .force('link', d3.forceLink(edges).id(d => d.id).distance(80))
  .force('charge', d3.forceManyBody().strength(-200))
  .force('center', d3.forceCenter(width / 2, height / 2))
  .force('collision', d3.forceCollide().radius(d => nodeRadius(d) + 5));
```

For graphs with more than 500 nodes, enable progressive rendering: show only the top-100 highest-centrality nodes initially, with a "Show all" toggle.

### Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Graph is a single dense blob | Too many weak edges included | Filter edges by minimum weight threshold (start at 2) |
| No clusters detected | Co-occurrence threshold too high | Lower the minimum co-occurrence from 2 to 1 |
| Orphan page count is misleadingly low | Only counting link edges, not tag edges | Count only `links_to` type edges for orphan detection |
| Visualization is slow or freezes | Too many nodes for D3 force simulation | Enable progressive rendering or switch to WebGL (sigma.js) for 1000+ nodes |
| Topic nodes dominate the graph | Tags are too granular | Normalize tags before graph construction (lowercase, merge synonyms) |
| Disconnected subgraphs | Content sections that never cross-reference | This is itself an insight — flag disconnected components as content silos |

### Cross-References

- **site-auditor** — Produces the content index (query-index.json) that feeds graph construction
- **report-hub-generator** — Renders graph insights as interactive HTML report sections
- **data-intelligence-pipeline** — Applies similar graph analysis to Slack thread data for knowledge mapping
