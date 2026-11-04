const PG=await figma.getNodeByIdAsync('30:2'); await figma.setCurrentPageAsync(PG);
const IDS=__IDS__;
const W=390,PAD=20,IN=W-2*PAD;
const fonts=[['Anton','Regular'],['Montserrat','Regular'],['Montserrat','Medium'],['Montserrat','SemiBold'],['Montserrat','Bold'],['Montserrat','ExtraBold']];
for(const [family,style] of fonts) await figma.loadFontAsync({family,style});
function fs(s){if(s>=110)return 56;if(s>=80)return 44;if(s>=56)return 34;if(s>=40)return 28;if(s>=28)return 22;if(s>=20)return 18;return s;}
function isAL(n){return 'layoutMode' in n && n.layoutMode!=='NONE';}
function walk(n,depth){
  if(n.type==='TEXT'){
    const segs=n.getStyledTextSegments(['fontSize']);
    for(const sg of segs) n.setRangeFontSize(sg.start,sg.end,fs(sg.fontSize));
    if(n.letterSpacing && n.letterSpacing.unit==='PERCENT' && n.letterSpacing.value>8) n.letterSpacing={unit:'PERCENT',value:8};
    return;
  }
  if(n.type==='INSTANCE') return;
  if(n.type==='RECTANGLE'){
    if(n.width>IN && n.height>2){const r=n.height/n.width; n.resize(IN,Math.round(IN*r));}
    return;
  }
  if(!('children' in n)) return;
  if(isAL(n)){
    if(n.paddingLeft>=100){n.paddingLeft=PAD;n.paddingRight=PAD;}
    else if(n.paddingLeft>40){n.paddingLeft=Math.min(n.paddingLeft,24);n.paddingRight=Math.min(n.paddingRight,24);}
    if(n.paddingTop>=64){n.paddingTop=Math.round(n.paddingTop*.55);n.paddingBottom=Math.round(n.paddingBottom*.55);}
    if(n.paddingLeft>24&&n.paddingLeft<100){n.paddingLeft=24;}
    if(n.itemSpacing>40) n.itemSpacing=Math.round(n.itemSpacing*.6);
    const keep=n.name==='Título'||n.name.startsWith('Item')||n.name.startsWith('Botão');
    if(n.layoutMode==='HORIZONTAL' && !keep && n.children.filter(c=>c.visible).length>1){
      n.layoutMode='VERTICAL'; n.primaryAxisAlignItems='MIN'; n.counterAxisAlignItems='MIN'; n.itemSpacing=Math.min(Math.max(n.itemSpacing,16),32); n.primaryAxisSizingMode='AUTO';
    }
  }
  for(const c of [...n.children]) walk(c,depth+1);
  if(isAL(n)){
    for(const c of n.children){
      if(c.layoutPositioning==='ABSOLUTE') continue;
      try{
        if(n.layoutMode==='VERTICAL'){
          if(c.layoutSizingVertical==='FILL') c.layoutSizingVertical=isAL(c)?'HUG':'FIXED';
          if(c.type==='TEXT'){c.textAutoResize='HEIGHT';c.layoutSizingHorizontal='FILL';}
          else if(isAL(c) && !c.name.startsWith('Botão') && !c.name.startsWith('Item')) c.layoutSizingHorizontal='FILL';
        } else if(c.type==='TEXT' && c.width>IN-60){c.textAutoResize='HEIGHT';c.layoutSizingHorizontal='FILL';}
      }catch(e){}
    }
  }
}
function header(h){
  const right=h.children[1]; if(right) right.remove();
  const ic=figma.createNodeFromSvg('<svg width="28" height="28" viewBox="0 0 24 24"><path d="M3 6h18M3 12h18M3 18h18" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/></svg>');ic.name='Menu (ícone)';h.appendChild(ic);
  h.paddingLeft=PAD;h.paddingRight=PAD;h.layoutMode='HORIZONTAL';h.primaryAxisAlignItems='SPACE_BETWEEN';
}
const out=[];
for(const [id,i] of IDS){
  const src=await figma.getNodeByIdAsync(id);
  const name=src.name.replace(/^(\d+) · /,'$1 · Celular · ');
  const old=PG.children.find(n=>n.name===name); if(old) old.remove();
  const m=src.clone(); m.name=name; PG.appendChild(m); m.x=i*1540; m.y=10000;
  m.resize(W,m.height); m.counterAxisSizingMode='FIXED'; m.primaryAxisSizingMode='AUTO';
  for(const s of m.children){ if(s.name==='Cabeçalho'){header(s);} else walk(s,1); try{s.layoutSizingHorizontal='FILL';}catch(e){} }
  m.findAll(n=>n.name==='Ponto').forEach(n=>n.remove());
  const X=m.absoluteBoundingBox.x,R=X+W-PAD+1;
  const bad=m.findAll(n=>n.visible&&n.absoluteBoundingBox&&n.absoluteBoundingBox.x+n.absoluteBoundingBox.width>R&&n.name!=='Brilho'&&n.parent!==m).map(n=>n.name.slice(0,25)+'@'+n.parent.name);
  const fixedV=m.findAll(n=>n.type==='FRAME'&&n.layoutMode==='VERTICAL'&&n.primaryAxisSizingMode==='FIXED').map(n=>n.name).slice(0,10);
  out.push({id:m.id,name,h:Math.round(m.height),bad:bad.slice(0,12),fixedV});
}
return out;
