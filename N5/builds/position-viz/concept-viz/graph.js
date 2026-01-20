// Concept Graph Visualizer
// Heterogeneous graph with Thoughts (circles) and Concepts (diamonds)

let graphData = null;
let simulation = null;
let svg, g, link, node, label;
let selectedNode = null;

const width = window.innerWidth - 360;
const height = window.innerHeight - 120;

async function init() {
    // Load graph data
    const response = await fetch('./concept_graph.json');
    graphData = await response.json();
    
    // Update stats
    document.getElementById('stats').textContent = 
        `${graphData.stats.total_thoughts} thoughts • ${graphData.stats.total_concepts} concepts • ${graphData.stats.total_edges} connections`;
    
    // Populate domain filter
    const domains = [...new Set(graphData.nodes
        .filter(n => n.type === 'thought')
        .map(n => n.domain))];
    const select = document.getElementById('domain-filter');
    domains.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d;
        opt.textContent = d.replace(/-/g, ' ');
        select.appendChild(opt);
    });
    
    // Build domain legend
    const legendContainer = document.getElementById('domain-legend');
    domains.forEach(d => {
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.innerHTML = `
            <span class="legend-shape circle" style="background: ${graphData.domain_colors[d] || '#6b7280'};"></span>
            <span>${d.replace(/-/g, ' ')}</span>
        `;
        legendContainer.appendChild(item);
    });
    
    // Setup SVG
    svg = d3.select('#graph')
        .attr('width', width)
        .attr('height', height);
    
    // Add zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });
    
    svg.call(zoom);
    
    g = svg.append('g');
    
    // Create force simulation
    simulation = d3.forceSimulation(graphData.nodes)
        .force('link', d3.forceLink(graphData.edges)
            .id(d => d.id)
            .distance(d => {
                // Concepts closer to their thoughts
                return 80;
            }))
        .force('charge', d3.forceManyBody()
            .strength(d => d.type === 'concept' ? -400 : -100))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide()
            .radius(d => d.size + 5));
    
    // Draw links
    link = g.append('g')
        .attr('class', 'links')
        .selectAll('line')
        .data(graphData.edges)
        .join('line')
        .attr('class', 'link')
        .attr('stroke-width', d => d.strength * 2);
    
    // Draw nodes
    node = g.append('g')
        .attr('class', 'nodes')
        .selectAll('g')
        .data(graphData.nodes)
        .join('g')
        .attr('class', 'node')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended))
        .on('click', (event, d) => selectNode(d))
        .on('mouseover', (event, d) => highlightConnections(d))
        .on('mouseout', resetHighlight);
    
    // Add shapes based on type
    node.each(function(d) {
        const el = d3.select(this);
        if (d.type === 'concept') {
            // Diamond for concepts
            el.append('rect')
                .attr('width', d.size)
                .attr('height', d.size)
                .attr('x', -d.size / 2)
                .attr('y', -d.size / 2)
                .attr('transform', 'rotate(45)')
                .attr('fill', d.color)
                .attr('stroke', '#fff')
                .attr('stroke-width', 2);
        } else {
            // Circle for thoughts
            el.append('circle')
                .attr('r', d.size)
                .attr('fill', d.color)
                .attr('stroke', d.connected ? '#fff' : '#404040')
                .attr('stroke-width', 1);
        }
    });
    
    // Add labels for concepts
    label = g.append('g')
        .attr('class', 'labels')
        .selectAll('text')
        .data(graphData.nodes.filter(n => n.type === 'concept'))
        .join('text')
        .attr('class', 'node-label concept')
        .text(d => d.label)
        .attr('text-anchor', 'middle')
        .attr('dy', d => d.size + 16);
    
    // Update positions on tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node.attr('transform', d => `translate(${d.x},${d.y})`);
        
        label
            .attr('x', d => d.x)
            .attr('y', d => d.y + d.size + 16);
    });
    
    // Setup controls
    setupControls();
}

function setupControls() {
    document.getElementById('show-all').addEventListener('click', () => {
        setActiveButton('show-all');
        showAll();
    });
    
    document.getElementById('show-concepts').addEventListener('click', () => {
        setActiveButton('show-concepts');
        showConceptsOnly();
    });
    
    document.getElementById('domain-filter').addEventListener('change', (e) => {
        filterByDomain(e.target.value);
    });
}

