// 文件精灵：由文件的 SHA-256 指纹确定性地生成一只像素精灵，并画成一张可分享的卡片。
// 同一份文件永远得到同一只；改动任意一个字节，指纹就会彻底改变，精灵也随之完全不同。
// 生成部分是纯函数（Node 测试可直接调用），绘制部分只在浏览器中使用。
// 颜色只用 PICO-8 十六色（ADR-005）；文字一律在全分辨率层绘制（ADR-007）。
(function initFileSpirit(root, factory) {
  const api = factory();
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.FileSpirit = api;
}(typeof globalThis !== 'undefined' ? globalThis : this, function createFileSpirit() {
  const P8 = {
    black: '#000000', darkBlue: '#1D2B53', darkPurple: '#7E2553', darkGreen: '#008751',
    brown: '#AB5236', darkGray: '#5F574F', lightGray: '#C2C3C7', white: '#FFF1E8',
    red: '#FF004D', orange: '#FFA300', yellow: '#FFEC27', green: '#00E436',
    blue: '#29ADFF', indigo: '#83769C', pink: '#FF77A8', peach: '#FFCCAA'
  };

  const RACES = [
    { id: 'image', name: '画灵', exts: ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'heic', 'svg', 'ico', 'psd'], palettes: [[P8.pink, P8.peach], [P8.orange, P8.peach], [P8.pink, P8.darkPurple]], accent: P8.orange },
    { id: 'doc', name: '书灵', exts: ['txt', 'md', 'doc', 'docx', 'pdf', 'ppt', 'pptx', 'xls', 'xlsx', 'csv', 'rtf', 'epub'], palettes: [[P8.lightGray, P8.white], [P8.peach, P8.white], [P8.indigo, P8.lightGray]], accent: P8.indigo },
    { id: 'code', name: '码灵', exts: ['js', 'ts', 'py', 'c', 'cpp', 'h', 'java', 'cs', 'go', 'rs', 'html', 'css', 'json', 'ps1', 'sh', 'sql', 'xml', 'yml', 'yaml'], palettes: [[P8.green, P8.darkGreen], [P8.darkGreen, P8.lightGray], [P8.green, P8.darkBlue]], accent: P8.lightGray },
    { id: 'program', name: '机灵', exts: ['exe', 'dll', 'msi', 'bat', 'cmd', 'lnk', 'sys', 'scr', 'com'], palettes: [[P8.indigo, P8.darkGray], [P8.lightGray, P8.darkGray], [P8.darkGray, P8.darkBlue]], accent: P8.orange },
    { id: 'audio', name: '音灵', exts: ['mp3', 'wav', 'flac', 'm4a', 'ogg', 'aac', 'mid'], palettes: [[P8.indigo, P8.darkPurple], [P8.pink, P8.darkPurple], [P8.peach, P8.indigo]], accent: P8.pink },
    { id: 'video', name: '影灵', exts: ['mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm'], palettes: [[P8.darkBlue, P8.indigo], [P8.indigo, P8.peach], [P8.darkPurple, P8.indigo]], accent: P8.peach },
    { id: 'archive', name: '匣灵', exts: ['zip', 'rar', '7z', 'tar', 'gz', 'iso', 'cab'], palettes: [[P8.brown, P8.orange], [P8.orange, P8.peach], [P8.brown, P8.darkGray]], accent: P8.peach },
    { id: 'other', name: '荒灵', exts: [], palettes: [[P8.darkGray, P8.brown], [P8.indigo, P8.darkGray], [P8.lightGray, P8.brown]], accent: P8.lightGray }
  ];
  const FIRST = ['阿', '小', '噗', '咕', '米', '糖', '豆', '波', '啾', '嘟', '叮', '芽', '泡', '栗', '绒', '布', '奶', '饼', '圆', '蹦', '果', '乐', '团', '毛'];
  const SECOND = ['噜', '啾', '咪', '嘀', '叭', '嗒', '奇', '丸', '糕', '球', '宝', '仔', '喵', '扑', '丁', '朵', '吉', '比', '多', '卡', '酥', '叽', '蛋', '蕾'];
  const PERSONALITIES = ['好奇', '害羞', '暴躁', '慵懒', '话痨', '勇敢', '爱睡', '机灵'];
  const SIZE_TIERS = [
    { max: 1024, name: '微型', scale: 0.7 },
    { max: 1024 * 1024, name: '小型', scale: 0.85 },
    { max: 100 * 1024 * 1024, name: '中型', scale: 1.0 },
    { max: Infinity, name: '巨型', scale: 1.2 }
  ];
  const RARITIES = { legendary: { name: '传说', color: P8.yellow }, rare: { name: '稀有', color: P8.lightGray }, common: { name: '普通', color: P8.indigo } };
  const RACE_LINES = {
    image: '它把这张画里的颜色都偷偷记在了身上。',
    doc: '它肚子里装满了字，走路都在小声背书。',
    code: '它说话总喜欢加个分号；',
    program: '一按开关，它就会立刻开始干活。',
    audio: '凑近一点，能听见它在哼歌。',
    video: '它眨一次眼，就是一帧画面。',
    archive: '它把好多东西折叠起来，塞进了自己的小匣子。',
    other: '我还没见过这种文件……它是从哪里来的？'
  };
  const GRID = 12; // 精灵主体 12×12，左右对称
  // 轮廓变体：[横向收缩, 纵向收缩, 边缘噪声]，让同一种族也有圆、高、宽、尖四种身形
  const SHAPES = [[1.0, 1.0, 0], [1.35, 0.9, 0], [0.85, 1.25, 0], [1.0, 1.0, 0.35]];
  const HALF = GRID / 2;

  function bytesFromHex(hex) {
    const clean = String(hex).trim().toLowerCase();
    if (!/^[0-9a-f]{64}$/.test(clean)) throw new Error('需要 64 位十六进制的 SHA-256 指纹');
    const bytes = new Uint8Array(32);
    for (let i = 0; i < 32; i += 1) bytes[i] = parseInt(clean.slice(i * 2, i * 2 + 2), 16);
    return bytes;
  }

  // 按位读取指纹；读完 256 位后从头循环
  function bitReader(bytes) {
    let pos = 0;
    return (n) => {
      let v = 0;
      for (let k = 0; k < n; k += 1) {
        const byte = bytes[(pos >> 3) % bytes.length];
        v = (v << 1) | ((byte >> (7 - (pos & 7))) & 1);
        pos += 1;
      }
      return v;
    };
  }

  function raceFor(ext) {
    const e = String(ext || '').replace(/^\./, '').toLowerCase();
    return RACES.find((r) => r.exts.includes(e)) || RACES[RACES.length - 1];
  }

  function sizeTier(size) {
    return SIZE_TIERS.find((t) => size < t.max) || SIZE_TIERS[SIZE_TIERS.length - 1];
  }

  function rarityFor(bytes) {
    if (bytes[31] < 4) return 'legendary'; // 约 1.6%
    if (bytes[31] < 36) return 'rare'; // 约 12.5%
    return 'common';
  }

  // 生成 12×12 的身体格子：中心大概率填充、边缘小概率，形成“生物”的轮廓
  function bodyCells(read, race, body, shape) {
    const [sx, sy, spike] = SHAPES[shape];
    const cells = Array.from({ length: GRID }, () => Array(GRID).fill(null));
    for (let y = 0; y < GRID; y += 1) {
      for (let x = 0; x < HALF; x += 1) {
        const dx = ((HALF - 0.5 - x) / HALF) * sx;
        const dy = ((y - 6.2) / 5.6) * sy;
        const r = dx * dx + dy * dy;
        let prob = r < 0.3 ? 0.95 : r < 0.6 ? 0.6 : r < 0.9 ? 0.25 + spike : 0.04 + spike * 0.5;
        if (y < 2) prob *= 0.5;
        const v = read(4) / 16;
        if (v < prob) {
          const shade = read(2) === 0 || y > 8 ? body[1] : body[0];
          cells[y][x] = shade;
          cells[y][GRID - 1 - x] = shade;
        }
      }
    }
    // 保证身体核心实心，避免生成过于稀疏的形状
    for (let y = 4; y <= 8; y += 1) {
      for (let x = 3; x < HALF; x += 1) {
        if (!cells[y][x]) {
          cells[y][x] = body[0];
          cells[y][GRID - 1 - x] = body[0];
        }
      }
    }
    // 腿：底部两行按指纹选择形态
    const legs = read(2);
    for (let x = 0; x < GRID; x += 1) cells[11][x] = null;
    const legX = [[3], [2, 4], [4], [1, 3]][legs];
    legX.forEach((lx) => {
      cells[10][lx] = body[1];
      cells[10][GRID - 1 - lx] = body[1];
      cells[11][lx] = body[1];
      cells[11][GRID - 1 - lx] = body[1];
    });
    return cells;
  }

  function addFace(cells, read) {
    const ey = 4 + read(1);
    const ex = 3 + read(1);
    const style = read(2);
    const eye = (x, y, c) => { cells[y][x] = c; cells[y][GRID - 1 - x] = c; };
    if (style === 0) eye(ex, ey, P8.black);
    else if (style === 1) { eye(ex, ey, P8.black); eye(ex, ey + 1, P8.black); }
    else if (style === 2) { eye(ex, ey, P8.black); eye(ex - 1, ey, P8.black); }
    else { eye(ex, ey, P8.white); eye(ex, ey + 1, P8.black); }
    const mouth = read(2);
    if (mouth === 1) { cells[ey + 2][HALF - 1] = P8.black; cells[ey + 2][HALF] = P8.black; }
    else if (mouth === 2) cells[ey + 2][HALF - 1] = P8.black;
    if (read(2) === 3) { cells[ey + 1][ex - 1] = P8.pink; cells[ey + 1][GRID - ex] = P8.pink; } // 腮红
    return { ex, ey };
  }

  // 种族特征：让同一种族的精灵有一眼能认出的共同点
  function addFeature(cells, race, read) {
    const a = race.accent;
    const v = read(2);
    switch (race.id) {
      case 'image': cells[7][0] = a; cells[8][0] = a; cells[9][1] = a; break; // 画笔尾巴
      case 'doc': cells[1][8] = P8.white; cells[1][9] = P8.white; cells[2][9] = P8.white; cells[2][8] = P8.indigo; break; // 书页折角
      case 'code': cells[6][0] = a; cells[6][GRID - 1] = a; cells[5][1] = a; cells[7][1] = a; cells[5][GRID - 2] = a; cells[7][GRID - 2] = a; break; // < >
      case 'program': cells[0][HALF] = a; cells[1][HALF] = P8.lightGray; cells[2][HALF] = P8.lightGray; break; // 天线
      case 'audio': cells[0][HALF + 1] = a; cells[1][HALF + 1] = a; cells[1][HALF + 2] = a; cells[2][HALF + 1] = a; break; // 音符
      case 'video': cells[4][HALF - 1] = P8.white; cells[4][HALF] = P8.white; cells[5][HALF - 1] = P8.darkBlue; cells[5][HALF] = P8.darkBlue; break; // 镜头
      case 'archive': for (let y = 3; y <= 9; y += 2) cells[y][HALF - 1] = a; break; // 拉链
      default: if (v === 0) { cells[1][2] = a; cells[1][GRID - 3] = a; } break;
    }
  }

  function outlined(cells) {
    const size = GRID + 2;
    const out = Array.from({ length: size }, () => Array(size).fill(null));
    for (let y = 0; y < GRID; y += 1) for (let x = 0; x < GRID; x += 1) out[y + 1][x + 1] = cells[y][x];
    for (let y = 0; y < size; y += 1) {
      for (let x = 0; x < size; x += 1) {
        if (out[y][x]) continue;
        const near = [[1, 0], [-1, 0], [0, 1], [0, -1]].some(([dx, dy]) => {
          const c = out[y + dy] && out[y + dy][x + dx];
          return c && c !== 'outline';
        });
        if (near) out[y][x] = 'outline';
      }
    }
    return out.map((row) => row.map((c) => (c === 'outline' ? P8.black : c)));
  }

  function daysBetween(a, b) {
    const t0 = new Date(a).getTime();
    const t1 = new Date(b).getTime();
    if (!Number.isFinite(t0) || !Number.isFinite(t1)) return 0;
    return Math.max(0, (t1 - t0) / 86400000);
  }

  function formatSize(n) {
    if (n < 1024) return `${n} B`;
    if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
    if (n < 1024 * 1024 * 1024) return `${(n / 1024 / 1024).toFixed(1)} MB`;
    return `${(n / 1024 / 1024 / 1024).toFixed(2)} GB`;
  }

  function echoComment(info, race, rarity, now) {
    const idle = daysBetween(info.modified, now);
    if (rarity === 'legendary') return '传说级！我在整个平原都没见过这样的指纹。';
    if (idle >= 365 * 3) return `它在这里睡了 ${Math.floor(idle / 365)} 年，你还记得它吗？`;
    if (idle < 1) return '它还热乎着——你刚刚才改过它。';
    if (info.size >= 1024 * 1024 * 1024) return `好大一只……它一个就占了你 ${formatSize(info.size)} 的硬盘。`;
    if (info.size < 1024) return '这么小一只，大概只有一句话那么重。';
    if (rarity === 'rare') return `稀有！${RACE_LINES[race.id]}`;
    return RACE_LINES[race.id];
  }

  // 纯函数：同样的输入永远得到同样的精灵
  function generate(info, options = {}) {
    const now = options.now || new Date().toISOString();
    const bytes = bytesFromHex(info.sha256);
    const read = bitReader(bytes);
    const race = raceFor(info.ext);
    const body = race.palettes[bytes[5] % race.palettes.length];
    const cells = bodyCells(read, race, body, bytes[6] % SHAPES.length);
    addFace(cells, read);
    addFeature(cells, race, read);
    const rarity = rarityFor(bytes);
    const tier = sizeTier(Number(info.size) || 0);
    const age = daysBetween(info.created, now);
    return {
      name: FIRST[bytes[1] % FIRST.length] + SECOND[bytes[2] % SECOND.length] + (rarity === 'legendary' ? SECOND[bytes[3] % SECOND.length] : ''),
      race: race.name,
      raceId: race.id,
      accent: race.accent,
      personality: PERSONALITIES[bytes[4] % PERSONALITIES.length],
      rarity,
      rarityName: RARITIES[rarity].name,
      rarityColor: RARITIES[rarity].color,
      level: Math.min(99, 1 + Math.floor(Math.sqrt(age))),
      sizeName: tier.name,
      scale: tier.scale,
      sprite: outlined(cells),
      fingerprint: Array.from(bytes),
      comment: echoComment(info, race, rarity, now)
    };
  }

  // ———————————— 以下为浏览器绘制 ————————————
  const UI = '"Microsoft YaHei", "PingFang SC", "Noto Sans SC", sans-serif';
  const MONO = 'Consolas, "Cascadia Mono", "Microsoft YaHei", monospace';
  const W = 600;
  const H = 980;

  function shortHash(hex) {
    return `${hex.slice(0, 8)}…${hex.slice(-4)}`;
  }

  function formatDate(iso) {
    const d = new Date(iso);
    if (!Number.isFinite(d.getTime())) return '未知';
    const p = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
  }

  function fitText(ctx, text, maxWidth) {
    if (ctx.measureText(text).width <= maxWidth) return text;
    let t = text;
    while (t.length > 1 && ctx.measureText(`${t}…`).width > maxWidth) t = t.slice(0, -1);
    return `${t}…`;
  }

  function drawScene(ctx, spirit, t) {
    const top = 40;
    const h = 380;
    const grad = ctx.createLinearGradient(0, top, 0, top + h);
    grad.addColorStop(0, P8.black);
    grad.addColorStop(1, P8.darkBlue);
    ctx.fillStyle = grad;
    ctx.fillRect(6, top, W - 12, h);
    // 桌面图标网格
    for (let y = top + 14; y < top + h; y += 28) {
      for (let x = 22; x < W - 10; x += 32) {
        ctx.fillStyle = Math.sin(x * 0.37 + y * 0.11 + t * 1.2) > 0.9 ? P8.indigo : '#151d3a';
        ctx.fillRect(x, y, 2, 2);
      }
    }
    // 迷你文件夹浮岛：等距菱形 + 棕色侧面 + 标签页 + 垂下的根须
    const cx = W / 2;
    const cy = top + 290;
    const rw = 150;
    const rh = 52;
    ctx.fillStyle = '#7a3a26';
    ctx.beginPath(); ctx.moveTo(cx - rw, cy); ctx.lineTo(cx, cy + rh); ctx.lineTo(cx, cy + rh + 22); ctx.lineTo(cx - rw, cy + 22); ctx.closePath(); ctx.fill();
    ctx.fillStyle = P8.brown;
    ctx.beginPath(); ctx.moveTo(cx + rw, cy); ctx.lineTo(cx, cy + rh); ctx.lineTo(cx, cy + rh + 22); ctx.lineTo(cx + rw, cy + 22); ctx.closePath(); ctx.fill();
    ctx.fillStyle = P8.orange;
    ctx.beginPath(); ctx.moveTo(cx - 20, cy - rh - 8); ctx.lineTo(cx + 70, cy - rh + 37); ctx.lineTo(cx + 70, cy - rh + 31); ctx.lineTo(cx - 20, cy - rh - 14); ctx.closePath(); ctx.fill();
    ctx.fillStyle = '#c99a78';
    ctx.beginPath(); ctx.moveTo(cx, cy - rh); ctx.lineTo(cx + rw, cy); ctx.lineTo(cx, cy + rh); ctx.lineTo(cx - rw, cy); ctx.closePath(); ctx.fill();
    ctx.strokeStyle = 'rgba(0,0,0,0.12)';
    ctx.lineWidth = 2;
    for (let k = -2; k <= 2; k += 1) {
      ctx.beginPath(); ctx.moveTo(cx + k * 30 - 60, cy + k * 10 - 20 - 10); ctx.lineTo(cx + k * 30 + 60, cy + k * 10 + 20 - 10); ctx.stroke();
    }
    ctx.fillStyle = '#3a3350';
    for (let k = 0; k < 6; k += 1) {
      const x = cx - 80 + k * 30;
      const len = 20 + ((spirit.fingerprint[k] % 5) * 8);
      ctx.fillRect(x, cy + 30 + Math.abs(x - cx) * -0.15 + 20, 2, len);
    }
    // 稀有度光环
    const bob = Math.round(Math.sin(t * 2.4) * 4);
    const px = Math.round(11 * spirit.scale);
    const size = spirit.sprite.length * px;
    const sx = Math.round(cx - size / 2);
    const sy = Math.round(cy - 18 - size + bob);
    if (spirit.rarity !== 'common') {
      ctx.strokeStyle = spirit.rarityColor;
      ctx.lineWidth = 3;
      ctx.setLineDash([6, 6]);
      ctx.lineDashOffset = -t * 20;
      ctx.beginPath(); ctx.ellipse(cx, sy + size / 2, size * 0.68, size * 0.68, 0, 0, Math.PI * 2); ctx.stroke();
      ctx.setLineDash([]);
      for (let k = 0; k < 6; k += 1) {
        const a = t * 1.5 + k * 1.05;
        const r = size * 0.75;
        ctx.fillStyle = spirit.rarityColor;
        ctx.fillRect(Math.round(cx + Math.cos(a) * r) - 2, Math.round(sy + size / 2 + Math.sin(a) * r * 0.6) - 2, 4, 4);
      }
    }
    ctx.fillStyle = 'rgba(0,0,0,0.35)';
    ctx.beginPath(); ctx.ellipse(cx, cy - 16, size * 0.36, 9, 0, 0, Math.PI * 2); ctx.fill();
    spirit.sprite.forEach((row, y) => row.forEach((c, x) => {
      if (!c) return;
      ctx.fillStyle = c;
      ctx.fillRect(sx + x * px, sy + y * px, px, px);
    }));
  }

  function drawCard(canvas, info, spirit, t = 0) {
    const dpr = (typeof window !== 'undefined' && window.devicePixelRatio) || 1;
    if (canvas.width !== W * dpr) {
      canvas.width = W * dpr;
      canvas.height = H * dpr;
      canvas.style.width = `${W}px`;
      canvas.style.height = `${H}px`;
    }
    const ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.imageSmoothingEnabled = false;
    ctx.textBaseline = 'middle';
    // 窗口外框与标题栏
    ctx.fillStyle = P8.black;
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = P8.lightGray;
    ctx.fillRect(0, 0, W, 40);
    ctx.fillRect(0, 0, 6, H); ctx.fillRect(W - 6, 0, 6, H); ctx.fillRect(0, H - 6, W, 6);
    ctx.fillStyle = P8.black;
    ctx.font = `bold 18px ${UI}`;
    ctx.fillText(fitText(ctx, `召唤文件精灵 — ${info.name}`, W - 140), 16, 20);
    [[W - 92, P8.darkGray], [W - 64, P8.darkGray], [W - 36, P8.red]].forEach(([x, c]) => {
      ctx.fillStyle = c;
      ctx.fillRect(x, 12, 18, 16);
    });
    drawScene(ctx, spirit, t);

    // 名字与标签
    let y = 456;
    ctx.fillStyle = P8.white;
    ctx.font = `900 40px ${UI}`;
    ctx.fillText(spirit.name, 28, y);
    const nameW = ctx.measureText(spirit.name).width;
    const tag = (text, x, bg, fg) => {
      ctx.font = `bold 18px ${UI}`;
      const w = ctx.measureText(text).width + 20;
      ctx.fillStyle = bg;
      ctx.fillRect(x, y - 15, w, 30);
      ctx.fillStyle = fg;
      ctx.fillText(text, x + 10, y);
      return x + w + 10;
    };
    let tx = tag(spirit.race, 28 + nameW + 18, spirit.accent, P8.black);
    tag(spirit.rarityName, tx, spirit.rarityColor, P8.black);

    // 属性
    y = 516;
    const stats = [['等级', `Lv.${spirit.level}`], ['体型', spirit.sizeName], ['性格', spirit.personality], ['大小', formatSize(info.size)]];
    stats.forEach(([k, v], i) => {
      const x = 28 + i * 138;
      ctx.fillStyle = '#151d3a';
      ctx.fillRect(x, y - 24, 128, 62);
      ctx.fillStyle = P8.indigo;
      ctx.font = `15px ${UI}`;
      ctx.fillText(k, x + 12, y - 6);
      ctx.fillStyle = P8.white;
      ctx.font = `bold 22px ${UI}`;
      ctx.fillText(v, x + 12, y + 20);
    });
    y = 592;
    ctx.font = `16px ${UI}`;
    ctx.fillStyle = P8.lightGray;
    ctx.fillText(fitText(ctx, `文件：${info.name}`, W - 56), 28, y);
    ctx.fillText(`诞生：${formatDate(info.created)}　　最后修改：${formatDate(info.modified)}`, 28, y + 28);

    // 文件指纹：32 根柱子对应 32 个字节
    y = 666;
    ctx.fillStyle = P8.white;
    ctx.font = `bold 17px ${UI}`;
    ctx.fillText('文件指纹 SHA-256', 28, y);
    ctx.fillStyle = P8.indigo;
    ctx.font = `15px ${MONO}`;
    ctx.fillText(shortHash(info.sha256), 200, y);
    spirit.fingerprint.forEach((b, i) => {
      const h = 6 + Math.round((b / 255) * 40);
      ctx.fillStyle = i % 2 ? P8.indigo : P8.lightGray;
      ctx.fillRect(28 + i * 17, y + 62 - h, 11, h);
    });
    ctx.fillStyle = P8.lightGray;
    ctx.font = `15px ${UI}`;
    ctx.fillText('同一个文件永远召唤出同一只；改一个字，就会变成完全不同的另一只。', 28, y + 84);

    // Echo 的评语：系统物件学里的一个小窗口
    y = 790;
    ctx.fillStyle = 'rgba(0,0,0,0.9)';
    ctx.fillRect(28, y, W - 56, 96);
    ctx.fillStyle = P8.blue;
    ctx.fillRect(28, y, W - 56, 28);
    ctx.fillRect(28, y, 3, 96); ctx.fillRect(W - 31, y, 3, 96); ctx.fillRect(28, y + 93, W - 56, 3);
    ctx.fillStyle = P8.black;
    ctx.font = `bold 15px ${MONO}`;
    ctx.fillText('Echo', 40, y + 14);
    ctx.fillStyle = P8.white;
    ctx.font = `bold 20px ${UI}`;
    ctx.fillText(fitText(ctx, spirit.comment, W - 96), 44, y + 62);

    // 落款：方便截图传播
    ctx.fillStyle = P8.indigo;
    ctx.font = `15px ${UI}`;
    ctx.fillText('数字文明 · 第一集 Explorer 平原', 28, H - 40);
    ctx.textAlign = 'right';
    ctx.fillText('B 站 / 抖音搜：数字文明', W - 28, H - 40);
    ctx.textAlign = 'left';
  }

  return { P8, RACES, generate, drawCard, bytesFromHex, raceFor, formatSize, CARD_SIZE: { width: W, height: H } };
}));
