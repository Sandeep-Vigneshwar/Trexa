import React, { useEffect, useRef, useState } from 'react';
import ForceGraph3D from '3d-force-graph';
import * as THREE from 'three';

export interface GraphNode {
  id: string;
  label?: string;
  name?: string;
  group?: string | number;
  color?: string;
}

export interface GraphLink {
  source: string;
  target: string;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface Graph3DProps {
  directory: string;
}

const Graph3D: React.FC<Graph3DProps> = ({ directory }) => {
  const graphRef = useRef<HTMLDivElement>(null);
  const fgRef = useRef<any>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!directory) return;
    setLoading(true);
    fetch('http://localhost:8080/graph', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: directory })
    })
      .then(res => res.json())
      .then((data) => {
        if (data.status === 'success' && data.graph) {
          setGraphData(data.graph);
        } else {
          setGraphData({ nodes: [], links: [] });
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [directory]);

  useEffect(() => {
    if (!graphRef.current || !graphData) return;
    if (fgRef.current) {
      fgRef.current._destructor();
      fgRef.current = null;
    }
    const fg = new (ForceGraph3D as any)()(graphRef.current)
      .graphData(graphData)
      .nodeAutoColorBy('group')
      .nodeLabel('')
      .linkDirectionalParticles(1)
      .linkDirectionalParticleWidth(1)
      .linkOpacity(0.5)
      .linkWidth(1)
      .enableNodeDrag(true)
      .onNodeClick((node: GraphNode) => alert(node.id))
      .nodeThreeObject((node: GraphNode) => {
        
        // Sphere for the node
        const sphereGeometry = new (THREE as any).SphereGeometry(1, 16, 16);
        const sphereMaterial = new (THREE as any).MeshBasicMaterial({ color: node.color || '#2196f3' });
        const sphere = new (THREE as any).Mesh(sphereGeometry, sphereMaterial);

        // Label sprite
        const label = node.label || node.name || node.id;
        const fontSize = 40;
        const padding = 20;
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        if (context) {
          context.font = `${fontSize}px Arial`;
        }
        
        const textWidth = context ? context.measureText(label).width : 0;
        canvas.width = Math.max(300, textWidth + padding * 2);
        canvas.height = fontSize + padding;
        if (context) {
          context.font = `${fontSize}px Arial`;
          context.fillStyle = '#222';
          context.textAlign = 'left';
          context.textBaseline = 'middle';
          context.clearRect(0, 0, canvas.width, canvas.height);
          context.fillText(label, padding, canvas.height / 2);
        }
        const texture = new (THREE as any).Texture(canvas);
        texture.needsUpdate = true;
        const spriteMaterial = new (THREE as any).SpriteMaterial({ map: texture, transparent: true });
        const sprite = new (THREE as any).Sprite(spriteMaterial);
        sprite.scale.set(canvas.width / 12, canvas.height / 12, 1);
        sprite.position.x = 12;

        const group = new (THREE as any).Group();
        group.add(sphere);
        group.add(sprite);
        return group;
      });

    fg.controls().enableDamping = true;
    fg.controls().dampingFactor = 0.15;
    fg.controls().screenSpacePanning = false;
    fg.controls().minDistance = 10;
    fg.controls().maxDistance = 1000;
    fg.controls().enablePan = true;
    fg.controls().enableZoom = true;
    fg.controls().enableRotate = true;

    fgRef.current = fg;
    return () => {
      fg._destructor();
      fgRef.current = null;
    };
  }, [graphData]);

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      {loading && (
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', fontSize: 18 }}>
          Loading graph...
        </div>
      )}
      <div ref={graphRef} style={{ width: '100vw', height: '100vh', visibility: loading ? 'hidden' : 'visible' }} />
    </div>
  );
};

export default Graph3D;
