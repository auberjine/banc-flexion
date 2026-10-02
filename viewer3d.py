# -*- coding: utf-8 -*-
"""
Fabrique out/banc_3d.html : visionneuse autonome du modele, le maillage est
embarque dans la page. Un double-clic suffit, aucun serveur, aucune installation.

    python viewer3d.py
"""

import io
import os
import base64
import json

import params as p

HERE = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(HERE, "out", "stl")
OUT = os.path.join(HERE, "out", "banc_3d.html")

PIECES = [
    ("flanc", "Flancs en treillis", "#7d8794", 2),
    ("traverse", "Plaques de traverse", "#5b6470", p.TRAVERSE_N),
    ("coulisseau", "Coulisseau a tete inclinee", "#8b93a0", 1),
    ("guide", "Guides CHC M%.0f" % p.GUIDE_VIS_D, "#4a5160", 4),
    ("tourillon", "Tourillon", "#6b7280", 1),
    ("pile_belleville", "Pile Belleville", "#b06a3b", 1),
    ("vis", "Tige filetee de commande", "#4a5160", 1),
    ("coin", "Coin de commande", "#7d8794", 1),
    ("plaquette_haute", "Plaquette bronze, dessus", "#b8863b", 1),
    ("plaquette_basse", "Plaquette bronze, dessous", "#c9973f", 1),
    ("support", "Platines de butee", "#5b6470", 2),
    ("entretoise_vis", "Entretoises de butee", "#6b7280", 2),
    ("poussoir", "Plateaux de poussoir", "#8b93a0", p.POUSSOIR_N),
    ("patin_appui", "Patins d'appui", "#c2703f", 4),
    ("patin_charge", "Patin de charge", "#c2703f", 1),
    ("plat_renfort", "Plats de renfort", "#c2703f", 2),
    ("entretoise", "Entretoises (6 cadre + 2 chape + 1 sommet)", "#6b7280", 9),
    ("pied", "Pieds a mi-bois (2 couche + 2 debout)", "#7d8794", 4),
    ("crochet", "Crochets d etuve", "#5b6470", 4),
    ("poutre", "Poutrelle beton", "#a8a296", 1),
]

