"use client";
// SPDX-License-Identifier: Apache-2.0
// Interactive view of the build chat's CAD model (design/cad/out/sensebook.glb). The behaviour
// (part labels, "pull apart" offsets, groups) follows the build chat's viewer, design/viewer/index.html.
// three.js and the 4 MB model load only when the visitor asks for them.

import { useCallback, useEffect, useId, useRef, useState } from "react";

type Status = "idle" | "loading" | "ready" | "error" | "no-webgl";

type Api = {
  explode: (t: number) => void;
  reset: () => void;
  dispose: () => void;
};

export function ModelStage({ src, poster, posterAlt }: { src: string; poster?: string; posterAlt: string }) {
  const stageRef = useRef<HTMLDivElement>(null);
  const apiRef = useRef<Api | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [explode, setExplode] = useState(0);
  const [picked, setPicked] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const sliderId = useId();

  const start = useCallback(async () => {
    if (!stageRef.current || apiRef.current) return;
    setStatus("loading");
    try {
      const api = await mountViewer(stageRef.current, src, {
        onProgress: setProgress,
        onPick: setPicked,
      });
      apiRef.current = api;
      setStatus("ready");
    } catch (e) {
      setStatus(e instanceof Error && e.message === "no-webgl" ? "no-webgl" : "error");
    }
  }, [src]);

  useEffect(() => () => apiRef.current?.dispose(), []);

  return (
    <div className="bg-stone-deep">
      <div
        ref={stageRef}
        className="relative aspect-[4/3] w-full touch-none overflow-hidden sm:aspect-[16/9]"
        role="img"
        aria-label="Interactive 3D model of the SenseBook prototype design. Drag to turn it; use the slider below to pull it apart."
      >
        {status !== "ready" && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-6 p-6 text-center">
            {poster && (
              // eslint-disable-next-line @next/next/no-img-element -- decorative poster behind the load button
              <img src={poster} alt={posterAlt} className="absolute inset-0 h-full w-full object-contain opacity-60" />
            )}
            <div className="relative flex flex-col items-center gap-3">
              {status === "idle" && (
                <button
                  type="button"
                  onClick={start}
                  className="inline-flex min-h-12 items-center rounded-full bg-ink px-6 text-[0.9375rem] font-medium text-stone transition-colors hover:bg-[#2c3739]"
                >
                  Open the 3D model
                </button>
              )}
              {status === "idle" && <p className="text-sm text-quiet">About 4 MB. Works with a mouse, a trackpad or touch.</p>}
              {status === "loading" && (
                <p className="rounded-full bg-stone px-5 py-3 text-sm text-ink" role="status">
                  Loading the model{progress > 0 ? `, ${Math.round(progress * 100)}%` : ""}
                </p>
              )}
              {status === "error" && (
                <p className="max-w-sm rounded bg-stone px-5 py-3 text-sm text-ink" role="alert">
                  The 3D model could not be loaded. The renders on this page show the same design.
                </p>
              )}
              {status === "no-webgl" && (
                <p className="max-w-sm rounded bg-stone px-5 py-3 text-sm text-ink" role="alert">
                  This browser cannot show 3D. The renders on this page show the same design.
                </p>
              )}
            </div>
          </div>
        )}
        {status === "ready" && picked && (
          <p className="pointer-events-none absolute bottom-4 left-4 rounded-full bg-stone px-4 py-2 text-sm font-medium text-ink shadow-sm" aria-live="polite">
            {picked}
          </p>
        )}
      </div>

      <div className="flex flex-col gap-5 border-t border-rule px-5 py-5 sm:flex-row sm:items-center sm:gap-8 sm:px-6">
        <div className="flex flex-1 items-center gap-4">
          <label htmlFor={sliderId} className="shrink-0 text-sm font-medium text-ink">
            Pull apart
          </label>
          <input
            id={sliderId}
            type="range"
            min={0}
            max={100}
            value={explode}
            disabled={status !== "ready"}
            aria-valuetext={explode === 0 ? "Assembled" : `${explode}% pulled apart`}
            onChange={(e) => {
              const v = Number(e.target.value);
              setExplode(v);
              apiRef.current?.explode(v / 100);
            }}
            className="h-11 w-full cursor-pointer accent-[#1a2224] disabled:cursor-not-allowed disabled:opacity-40"
          />
        </div>
        <button
          type="button"
          disabled={status !== "ready"}
          onClick={() => {
            setExplode(0);
            apiRef.current?.explode(0);
            apiRef.current?.reset();
            setPicked(null);
          }}
          className="min-h-11 self-start rounded-full px-5 text-sm font-medium text-ink ring-1 ring-[#b9bcb5] ring-inset transition-shadow hover:ring-ink disabled:opacity-40 sm:self-auto"
        >
          Reset view
        </button>
      </div>
    </div>
  );
}

