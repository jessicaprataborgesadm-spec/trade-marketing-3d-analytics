import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# Lendo o CSV
df = pd.read_csv('dados_vendas.csv')
dados_json = df.to_json(orient='records')

st.set_page_config(layout="wide", page_title="Trade Marketing 3D Analytics", initial_sidebar_state="collapsed")
st.markdown("<style>.stApp { background-color: #080c14; margin: 0; padding: 0; } iframe { border-radius: 12px; border: 1px solid #1f2940 !important; }</style>", unsafe_allow_html=True)

dashboard_3d_code = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', system-ui, sans-serif; }
        body { background: #080c14; color: #fff; overflow: hidden; height: 100vh; display: flex; }
        #viewport { flex: 6; position: relative; height: 100vh; }
        #sidebar { flex: 4; background: #0f1623; border-left: 1px solid #1e293b; padding: 18px; display: flex; flex-direction: column; gap: 14px; overflow-y: auto; }
        .header { border-bottom: 1px solid #1e293b; padding-bottom: 10px; margin-bottom: 5px; }
        .header h1 { font-size: 16px; color: #00f2fe; text-transform: uppercase; }
        .control-group { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        label { font-size: 10px; color: #94a3b8; font-weight: 700; text-transform: uppercase; display: block; margin-bottom: 4px; }
        select { width: 100%; background: #172033; border: 1px solid #334155; color: #fff; padding: 6px; border-radius: 4px; font-size: 11px; }
        .module { background: #172033; border: 1px solid #1e293b; border-radius: 8px; padding: 12px; }
        .mod-title { font-size: 11px; font-weight: 700; color: #00f2fe; text-transform: uppercase; margin-bottom: 10px; display: flex; justify-content: space-between; }
        .kpi-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; text-align: center; }
        .kpi-box { background: #0f1623; border: 1px solid #1e293b; border-radius: 6px; padding: 8px; }
        .kpi-label { font-size: 9px; color: #64748b; font-weight: 700; text-transform: uppercase; }
        .kpi-val { font-size: 14px; font-weight: 800; color: #fff; margin: 4px 0; }
        .highlight { color: #10b981; }
        .bar-bg { background: #0f1623; height: 8px; border-radius: 4px; width: 100%; margin-top: 4px; overflow: hidden; }
        .bar-fill { height: 100%; border-radius: 4px; }
        .chart-container { height: 160px; width: 100%; }
        .overlay { position: absolute; top: 15px; left: 15px; background: rgba(15,22,35,0.8); padding: 8px 12px; border-radius: 6px; border: 1px solid #1e293b; font-size: 11px; color: #94a3b8; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div id="viewport"><div class="overlay">👆 Clique em um produto na prateleira</div></div>
    <div id="sidebar">
        <div class="header">
            <h1>Trade Marketing Analytics</h1>
            <div id="prod-nome" style="font-size: 12px; color: #fff; font-weight: 700; margin-top: 4px;">-</div>
        </div>
        <div class="control-group">
            <div>
                <label>Clima</label>
                <select id="clima-select" onchange="atualizarPainel()">
                    <option value="1.2">Verão (+20%)</option>
                    <option value="1.0" selected>Normal</option>
                    <option value="0.75">Chuvoso (-25%)</option>
                </select>
            </div>
            <div>
                <label>Promoção</label>
                <select id="promo-select" onchange="atualizarPainel()">
                    <option value="1.35">Leve 3 Pague 2</option>
                    <option value="1.15" selected>Desconto 10%</option>
                    <option value="1.0">Sem Promo</option>
                </select>
            </div>
        </div>
        <div class="module">
            <div class="mod-title"><span>A/B e Lucro Incremental</span> <span id="lucro-badge" class="highlight">R$ 0,00</span></div>
            <div class="kpi-grid">
                <div class="kpi-box">
                    <div class="kpi-label">Cenário A (Base)</div>
                    <div id="vendas-a" class="kpi-val">0 un</div>
                </div>
                <div class="kpi-box" style="border-color: #00f2fe;">
                    <div class="kpi-label" style="color:#00f2fe;">Cenário B (Simulação)</div>
                    <div id="vendas-b" class="kpi-val" style="color:#00f2fe;">0 un</div>
                </div>
            </div>
        </div>
        <div class="module">
            <div class="mod-title">Posicionamento e Fair Share</div>
            <div style="margin-bottom: 12px;">
                <div class="kpi-label">Nível da Gôndola</div>
                <div id="nivel-gondola" style="font-size: 13px; font-weight: bold; color: #fff;">-</div>
            </div>
            <div class="kpi-grid" style="text-align: left; grid-template-columns: 1fr;">
                <div>
                    <div class="kpi-label">Espaço Ocupado (<span id="txt-espaco">0</span>%)</div>
                    <div class="bar-bg"><div id="bar-espaco" class="bar-fill" style="background: #64748b; width: 0%;"></div></div>
                </div>
                <div>
                    <div class="kpi-label">Participação em Vendas (<span id="txt-share">0</span>%)</div>
                    <div class="bar-bg"><div id="bar-share" class="bar-fill" style="background: #00f2fe; width: 0%;"></div></div>
                </div>
            </div>
        </div>
        <div class="module">
            <div class="mod-title">
                <span>Previsão (7 dias) vs Real (30 dias)</span>
                <span id="cat-badge" style="color: #94a3b8; font-size: 9px;">-</span>
            </div>
            <div class="chart-container">
                <canvas id="linhaChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        const container = document.getElementById('viewport');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x080c14);

        const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
        camera.position.set(0, 1.8, 6.5);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

        scene.add(new THREE.AmbientLight(0xffffff, 0.7));
        const spotLight = new THREE.SpotLight(0x00f2fe, 1.5);
        spotLight.position.set(2, 8, 5);
        scene.add(spotLight);

        // DADOS RECEBIDOS DO CSV
        const db = INSERT_JSON_HERE;
        const interactiveObjects = [];

        const metalMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.8 });
        const post = new THREE.BoxGeometry(0.1, 4, 1.2);
        const p1 = new THREE.Mesh(post, metalMat); p1.position.set(-2.2, 0.3, 0); scene.add(p1);
        const p2 = new THREE.Mesh(post, metalMat); p2.position.set(2.2, 0.3, 0); scene.add(p2);

        db.forEach(item => {
            const shelf = new THREE.Mesh(new THREE.BoxGeometry(4.3, 0.08, 1.2), new THREE.MeshStandardMaterial({ color: 0x0f172a }));
            shelf.position.set(0, item.y, 0);
            scene.add(shelf);

            const corHex = parseInt(item.cor, 16);
            const prodMat = new THREE.MeshStandardMaterial({ color: corHex, roughness: 0.1 });
            
            for(let x = -1.5; x <= 1.5; x += 0.6) {
                const prod = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.65, 0.45), prodMat);
                prod.position.set(x, item.y + 0.38, 0);
                prod.userData = item;
                scene.add(prod);
                interactiveObjects.push(prod);
            }
        });

        let prodSel = db[1] || db[0]; 
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        window.addEventListener('pointerdown', (e) => {
            const rect = renderer.domElement.getBoundingClientRect();
            mouse.x = ((e.clientX - rect.left) / container.clientWidth) * 2 - 1;
            mouse.y = -((e.clientY - rect.top) / container.clientHeight) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(interactiveObjects);

            if (intersects.length > 0) {
                prodSel = intersects[0].object.userData;
                atualizarPainel();
            }
        });

        const ctx = document.getElementById('linhaChart').getContext('2d');
        const linhaChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['-30d', '-20d', '-10d', 'Hoje', '+2d', '+5d', '+7d'],
                datasets: [
                    { label: 'Real', data: [0,0,0,0, null, null, null], borderColor: '#64748b', tension: 0.4 },
                    { label: 'IA (Previsto)', data: [null, null, null, 0, 0, 0, 0], borderColor: '#00f2fe', borderDash: [5, 5], tension: 0.4 }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } }, y: { grid: { color: '#1e293b' } } } }
        });

        function atualizarPainel() {
            if(!prodSel) return;
            const fClima = parseFloat(document.getElementById('clima-select').value);
            const fPromo = parseFloat(document.getElementById('promo-select').value);

            const vBase = prodSel.base;
            const rBase = vBase * prodSel.preco;
            const lBase = rBase * prodSel.margem;

            const vSim = Math.round(vBase * fClima * fPromo);
            const rSim = vSim * prodSel.preco;
            const lSim = rSim * prodSel.margem;
            const lucroInc = lSim - lBase;

            document.getElementById('prod-nome').innerText = prodSel.nome;
            document.getElementById('vendas-a').innerText = `${vBase} un`;
            document.getElementById('vendas-b').innerText = `${vSim} un`;
            document.getElementById('lucro-badge').innerText = `${lucroInc >= 0 ? '+' : ''}${lucroInc.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}`;
            document.getElementById('lucro-badge').style.color = lucroInc >= 0 ? '#10b981' : '#ef4444';

            document.getElementById('nivel-gondola').innerText = prodSel.nivel;
            document.getElementById('cat-badge').innerText = `CAT: ${prodSel.cat.toUpperCase()}`;
            
            document.getElementById('txt-espaco').innerText = prodSel.espaco;
            document.getElementById('bar-espaco').style.width = `${prodSel.espaco}%`;
            
            document.getElementById('txt-share').innerText = prodSel.share;
            document.getElementById('bar-share').style.width = `${prodSel.share}%`;
            document.getElementById('bar-share').style.background = prodSel.share >= prodSel.espaco ? '#10b981' : '#ef4444';

            linhaChart.data.datasets[0].data = [vBase*0.9, vBase*1.1, vBase*0.95, vBase, null, null, null];
            linhaChart.data.datasets[1].data = [null, null, null, vBase, Math.round(vSim*0.8), Math.round(vSim*1.1), vSim];
            linhaChart.update();
        }

        function animate() { requestAnimationFrame(animate); controls.update(); renderer.render(scene, camera); }
        animate(); 
        setTimeout(atualizarPainel, 300);

        window.addEventListener('resize', () => {
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        });
    </script>
</body>
</html>
"""

# Injeta os dados do Pandas diretamente no HTML/JS
dashboard_3d_code = dashboard_3d_code.replace("INSERT_JSON_HERE", dados_json)
components.html(dashboard_3d_code, height=720)