HTML = u"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<title>Banc de flexion - modele 3D</title>
<style>
 html,body{margin:0;height:100%;background:#1b1e24;color:#e6e8ec;
   font:14px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;overflow:hidden}
 #vue{position:absolute;inset:0}
 #panneau{position:absolute;top:14px;left:14px;background:#252932e8;padding:14px 16px;
   border-radius:10px;max-width:290px;backdrop-filter:blur(6px)}
 h1{font-size:15px;margin:0 0 2px;font-weight:600}
 .sous{color:#9aa3b0;font-size:12px;margin-bottom:10px}
 label{display:flex;align-items:center;gap:8px;font-size:12.5px;padding:2px 0;cursor:pointer}
 label:hover{color:#fff}
 .pastille{width:11px;height:11px;border-radius:3px;flex:none}
 #aide{position:absolute;bottom:12px;left:14px;color:#7f8794;font-size:11.5px}
 #charge{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
   color:#9aa3b0;font-size:13px}
 button{background:#343a46;color:#e6e8ec;border:0;border-radius:6px;padding:5px 10px;
   font-size:12px;cursor:pointer;margin-top:10px;margin-right:6px}
 button:hover{background:#414958}
</style></head><body>
<div id="vue"></div><div id="charge">chargement du modele...</div>
<div id="panneau">
 <h1>Banc de flexion 3 points</h1>
 <div class="sous">poutrelle 103 x 107 x 840, portee 750, capacite 12 kN<br>
 cadre __CADRE__, __MASSE__ kg</div>
 <div id="liste"></div>
 <button id="iso">vue 3/4</button><button id="face">elevation</button><button id="bout">bout</button>
 <button id="tout">tout</button><button id="rien">rien</button>
</div>
<div id="aide">glisser : tourner &nbsp;|&nbsp; molette : zoom &nbsp;|&nbsp; clic droit : deplacer</div>
<script>__THREE__</script>
<script>
const DATA = __DATA__;

function b64(s){const b=atob(s);const a=new Uint8Array(b.length);
  for(let i=0;i<b.length;i++)a[i]=b.charCodeAt(i);return a.buffer;}

function parseSTL(buf){
  const dv=new DataView(buf);const n=dv.getUint32(80,true);
  const pos=new Float32Array(n*9);const nor=new Float32Array(n*9);
  for(let i=0;i<n;i++){const o=84+i*50;
    const nx=dv.getFloat32(o,true),ny=dv.getFloat32(o+4,true),nz=dv.getFloat32(o+8,true);
    for(let j=0;j<3;j++){const q=o+12+j*12;
      pos[i*9+j*3]=dv.getFloat32(q,true);
      pos[i*9+j*3+1]=dv.getFloat32(q+4,true);
      pos[i*9+j*3+2]=dv.getFloat32(q+8,true);
    }
    // normale recalculee depuis les sommets : celle du fichier est parfois nulle
    const ax=pos[i*9],ay=pos[i*9+1],az=pos[i*9+2],bx=pos[i*9+3]-ax,by=pos[i*9+4]-ay,bz=pos[i*9+5]-az,
          cx=pos[i*9+6]-ax,cy=pos[i*9+7]-ay,cz=pos[i*9+8]-az;
    let fx=by*cz-bz*cy,fy=bz*cx-bx*cz,fz=bx*cy-by*cx;const l=Math.hypot(fx,fy,fz)||1;fx/=l;fy/=l;fz/=l;
    for(let j=0;j<3;j++){nor[i*9+j*3]=fx;nor[i*9+j*3+1]=fy;nor[i*9+j*3+2]=fz;}}
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.BufferAttribute(pos,3));
  g.setAttribute('normal',new THREE.BufferAttribute(nor,3));
  return g;}

const scene=new THREE.Scene();scene.background=new THREE.Color(0x1b1e24);
const cam=new THREE.PerspectiveCamera(35,innerWidth/innerHeight,5,8000);
const rend=new THREE.WebGLRenderer({antialias:true});
rend.setPixelRatio(devicePixelRatio);rend.setSize(innerWidth,innerHeight);
document.getElementById('vue').appendChild(rend.domElement);

scene.add(new THREE.HemisphereLight(0xdfe6f0,0x2a2f38,1.5));
const d1=new THREE.DirectionalLight(0xffffff,1.5);d1.position.set(600,900,700);scene.add(d1);
const d2=new THREE.DirectionalLight(0xffffff,0.6);d2.position.set(-700,-300,400);scene.add(d2);

const monde=new THREE.Group();scene.add(monde);
const root=new THREE.Group();monde.add(root);
const groupes={};
DATA.forEach(p=>{
  const g=parseSTL(b64(p.stl));
  const m=new THREE.MeshStandardMaterial({color:p.couleur,metalness:0.45,roughness:0.55,
    side:THREE.DoubleSide});
  const mesh=new THREE.Mesh(g,m);
  const grp=new THREE.Group();grp.add(mesh);
  root.add(grp);groupes[p.nom]=grp;
  const l=document.createElement('label');
  l.innerHTML='<input type="checkbox" checked data-n="'+p.nom+'">'+
    '<span class="pastille" style="background:'+p.couleur+'"></span>'+p.titre+
    ' <span style="color:#7f8794">x'+p.qte+'</span>';
  document.getElementById('liste').appendChild(l);
});
document.getElementById('liste').addEventListener('change',e=>{
  const n=e.target.dataset.n;
  if(!n||!groupes[n])return;
  groupes[n].visible=e.target.checked;
  maj();});                       // sans ce rendu la case se coche sans rien changer

root.updateMatrixWorld(true);
const box=new THREE.Box3().setFromObject(root);
const ctr=box.getCenter(new THREE.Vector3());
root.position.sub(ctr);
const rayon=box.getSize(new THREE.Vector3()).length()/2;
monde.rotation.x=-Math.PI/2;   // z du modele vers le haut de la scene

let theta=0.9,phi=1.12,dist=rayon*2.9;
const cible=new THREE.Vector3(0,0,0);
function maj(){
  cam.position.set(cible.x+dist*Math.sin(phi)*Math.cos(theta),
                   cible.y+dist*Math.cos(phi),
                   cible.z+dist*Math.sin(phi)*Math.sin(theta));
  cam.lookAt(cible);cam.updateMatrixWorld();rend.render(scene,cam);}
// le deplacement suit le plan de l'ECRAN : on lit les axes droite et haut dans
// la matrice de la camera, au lieu de pousser la cible selon x et y du monde.
const axeD=new THREE.Vector3(),axeH=new THREE.Vector3();
let drag=null;
rend.domElement.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY,b:e.button};});
addEventListener('pointerup',()=>drag=null);
addEventListener('pointermove',e=>{if(!drag)return;
  const dx=e.clientX-drag.x,dy=e.clientY-drag.y;drag.x=e.clientX;drag.y=e.clientY;
  if(drag.b===2){
    const k=2*dist*Math.tan(cam.fov*Math.PI/360)/innerHeight;   // mm par pixel
    axeD.setFromMatrixColumn(cam.matrixWorld,0);
    axeH.setFromMatrixColumn(cam.matrixWorld,1);
    cible.addScaledVector(axeD,-dx*k).addScaledVector(axeH,dy*k);
  }
  else{theta+=dx*0.008;phi=Math.max(0.05,Math.min(3.09,phi-dy*0.008));}
  maj();});
