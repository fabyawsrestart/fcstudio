const PG=await figma.getNodeByIdAsync('30:2'); await figma.setCurrentPageAsync(PG);
const LOGO=await figma.getNodeByIdAsync('32:5');
const STAR='a2b86609309ce178f95ea34a66a273fffb76c19c',EQ='8600b1a38262bc2f0231c3dbaf4645306ab09071',GW='6c247ff2faaaccca6b3295761c730eaaf6c24bf4';
const hx=h=>({r:parseInt(h.slice(1,3),16)/255,g:parseInt(h.slice(3,5),16)/255,b:parseInt(h.slice(5,7),16)/255});
const S=(h,o=1)=>({type:'SOLID',color:hx(h),opacity:o});
const GR={type:'GRADIENT_LINEAR',gradientTransform:[[1,0,0],[0,1,0]],gradientStops:[{position:0,color:{...hx('#00F000'),a:1}},{position:1,color:{...hx('#00B100'),a:1}}]};
const STARS={type:'IMAGE',imageHash:STAR,scaleMode:'TILE',scalingFactor:1};
const FN={d:{family:'Anton',style:'Regular'},r:{family:'Montserrat',style:'Regular'},m:{family:'Montserrat',style:'Medium'},s:{family:'Montserrat',style:'SemiBold'},b:{family:'Montserrat',style:'Bold'},x:{family:'Montserrat',style:'ExtraBold'}};
for(const f of Object.values(FN)) await figma.loadFontAsync(f);
const C={g:'#00D61A',w:'#FFFFFF',t:'#A3A3A3',bk:'#050505',n:'#0D0D0D',card:'#141414',ln:'#2A2A2A',c3:'#CBD2D9',claro:'#F2F2F0',tinta:'#0A0A0A',t2:'#4B5563',v8:'#007A10'};
const GLOW=(a=.35,r=32)=>({type:'DROP_SHADOW',color:{...hx('#00D61A'),a},offset:{x:0,y:0},radius:r,spread:0,visible:true,blendMode:'NORMAL'});
function T(str,o={}){const {f='r',s=16,c=C.t,lh,ls=0,up=false,w,al='LEFT',name}=o;const t=figma.createText();t.fontName=FN[f];t.characters=str;t.fontSize=s;t.fills=[S(c)];if(lh)t.lineHeight={unit:'PERCENT',value:lh};if(ls)t.letterSpacing={unit:'PERCENT',value:ls};if(up)t.textCase='UPPER';t.textAlignHorizontal=al;if(name)t.name=name;if(w){t.resize(w,t.height);t.textAutoResize='HEIGHT';}return t;}
const green=(t,word)=>{const i=t.characters.indexOf(word);if(word&&i>=0)t.setRangeFills(i,i+word.length,[GR]);return t;};
const bold=(t,words,c=C.w)=>{for(const wd of words){const i=t.characters.indexOf(wd);if(i>=0){t.setRangeFontName(i,i+wd.length,FN.b);t.setRangeFills(i,i+wd.length,[S(c)]);}}return t;};
function AL(dir,kids=[],o={}){const a=figma.createAutoLayout(dir);a.fills=[];a.set(o);for(const k of kids)if(k)a.appendChild(k);return a;}
const Y0=7300; const out=[];
const old=PG.findAll(n=>n.parent===PG&&n.name.startsWith('Rede · ')); old.forEach(n=>n.remove());
function BG(name,w,h,x){const f=figma.createFrame();f.name=name;f.resize(w,h);f.x=x;f.y=Y0;f.clipsContent=true;f.fills=[S(C.bk),{...STARS,opacity:.9}];
 const g=figma.createEllipse();g.resize(w*.6,h*1.2);g.x=w*.55;g.y=-h*.1;g.fills=[S(C.g,.22)];g.effects=[{type:'LAYER_BLUR',radius:Math.max(w,h)*.12,visible:true}];g.name='Brilho';f.appendChild(g);PG.appendChild(f);out.push(f.id);return f;}
function LG(scale){const l=LOGO.createInstance();l.rescale(scale);return l;}
function BLOCK(hs,ss,w){const h=T('SITES QUE TRAZEM\nCLIENTES DE VERDADE.',{f:'d',s:hs,c:C.w,lh:98});green(h,'CLIENTES DE VERDADE.');
 const s=T('Strategic UI/UX Design · Sites, landing pages, sistemas e anúncios',{f:'m',s:ss,c:C.t,lh:140,w});
 const u=T('fcstudio.dev.br',{f:'b',s:ss,c:C.g});return AL('VERTICAL',[h,s,u],{itemSpacing:ss*.9});}
let x=0;
// YouTube banner 2560x1440, área segura 1546x423 no centro
{const f=BG('Rede · YouTube capa 2560x1440',2560,1440,x);
 const row=AL('HORIZONTAL',[LG(1.35),BLOCK(110,28,900)],{itemSpacing:80,counterAxisAlignItems:'CENTER'});f.appendChild(row);row.x=(2560-row.width)/2;row.y=(1440-row.height)/2;
 const safe=figma.createRectangle();safe.name='Área segura (apagar ao exportar)';safe.resize(1546,423);safe.x=507;safe.y=508;safe.fills=[];safe.strokes=[S(C.g,.5)];safe.dashPattern=[12,12];safe.visible=false;f.appendChild(safe);x+=2660;}
// YouTube foto 800x800
{const f=BG('Rede · YouTube foto 800x800',800,800,x);const l=LG(2.4);f.appendChild(l);l.x=(800-l.width)/2;l.y=(800-l.height)/2;x+=900;}
// LinkedIn logo 400x400
{const f=BG('Rede · LinkedIn logo 400x400',400,400,x);const l=LG(1.2);f.appendChild(l);l.x=(400-l.width)/2;l.y=(400-l.height)/2;x+=500;}
// LinkedIn página 1128x191 (logo da página cobre o canto esquerdo)
{const f=BG('Rede · LinkedIn página 1128x191',1128,191,0);f.y=Y0+1540;
 const h=T('SITES QUE TRAZEM CLIENTES DE VERDADE.',{f:'d',s:40,c:C.w});green(h,'CLIENTES DE VERDADE.');
 const s=T('Strategic UI/UX Design · fcstudio.dev.br',{f:'m',s:16,c:C.t});
 const b=AL('VERTICAL',[h,s],{itemSpacing:8,counterAxisAlignItems:'MAX'});f.appendChild(b);b.x=1128-b.width-48;b.y=(191-b.height)/2;}
// LinkedIn perfil 1584x396 (foto cobre o canto inferior esquerdo)
{const f=BG('Rede · LinkedIn perfil 1584x396',1584,396,1228);f.y=Y0+1540;
 const row=AL('HORIZONTAL',[LG(.75),BLOCK(64,20,620)],{itemSpacing:48,counterAxisAlignItems:'CENTER'});f.appendChild(row);row.x=1584-row.width-90;row.y=(396-row.height)/2;}
return out;
