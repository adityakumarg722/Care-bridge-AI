(function () {
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---------- styles for the animations ----------
  var css =
    ".hero{position:relative;overflow:hidden;min-height:520px;display:flex;align-items:center}" +
    ".hero-content{position:relative;z-index:2;width:100%}" +
    ".hero-content>*{opacity:0;transform:translateY(22px);animation:cbUp .8s ease forwards}" +
    ".hero-content>*:nth-child(2){animation-delay:.12s}" +
    ".hero-content>*:nth-child(3){animation-delay:.24s}" +
    ".hero-content>*:nth-child(4){animation-delay:.36s}" +
    "@keyframes cbUp{to{opacity:1;transform:none}}" +
    ".cb-rv{opacity:0;transform:translateY(26px);transition:opacity .6s ease,transform .6s ease}" +
    ".cb-rv.cb-in{opacity:1;transform:none}" +
    ".stat-card,.hospital{transition:transform .3s,box-shadow .3s,opacity .6s}" +
    ".stat-card:hover,.hospital:hover{transform:translateY(-4px);box-shadow:0 12px 28px rgba(15,118,110,.18)}" +
    ".hero-button{transition:transform .2s,box-shadow .2s,background .2s}" +
    ".hero-button:hover{transform:translateY(-3px);box-shadow:0 10px 24px rgba(8,102,220,.35)}" +
    "@media (prefers-reduced-motion:reduce){.hero-content>*{animation:none;opacity:1;transform:none}" +
    ".cb-rv{opacity:1;transform:none;transition:none}}";
  var st = document.createElement("style");
  st.textContent = css;
  document.head.appendChild(st);

  // ---------- reveal cards on scroll ----------
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add("cb-in"); io.unobserve(e.target); }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll(".stat-card,.hospital,.search,.notice").forEach(function (el) {
    el.classList.add("cb-rv");
    io.observe(el);
  });

  // ---------- dashboard numbers count up ----------
  if (!reduce) {
    document.querySelectorAll(".stat-number").forEach(function (el) {
      var end = parseInt(el.textContent, 10);
      if (isNaN(end)) return;
      var o = new IntersectionObserver(function (es) {
        if (!es[0].isIntersecting) return;
        o.disconnect();
        var t0 = performance.now();
        (function tick(now) {
          var p = Math.min((now - t0) / 1000, 1);
          el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3)));
          if (p < 1) requestAnimationFrame(tick);
        })(t0);
      });
      o.observe(el);
    });
  }

  // ---------- 3D hero (Three.js) ----------
  var canvas = document.getElementById("hero3d");
  if (!canvas) return;
  var s = document.createElement("script");
  s.src = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js";
  s.onload = initHero;
  document.head.appendChild(s);

  function initHero() {
    var renderer;
    try {
      renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
    } catch (e) { return; }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100);
    camera.position.set(0, 0, 9);
    scene.add(new THREE.AmbientLight(0xffffff, 0.9));
    var key = new THREE.DirectionalLight(0xffffff, 1.1); key.position.set(4, 5, 6); scene.add(key);
    var glowA = new THREE.PointLight(0x38bdf8, 2.2, 14); scene.add(glowA);
    var glowB = new THREE.PointLight(0x14b8a6, 1.6, 14); scene.add(glowB);

    var TEAL = 0x0f766e, SKY = 0x38bdf8;
    var group = new THREE.Group(); scene.add(group);

    // hint text
    var hint = document.createElement("div");
    hint.textContent = "Tap to feel the heartbeat";
    hint.style.cssText = "position:absolute;right:5%;bottom:14px;z-index:2;font-size:12px;color:#0369a1;letter-spacing:.5px;pointer-events:none";
    canvas.parentElement.appendChild(hint);

    // 1) medical cross that beats like a heart
    var cross = new THREE.Group();
    var cm = new THREE.MeshStandardMaterial({ color: TEAL, emissive: 0x0a4f4a, roughness: 0.25, metalness: 0.2 });
    cross.add(new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.62, 0.62), cm));
    cross.add(new THREE.Mesh(new THREE.BoxGeometry(0.62, 1.9, 0.62), cm));
    cross.position.set(-0.4, 0, 0);
    group.add(cross);

    // heartbeat ripple rings
    var rings = [];
    for (var r = 0; r < 4; r++) {
      var rm = new THREE.Mesh(
        new THREE.TorusGeometry(1, 0.012, 8, 72),
        new THREE.MeshBasicMaterial({ color: SKY, transparent: true, opacity: 0 })
      );
      rm.visible = false; rm.userData.life = -1;
      rm.position.copy(cross.position);
      group.add(rm); rings.push(rm);
    }
    function ripple() {
      for (var i = 0; i < rings.length; i++) {
        if (rings[i].userData.life < 0) { rings[i].userData.life = 0; rings[i].visible = true; return; }
      }
    }

    // 2) DNA helix
    var helix = new THREE.Group();
    var sg = new THREE.SphereGeometry(0.11, 16, 16);
    var mA = new THREE.MeshStandardMaterial({ color: TEAL, roughness: 0.3 });
    var mB = new THREE.MeshStandardMaterial({ color: SKY, roughness: 0.3 });
    var rg = new THREE.CylinderGeometry(0.03, 0.03, 1.2, 8);
    var rmat = new THREE.MeshStandardMaterial({ color: 0xcbd5e1 });
    var steps = 26;
    for (var i = 0; i < steps; i++) {
      var a = (i / steps) * Math.PI * 2 * 2.2, y = (i / steps - 0.5) * 4.6;
      var s1 = new THREE.Mesh(sg, mA); s1.position.set(Math.cos(a) * 0.6, y, Math.sin(a) * 0.6);
      var s2 = new THREE.Mesh(sg, mB); s2.position.set(-Math.cos(a) * 0.6, y, -Math.sin(a) * 0.6);
      var rung = new THREE.Mesh(rg, rmat);
      rung.rotation.z = Math.PI / 2;
      var holder = new THREE.Group(); holder.position.y = y; holder.rotation.y = -a; holder.add(rung);
      helix.add(s1, s2, holder);
    }
    helix.position.set(2.4, 0, 0);
    group.add(helix);

    // 3) floating pills (capsule = cylinder + 2 spheres)
    function makePill(c1, c2) {
      var p = new THREE.Group();
      var cg = new THREE.CylinderGeometry(0.17, 0.17, 0.36, 20), pg = new THREE.SphereGeometry(0.17, 20, 20);
      var m1 = new THREE.MeshStandardMaterial({ color: c1, roughness: 0.25 });
      var m2 = new THREE.MeshStandardMaterial({ color: c2, roughness: 0.25 });
      var b = new THREE.Mesh(cg, m1); b.position.y = -0.18;
      var t = new THREE.Mesh(cg, m2); t.position.y = 0.18;
      var cb = new THREE.Mesh(pg, m1); cb.position.y = -0.36;
      var ct = new THREE.Mesh(pg, m2); ct.position.y = 0.36;
      p.add(b, t, cb, ct);
      return p;
    }
    var spots = [[-1.8, 1.9, 0.6], [-1.6, -1.9, 0.8], [0.9, 2.6, -0.4], [3.8, 2.4, 0.4], [3.6, -2.0, 0.6]];
    var pills = spots.map(function (sp, i) {
      var p = makePill(i % 2 ? SKY : TEAL, 0xffffff);
      p.position.set(sp[0], sp[1], sp[2]);
      p.userData = { base: sp, ph: i * 1.3 };
      group.add(p);
      return p;
    });

    // 4) ECG line across the bottom
    var N = 140, ecgPos = new Float32Array(N * 3), ecgGeo = new THREE.BufferGeometry();
    ecgGeo.setAttribute("position", new THREE.BufferAttribute(ecgPos, 3));
    var ecg = new THREE.Line(ecgGeo, new THREE.LineBasicMaterial({ color: TEAL, transparent: true, opacity: 0.55 }));
    ecg.frustumCulled = false;
    scene.add(ecg);
    function gs(u, c, w, a) { var z = (u - c) / w; return a * Math.exp(-z * z); }
    function ecgY(u) {
      return gs(u, 0.18, 0.03, 0.12) + gs(u, 0.37, 0.012, -0.15) + gs(u, 0.41, 0.012, 1.2) +
             gs(u, 0.45, 0.012, -0.35) + gs(u, 0.65, 0.05, 0.22);
    }

    // interaction
    var mx = 0, my = 0, sy = 0, visible = true, kick = 0;
    window.addEventListener("pointermove", function (e) {
      mx = (e.clientX / innerWidth - 0.5) * 2;
      my = (e.clientY / innerHeight - 0.5) * 2;
    });
    window.addEventListener("scroll", function () { sy = Math.min(window.scrollY / innerHeight, 1); });
    canvas.parentElement.addEventListener("pointerdown", function () { kick = 0.35; ripple(); });
    new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }).observe(canvas);

    function resize() {
      var w = canvas.clientWidth, h = canvas.clientHeight, wide = w > 800;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      group.position.set(wide ? 2.6 : 0.4, wide ? 0 : -1.8, 0);
      var k = wide ? 0.85 : 0.55;
      group.scale.set(k, k, k);
      camera.updateProjectionMatrix();
    }
    window.addEventListener("resize", resize);
    resize();

    var t = 0, beat = 0, PERIOD = 1.1, clock = new THREE.Clock();
    (function loop() {
      requestAnimationFrame(loop);
      var d = clock.getDelta();
      if (!visible) return;
      if (!reduce) { t += d; beat += d; }
      if (beat >= PERIOD) { beat -= PERIOD; ripple(); }

      // lub-dub heartbeat
      var amp = Math.exp(-beat * 10) * 0.16 + (beat > 0.28 ? Math.exp(-(beat - 0.28) * 12) * 0.1 : 0);
      kick *= 0.92;
      var sc = 1 + amp + kick;
      cross.scale.set(sc, sc, sc);
      cross.rotation.y = mx * 0.6 + Math.sin(t * 0.6) * 0.25;
      cross.rotation.x = my * 0.4;

      rings.forEach(function (rm) {
        var u = rm.userData;
        if (u.life < 0) return;
        u.life += d;
        var s = 1 + u.life * 2.2;
        rm.scale.set(s, s, s);
        rm.material.opacity = Math.max(0, 0.6 * (1 - u.life / 1.4));
        if (u.life > 1.4) { u.life = -1; rm.visible = false; }
      });

      helix.rotation.y = t * 0.7 + sy * 4 + mx * 0.8;
      pills.forEach(function (p) {
        var b = p.userData.base, ph = p.userData.ph;
        p.position.set(b[0] + Math.sin(t * 0.8 + ph) * 0.15, b[1] + Math.cos(t * 0.9 + ph) * 0.25, b[2]);
        p.rotation.z = t * 0.5 + ph; p.rotation.x = t * 0.3 + ph;
      });

      for (var i = 0; i < N; i++) {
        var x = -7 + 14 * i / (N - 1), u = (((x * 0.12 - t * 0.5) % 1) + 1) % 1;
        ecgPos[i * 3] = x; ecgPos[i * 3 + 1] = -2.5 + ecgY(u) * 0.9; ecgPos[i * 3 + 2] = 0;
      }
      ecgGeo.attributes.position.needsUpdate = true;

      glowA.position.set(mx * 4, -my * 3, 3);
      glowB.position.set(-mx * 3, my * 3, 3);
      camera.position.x += (mx * 0.6 - camera.position.x) * 0.05;
      camera.position.y += (-my * 0.4 - camera.position.y) * 0.05;
      camera.lookAt(0, 0, 0);
      renderer.render(scene, camera);
    })();
  }
})();