rend.domElement.addEventListener('contextmenu',e=>e.preventDefault());
addEventListener('wheel',e=>{dist=Math.max(rayon*0.4,Math.min(rayon*9,
  dist*(1+Math.sign(e.deltaY)*0.12)));maj();},{passive:true});
addEventListener('resize',()=>{cam.aspect=innerWidth/innerHeight;cam.updateProjectionMatrix();
  rend.setSize(innerWidth,innerHeight);maj();});
document.getElementById('iso').onclick=()=>{theta=0.9;phi=1.12;maj();};
document.getElementById('face').onclick=()=>{theta=-Math.PI/2;phi=Math.PI/2;maj();};
document.getElementById('bout').onclick=()=>{theta=0;phi=Math.PI/2;maj();};
function toutes(v){
  document.querySelectorAll('#liste input').forEach(i=>{
    i.checked=v;groupes[i.dataset.n].visible=v;});
  maj();}
document.getElementById('tout').onclick=()=>toutes(true);
document.getElementById('rien').onclick=()=>toutes(false);
document.getElementById('charge').remove();
maj();
</script></body></html>
"""


def main():
    data = []
    for nom, titre, couleur, qte in PIECES:
        f = os.path.join(STL, nom + "_montes.stl")
        if not os.path.isfile(f):
            print("  absent :", nom)
            continue
        raw = open(f, "rb").read()
        data.append(dict(nom=nom, titre=titre, couleur=couleur, qte=qte,
                         stl=base64.b64encode(raw).decode("ascii")))
    # une seule instance par piece ne suffit pas : on prend l'assemblage complet
    f = os.path.join(STL, "banc_assemblage.stl")
    masses = json.load(open(os.path.join(HERE, "out", "masses.json")))
    # three.js est EMBARQUE (vendor/three.min.js, r160 de cdnjs) : la page doit
    # s ouvrir sans reseau, sur n importe quel poste. Le </script> eventuel du
    # source est neutralise pour ne pas fermer la balise.
    three = io.open(os.path.join(HERE, "vendor", "three.min.js"), encoding="utf-8").read()
    three = three.replace("</script>", "<" + chr(92) + "/script>")
    html = HTML.replace("__THREE__", three).replace("__DATA__", json.dumps(data))
    html = html.replace("__MASSE__", ("%.1f" % masses["cadre_kg"]).replace(".", ","))
    html = html.replace("__CADRE__", "%.0f x %.0f x %.0f"
                        % (p.L_FLANC, p.H_FLANC, p.ECART_FLANCS + 2 * p.EP_FLANC))
    with open(OUT, "w") as fh:
        fh.write(html)
    print(OUT, "%.1f Mo" % (os.path.getsize(OUT) / 1e6))


if __name__ == "__main__":
    main()