function setActiveButton(id) {
    document.querySelectorAll('#controls button').forEach(b => b.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

function showAll() {
    node.style('display', 'block');
    link.style('display', 'block');
    label.style('display', 'block');
}

function showConceptsOnly() {
    node.style('display', d => d.type === 'concept' ? 'block' : 'none');
    link.style('display', 'none');
    label.style('display', 'block');
}

function filterByDomain(domain) {
    if (domain === 'all') {
        showAll();
        return;
    }
    
    const visibleThoughts = new Set(
        graphData.nodes
            .filter(n => n.type === 'thought' && n.domain === domain)
            .map(n => n.id)
    );
    
    // Find connected concepts
    const visibleConcepts = new Set();
    graphData.edges.forEach(e => {
        if (visibleThoughts.has(e.source.id || e.source)) {
            visibleConcepts.add(e.target.id || e.target);
        }
    });
    
    node.style('display', d => {
        if (d.type === 'thought') return visibleThoughts.has(d.id) ? 'block' : 'none';
        return visibleConcepts.has(d.id) ? 'block' : 'none';
    });
    
    link.style('display', d => {
        const sourceId = d.source.id || d.source;
        return visibleThoughts.has(sourceId) ? 'block' : 'none';
    });
    
    label.style('display', d => visibleConcepts.has(d.id) ? 'block' : 'none');
}

function highlightConnections(d) {
    const connectedIds = new Set([d.id]);
    
    graphData.edges.forEach(e => {
        const sourceId = e.source.id || e.source;
        const targetId = e.target.id || e.target;
        if (sourceId === d.id) connectedIds.add(targetId);
        if (targetId === d.id) connectedIds.add(sourceId);
    });
    
    node.classed('faded', n => !connectedIds.has(n.id));
    node.classed('highlighted', n => connectedIds.has(n.id));
    
    link.classed('faded', e => {
        const sourceId = e.source.id || e.source;
        const targetId = e.target.id || e.target;
        return sourceId !== d.id && targetId !== d.id;
    });
    link.classed('highlighted', e => {
        const sourceId = e.source.id || e.source;
        const targetId = e.target.id || e.target;
        return sourceId === d.id || targetId === d.id;
    });
}

function resetHighlight() {
    node.classed('faded', false).classed('highlighted', false);
    link.classed('faded', false).classed('highlighted', false);
}

function selectNode(d) {
    selectedNode = d;
    const panel = document.getElementById('detail-panel');
    
    // Get connections
    const connections = [];
    graphData.edges.forEach(e => {
        const sourceId = e.source.id || e.source;
        const targetId = e.target.id || e.target;
        
        if (sourceId === d.id) {
            const target = graphData.nodes.find(n => n.id === targetId);
            if (target) connections.push({ node: target, strength: e.strength, direction: 'to' });
        }
        if (targetId === d.id) {
            const source = graphData.nodes.find(n => n.id === sourceId);
            if (source) connections.push({ node: source, strength: e.strength, direction: 'from' });
        }
    });
    
    if (d.type === 'concept') {
        panel.innerHTML = `
            <span class="node-type concept">Concept</span>
            <h2>${d.label}</h2>
            <p class="description">${d.description}</p>
            <div class="connections">
                <h3>Connected Thoughts (${connections.length})</h3>
                <div class="connection-list">
                    ${connections.map(c => `
                        <div class="connection-item" onclick="focusNode('${c.node.id}')">
                            <div class="label">${c.node.label}</div>
                            <div class="meta">${c.node.domain} • strength: ${c.strength}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    } else {
        // Find concepts this thought connects to
        const concepts = connections.filter(c => c.node.type === 'concept');
        
        panel.innerHTML = `
            <span class="node-type thought">Thought</span>
            <h2>${d.full_title || d.label}</h2>
            <p class="description">${d.insight_preview || ''}</p>
            <div style="margin-top: 12px;">
                <span style="display: inline-block; padding: 4px 8px; background: ${d.color}33; color: ${d.color}; border-radius: 4px; font-size: 0.75rem;">
                    ${d.domain}
                </span>
            </div>
            <div class="connections">
                <h3>Concepts (${concepts.length})</h3>
                <div class="connection-list">
                    ${concepts.map(c => `
                        <div class="connection-item" onclick="focusNode('${c.node.id}')">
                            <div class="label">${c.node.label}</div>
                            <div class="meta">strength: ${c.strength}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
}

function focusNode(id) {
    const target = graphData.nodes.find(n => n.id === id);
    if (target) {
        selectNode(target);
        highlightConnections(target);
    }
}

function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

// Initialize on load
init();