/** Builds the three.js scene. Kept outside React so the render loop never re-renders components. */
async function mountViewer(
  host: HTMLDivElement,
  src: string,
  cb: { onProgress: (p: number) => void; onPick: (label: string | null) => void },
): Promise<Api> {
  const THREE = await import("three");
  const { OrbitControls } = await import("three/addons/controls/OrbitControls.js");
  const { GLTFLoader } = await import("three/addons/loaders/GLTFLoader.js");
  const { RoomEnvironment } = await import("three/addons/environments/RoomEnvironment.js");

  let renderer: InstanceType<typeof THREE.WebGLRenderer>;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  } catch {
    throw new Error("no-webgl");
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.3;
  renderer.domElement.style.display = "block";
  renderer.domElement.style.width = "100%";
  renderer.domElement.style.height = "100%";
  host.prepend(renderer.domElement);

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.add(new THREE.HemisphereLight(0xffffff, 0x9aa5a8, 1.1));

  const camera = new THREE.PerspectiveCamera(30, 1, 0.005, 10);
  const lamp = new THREE.DirectionalLight(0xffffff, 2.1);
  lamp.position.set(-0.3, 0.5, 1);
  camera.add(lamp);
  scene.add(camera);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.enablePan = false;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  controls.autoRotate = !reduce;
  controls.autoRotateSpeed = 0.6;
  controls.addEventListener("start", () => (controls.autoRotate = false));

  type Body = {
    node: InstanceType<typeof THREE.Object3D>;
    base: InstanceType<typeof THREE.Vector3>;
    off: InstanceType<typeof THREE.Vector3>;
    label: string;
    mats: InstanceType<typeof THREE.MeshStandardMaterial>[];
  };
  const bodies: Body[] = [];
  let home: { pos: InstanceType<typeof THREE.Vector3>; target: InstanceType<typeof THREE.Vector3> } | null = null;
  let selected: Body | null = null;
  let disposed = false;

  const draw = () => renderer.render(scene, camera);

  const fitDistance = () => {
    const box = new THREE.Box3();
    bodies.forEach((b) => box.expandByObject(b.node));
    const c = box.getCenter(new THREE.Vector3());
    const r = box.getSize(new THREE.Vector3()).length() / 2;
    const fov = THREE.MathUtils.degToRad(camera.fov / 2);
    const fit = Math.min(Math.sin(fov), Math.sin(Math.atan(Math.tan(fov) * camera.aspect)));
    return { c, d: (r / fit) * 1.02 };
  };

  const frame = () => {
    if (!bodies.length) return;
    const { c, d } = fitDistance();
    const dir = new THREE.Vector3(0.62, 0.42, -0.66).normalize(); // from the reader's left, a little above
    camera.position.copy(c).addScaledVector(dir, d);
    controls.target.copy(c);
    controls.update();
    home = { pos: camera.position.clone(), target: c.clone() };
  };

  const resize = () => {
    const w = host.clientWidth;
    const h = host.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / Math.max(h, 1);
    camera.updateProjectionMatrix();
    draw();
  };
  const ro = new ResizeObserver(resize);
  ro.observe(host);

  const gltf = await new GLTFLoader().loadAsync(src, (e) => {
    if (e.total) cb.onProgress(e.loaded / e.total);
  });
  if (disposed) return { explode() {}, reset() {}, dispose() {} };
  const root = gltf.scene;
  scene.add(root);
  root.updateMatrixWorld(true);
  root.children.slice().forEach((node) => {
    const u = (node.userData || {}) as { label?: string; explode?: number[] };
    if (!u.label) return;
    const e = u.explode || [0, 0, 0];
    const mats: Body["mats"] = [];
    node.traverse((o) => {
      const mesh = o as InstanceType<typeof THREE.Mesh>;
      if (!mesh.isMesh) return;
      const m = (mesh.material as InstanceType<typeof THREE.MeshStandardMaterial>).clone();
      m.userData.em0 = m.emissive ? m.emissive.getHex() : 0;
      mesh.material = m;
      mats.push(m);
    });
    const body: Body = { node, base: node.position.clone(), off: new THREE.Vector3(e[0], e[2], -e[1]), label: u.label, mats };
    node.traverse((o) => (o.userData.body = body));
    bodies.push(body);
  });
  resize();
  frame();

  const select = (b: Body | null) => {
    selected?.mats.forEach((m) => m.emissive?.setHex(m.userData.em0 ?? 0));
    selected = b;
    b?.mats.forEach((m) => m.emissive?.setHex(0x8a4b00));
    cb.onPick(b ? b.label : null);
    draw();
  };

  // A click (not a drag) names the part under the pointer.
  const ray = new THREE.Raycaster();
  let down: [number, number] | null = null;
  const onDown = (e: PointerEvent) => (down = [e.clientX, e.clientY]);
  const onUp = (e: PointerEvent) => {
    if (!down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 5) return;
    const r = renderer.domElement.getBoundingClientRect();
    ray.setFromCamera(new THREE.Vector2(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1), camera);
    const hit = ray.intersectObjects(scene.children, true).find((h) => h.object.visible && h.object.userData.body);
    select(hit ? (hit.object.userData.body as Body) : null);
  };
  renderer.domElement.addEventListener("pointerdown", onDown);
  renderer.domElement.addEventListener("pointerup", onUp);

  let raf = 0;
  const tick = () => {
    raf = requestAnimationFrame(tick);
    controls.update();
    draw();
  };
  tick();

  return {
    explode(t) {
      bodies.forEach((b) => b.node.position.copy(b.base).addScaledVector(b.off, t));
      if (home) {
        const { c, d } = fitDistance();
        const dir = camera.position.clone().sub(controls.target).normalize();
        camera.position.copy(c).addScaledVector(dir, d);
        controls.target.copy(c);
      }
    },
    reset() {
      if (!home) return;
      camera.position.copy(home.pos);
      controls.target.copy(home.target);
      controls.update();
    },
    dispose() {
      disposed = true;
      cancelAnimationFrame(raf);
      ro.disconnect();
      controls.dispose();
      renderer.domElement.removeEventListener("pointerdown", onDown);
      renderer.domElement.removeEventListener("pointerup", onUp);
      renderer.dispose();
      pmrem.dispose();
      renderer.domElement.remove();
    },
  };
}
