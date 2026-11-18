async function start(){
const status=document.getElementById('status');
status.textContent='Loading the 3D assembly…';
const response=await fetch(new URL('./assets/assembly-1p7-5c78b9f5a251.glb.gz',import.meta.url));
if(!response.ok)throw new Error('The model could not be downloaded ('+response.status+').');
let bytes=new Uint8Array(await response.arrayBuffer());
if(bytes[0]===0x1f && bytes[1]===0x8b){
 if(typeof DecompressionStream==='undefined')throw new Error('Please use a current browser to open this compressed model.');
 bytes=new Uint8Array(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer());
}
const dv=new DataView(bytes.buffer),jsonLength=dv.getUint32(12,true),doc=JSON.parse(new TextDecoder().decode(bytes.slice(20,20+jsonLength))),binStart=20+jsonLength+8;
const link=document.getElementById('download');link.href=URL.createObjectURL(new Blob([bytes],{type:'model/gltf-binary'}));link.download='NFC_1p7mm_components.glb';
const canvas=document.getElementById('view'),gl=canvas.getContext('webgl',{antialias:true,alpha:false});
if(!gl)throw new Error('3D graphics are unavailable in this browser. Try enabling hardware acceleration or use another browser.');
function shader(type,src){const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s}
const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,'attribute vec3 pos;attribute vec3 normal;uniform mat4 vp;uniform vec3 offset;varying vec3 n;void main(){n=normal;gl_Position=vp*vec4(pos+offset,1.0);}'));
gl.attachShader(program,shader(gl.FRAGMENT_SHADER,'precision mediump float;varying vec3 n;uniform vec4 color;void main(){float light=0.52+0.48*abs(dot(normalize(n),normalize(vec3(0.3,0.8,0.5))));gl_FragColor=vec4(color.rgb*light,color.a);}'));gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(program));gl.useProgram(program);
const loc={pos:gl.getAttribLocation(program,'pos'),normal:gl.getAttribLocation(program,'normal'),vp:gl.getUniformLocation(program,'vp'),offset:gl.getUniformLocation(program,'offset'),color:gl.getUniformLocation(program,'color')};
function array(index){const a=doc.accessors[index],v=doc.bufferViews[a.bufferView];return new Float32Array(bytes.buffer,binStart+(v.byteOffset||0)+(a.byteOffset||0),a.count*3)}
function upload(data){const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,data,gl.STATIC_DRAW);return b}
const meshes=doc.nodes.map(node=>{const p=doc.meshes[node.mesh].primitives[0];return{node,pos:upload(array(p.attributes.POSITION)),normal:upload(array(p.attributes.NORMAL)),count:doc.accessors[p.attributes.POSITION].count,color:doc.materials[p.material].pbrMetallicRoughness.baseColorFactor}});
const groupNames={frame:'Housing and frame',insert:'Spiral inserts',wire:'Magnet wire and leads',carriers:'Board carriers',pn5180:'PN5180 module',xiao:'XIAO STM32C5',tuning:'Tuning layout concept',cable:'USB plug and cable',covers:'Covers, transparent'};
const visible={};for(const [key,name]of Object.entries(groupNames)){visible[key]=key!=='covers';const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.checked=visible[key];input.onchange=()=>{visible[key]=input.checked;draw()};label.append(input,' '+name);document.getElementById('groups').append(label)}
document.getElementById('status').textContent=meshes.length+' named component meshes. Model units: metres.';
let target=[0,.025,.015],distance=.76,yaw=.60,pitch=.63,explode=0;
const norm=a=>{const l=Math.hypot(...a);return a.map(v=>v/l)},cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]],dot=(a,b)=>a.reduce((v,x,i)=>v+x*b[i],0);
function lookAt(eye,to){const z=norm(eye.map((v,i)=>v-to[i])),x=norm(cross([0,1,0],z)),y=cross(z,x);return[x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,-dot(x,eye),-dot(y,eye),-dot(z,eye),1]}
function perspective(aspect){const f=1/Math.tan(Math.PI/8),near=.001,far=20;return[f/aspect,0,0,0,0,f,0,0,0,0,(far+near)/(near-far),-1,0,0,2*far*near/(near-far),0]}
function mul(a,b){const o=new Float32Array(16);for(let c=0;c<4;c++)for(let r=0;r<4;r++)for(let k=0;k<4;k++)o[c*4+r]+=a[k*4+r]*b[c*4+k];return o}
let renderedFrames=0;
function draw(){const dpr=Math.min(devicePixelRatio||1,2);canvas.width=Math.round(canvas.clientWidth*dpr);canvas.height=Math.round(canvas.clientHeight*dpr);gl.viewport(0,0,canvas.width,canvas.height);gl.clearColor(.934,.953,.965,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.enable(gl.DEPTH_TEST);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);
const eye=[target[0]+distance*Math.cos(pitch)*Math.sin(yaw),target[1]+distance*Math.sin(pitch),target[2]+distance*Math.cos(pitch)*Math.cos(yaw)];gl.uniformMatrix4fv(loc.vp,false,mul(perspective(canvas.width/canvas.height),lookAt(eye,target)));
for(const transparent of [false,true])for(const m of meshes){const g=m.node.extras.group;if(!visible[g]||(m.color[3]<1)!==transparent)continue;gl.depthMask(!transparent);gl.bindBuffer(gl.ARRAY_BUFFER,m.pos);gl.enableVertexAttribArray(loc.pos);gl.vertexAttribPointer(loc.pos,3,gl.FLOAT,false,0,0);gl.bindBuffer(gl.ARRAY_BUFFER,m.normal);gl.enableVertexAttribArray(loc.normal);gl.vertexAttribPointer(loc.normal,3,gl.FLOAT,false,0,0);gl.uniform4fv(loc.color,m.color);gl.uniform3fv(loc.offset,m.node.extras.explode.map(x=>x*explode));gl.drawArrays(gl.TRIANGLES,0,m.count)}gl.depthMask(true);document.documentElement.dataset.rendered=String(++renderedFrames)}
document.getElementById('whole').onclick=()=>{target=[0,.025,.015];distance=.76;yaw=.60;pitch=.63;draw()};
document.getElementById('detail').onclick=()=>{target=[-.084,.045,.181];distance=.25;yaw=.28;pitch=.30;draw()};
document.getElementById('explode').oninput=e=>{explode=Number(e.target.value)/100;draw()};
document.getElementById('toggle-controls').onclick=()=>document.getElementById('controls').classList.toggle('open');
let drag=null;const touches=new Map();let pinch=null;canvas.oncontextmenu=e=>e.preventDefault();canvas.onpointerdown=e=>{touches.set(e.pointerId,[e.clientX,e.clientY]);if(touches.size===2){const [a,b]=[...touches.values()];pinch=Math.hypot(a[0]-b[0],a[1]-b[1]);drag=null;canvas.setPointerCapture(e.pointerId);return;}drag=[e.clientX,e.clientY,e.button];canvas.setPointerCapture(e.pointerId)};canvas.onpointerup=canvas.onpointercancel=e=>{touches.delete(e.pointerId);drag=null;pinch=null};
canvas.onpointermove=e=>{if(touches.has(e.pointerId))touches.set(e.pointerId,[e.clientX,e.clientY]);if(touches.size===2){const [a,b]=[...touches.values()],next=Math.hypot(a[0]-b[0],a[1]-b[1]);if(pinch&&next>0)distance=Math.max(.065,Math.min(3,distance*pinch/next));pinch=next;draw();return;}if(!drag)return;const dx=e.clientX-drag[0],dy=e.clientY-drag[1];if(drag[2]===2){const right=[Math.cos(yaw),0,-Math.sin(yaw)],up=[-Math.sin(pitch)*Math.sin(yaw),Math.cos(pitch),-Math.sin(pitch)*Math.cos(yaw)];target=target.map((v,i)=>v-dx*distance*.0015*right[i]+dy*distance*.0015*up[i])}else{yaw-=dx*.008;pitch=Math.max(-1.4,Math.min(1.4,pitch+dy*.008))}drag[0]=e.clientX;drag[1]=e.clientY;draw()};
canvas.onwheel=e=>{e.preventDefault();distance=Math.max(.065,Math.min(3,distance*Math.exp(e.deltaY*.001)));draw()};addEventListener('resize',draw);draw();

}
start().catch(error=>{document.getElementById('status').textContent='The 3D viewer could not start.';document.getElementById('error').textContent=error.message;document.getElementById('retry').hidden=false;console.error(error)});
document.getElementById('retry').onclick=()=>location.reload();
