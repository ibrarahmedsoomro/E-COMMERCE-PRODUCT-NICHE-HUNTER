/**
 * HUNTER 3D // Interactive Spatial Radar & WebGL Hologram
 */

class Hologram3DScene {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.radarMesh = null;
    this.innerMesh = null;
    this.outerRing = null;
    this.middleRing = null;
    this.particles = null;
    this.group = null;
    this.currentColor = 0x10b981; // Default launch green
    this.targetColor = 0x10b981;
    this.dimensionScores = {
      profitability: 85,
      demand_traction: 70,
      competitive_gap: 65,
      differentiation_moat: 80,
      trend_momentum: 60,
      risk_profile: 90
    };
    
    this.mouseX = 0;
    this.mouseY = 0;
    this.targetRotationX = 0;
    this.targetRotationY = 0;

    if (this.container && window.THREE) {
      this.init();
      this.createHologramObjects();
      this.addEventListeners();
      this.animate();
    }
  }

  init() {
    try {
      if (!this.container) return;
      this.scene = new THREE.Scene();

      const width = this.container.clientWidth || 600;
      const height = this.container.clientHeight || 450;
      this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
      this.camera.position.set(0, 2.5, 6.5);

      this.renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
      this.renderer.setSize(width, height);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      this.container.innerHTML = '';
      this.container.appendChild(this.renderer.domElement);

      const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
      this.scene.add(ambientLight);

      const pointLight = new THREE.PointLight(0x06b6d4, 3, 20);
      pointLight.position.set(0, 4, 3);
      this.scene.add(pointLight);
    } catch (err) {
      console.warn("WebGL Scene initialization error:", err);
    }
  }

  createHologramObjects() {
    if (!this.scene) return;
    try {
      this.group = new THREE.Group();
      this.scene.add(this.group);

      const geom = new THREE.IcosahedronGeometry(1.6, 1);
      const material = new THREE.MeshPhongMaterial({
        color: this.currentColor,
        emissive: this.currentColor,
        emissiveIntensity: 0.35,
        wireframe: true,
        wireframeLinewidth: 2,
        transparent: true,
        opacity: 0.85
      });

      const innerMat = new THREE.MeshBasicMaterial({
        color: this.currentColor,
        transparent: true,
        opacity: 0.12,
        side: THREE.DoubleSide
      });

      this.radarMesh = new THREE.Mesh(geom, material);
      this.innerMesh = new THREE.Mesh(geom.clone(), innerMat);
      this.group.add(this.radarMesh);
      this.group.add(this.innerMesh);

      const ringGeom = new THREE.TorusGeometry(2.4, 0.02, 16, 100);
      const ringMat = new THREE.MeshBasicMaterial({
        color: 0x06b6d4,
        transparent: true,
        opacity: 0.4
      });
      this.outerRing = new THREE.Mesh(ringGeom, ringMat);
      this.outerRing.rotation.x = Math.PI / 3;
      this.group.add(this.outerRing);

      const midRingGeom = new THREE.TorusGeometry(2.0, 0.015, 16, 80);
      const midRingMat = new THREE.MeshBasicMaterial({
        color: 0x8b5cf6,
        transparent: true,
        opacity: 0.35
      });
      this.middleRing = new THREE.Mesh(midRingGeom, midRingMat);
      this.middleRing.rotation.y = Math.PI / 4;
      this.group.add(this.middleRing);

      const particleCount = 120;
      const particleGeom = new THREE.BufferGeometry();
      const particlePositions = new Float32Array(particleCount * 3);

      for (let i = 0; i < particleCount * 3; i += 3) {
        particlePositions[i] = (Math.random() - 0.5) * 6;
        particlePositions[i + 1] = (Math.random() - 0.5) * 5;
        particlePositions[i + 2] = (Math.random() - 0.5) * 6;
      }

      particleGeom.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
      const particleMat = new THREE.PointsMaterial({
        color: 0x06b6d4,
        size: 0.04,
        transparent: true,
        opacity: 0.6
      });
      this.particles = new THREE.Points(particleGeom, particleMat);
      this.group.add(this.particles);
    } catch (e) {
      console.warn("Error creating hologram meshes:", e);
    }
  }

  addEventListeners() {
    window.addEventListener('resize', () => {
      if (!this.container || !this.renderer || !this.camera) return;
      const w = this.container.clientWidth;
      const h = this.container.clientHeight;
      if (w > 0 && h > 0) {
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(w, h);
      }
    });

    if (this.container) {
      this.container.addEventListener('mousemove', (e) => {
        const rect = this.container.getBoundingClientRect();
        this.mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouseY = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        this.targetRotationY = this.mouseX * 0.8;
        this.targetRotationX = this.mouseY * 0.5;
      });
    }
  }

  updateColorByVerdict(verdict) {
    if (verdict === 'LAUNCH') {
      this.targetColor = 0x10b981;
    } else if (verdict === 'WATCHLIST') {
      this.targetColor = 0xf59e0b;
    } else {
      this.targetColor = 0xf43f5e;
    }
  }

  updateDimensions(dimensionScores) {
    if (!dimensionScores) return;
    this.dimensionScores = dimensionScores;
    const avgScore = (
      (dimensionScores.profitability || 70) +
      (dimensionScores.demand_traction || 70) +
      (dimensionScores.competitive_gap || 70) +
      (dimensionScores.differentiation_moat || 70) +
      (dimensionScores.trend_momentum || 70) +
      (dimensionScores.risk_profile || 70)
    ) / 600.0;

    const scale = 0.8 + avgScore * 0.8;
    if (this.radarMesh) {
      this.radarMesh.scale.set(scale, scale, scale);
    }
    if (this.innerMesh) {
      this.innerMesh.scale.set(scale * 0.95, scale * 0.95, scale * 0.95);
    }
  }

  animate() {
    requestAnimationFrame(() => this.animate());
    if (!this.renderer || !this.scene || !this.camera) return;

    const time = performance.now() * 0.001;

    if (this.radarMesh && this.innerMesh) {
      this.radarMesh.material.color.lerp(new THREE.Color(this.targetColor), 0.05);
      this.radarMesh.material.emissive.lerp(new THREE.Color(this.targetColor), 0.05);
      this.innerMesh.material.color.lerp(new THREE.Color(this.targetColor), 0.05);
    }

    if (this.group) {
      this.group.rotation.y += 0.004;
      this.group.rotation.x += (this.targetRotationX - this.group.rotation.x) * 0.05;
      this.group.rotation.y += (this.targetRotationY - (this.group.rotation.y % (Math.PI * 2))) * 0.01;
    }

    if (this.outerRing) {
      this.outerRing.rotation.z += 0.008;
      this.outerRing.rotation.x = Math.PI / 3 + Math.sin(time * 0.8) * 0.15;
    }

    if (this.middleRing) {
      this.middleRing.rotation.z -= 0.006;
      this.middleRing.rotation.y = Math.PI / 4 + Math.cos(time * 0.6) * 0.15;
    }

    if (this.particles) {
      this.particles.rotation.y -= 0.002;
    }

    if (this.radarMesh) {
      this.radarMesh.rotation.y += 0.005;
      this.radarMesh.rotation.x = Math.sin(time * 0.5) * 0.1;
    }

    this.renderer.render(this.scene, this.camera);
  }
}

// Safe global initialization
window.hologramScene = null;
document.addEventListener('DOMContentLoaded', () => {
  try {
    const el = document.getElementById('threejs-container');
    if (el) {
      window.hologramScene = new Hologram3DScene('threejs-container');
    }
  } catch (err) {
    console.warn("Hologram init deferred:", err);
  }
});
