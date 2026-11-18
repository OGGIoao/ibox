// 根系探测器：认亲、分层、快照对比与根系图绘制
// 纯 JS，零依赖。浏览器里挂在 window.RootProbe 上，Node 里用 require 引入（测试用）。
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.RootProbe = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const P8 = {
    black: '#000000', darkBlue: '#1D2B53', darkPurple: '#7E2553', darkGreen: '#008751',
    brown: '#AB5236', darkGray: '#5F574F', lightGray: '#C2C3C7', white: '#FFF1E8',
    red: '#FF004D', orange: '#FFA300', yellow: '#FFEC27', green: '#00E436',
    blue: '#29ADFF', indigo: '#83769C', pink: '#FF77A8', peach: '#FFCCAA'
  };

  const ARTICLE = 'https://github.com/OGGIoao/digital-civilization/blob/main/toys/s2e01-root-probe/%E6%8B%86%E8%A7%A3.md';

  // 四层深度 + 横切的高危痕迹。depth 越大，根扎得越深。
  const LAYERS = {
    surface: { name: '地表', depth: 1, desc: '你看得见的界面：右键菜单、文件关联、快捷方式', band: P8.brown },
    strata: { name: '地层', depth: 2, desc: '系统的账本和机关：注册表、开机自启、服务、计划任务', band: P8.darkGray },
    deep: { name: '深层', depth: 3, desc: '硬盘上的家当：程序目录和数据目录里的文件夹', band: P8.darkBlue },
    core: { name: '核心', depth: 4, desc: '内核里的驱动：权限比管理员还高', band: P8.darkPurple },
    edge: { name: '横切', depth: 0, desc: '改变电脑信任谁、网络走哪里的痕迹', band: P8.black }
  };

  // 每种足迹：属于哪一层、30 秒原理、如果它是残留该怎么处理
  const KINDS = {
    contextmenu: {
      label: '右键菜单', layer: 'surface', hook: true,
      explain: '右键菜单里的每一项，都是注册表 Classes 下的一行登记；复杂的菜单项是一个 DLL，Explorer 在你右键的那一刻把它加载进来。',
      fix: '在注册表编辑器里找到"登记位置"那一项，先右键导出备份，再删除。'
    },
    association: {
      label: '文件关联', layer: 'surface', hook: true,
      explain: '双击一个文件时，系统按"扩展名 → 你的选择 → 类型名 → 打开命令"这条路找到要运行的程序。终点被删了，路标还在，双击就会出错。',
      fix: '在"设置 → 应用 → 默认应用"里，把这种文件的打开方式换成别的程序即可，不需要动注册表。'
    },
    shortcut: {
      label: '快捷方式', layer: 'surface', hook: false,
      explain: '快捷方式是一个小文件，里面记着目标程序的路径。程序删了，快捷方式不会自己消失。',
      fix: '直接删除这个快捷方式即可。'
    },
    uninstall: {
      label: '户口（卸载登记）', layer: 'strata', hook: false,
      explain: '"设置 → 应用"里的已安装列表不是扫描硬盘得来的，而是读注册表里的卸载登记。软件删了、登记没擦，列表里就还有它。',
      fix: '先在"设置 → 应用"里点卸载；卸载程序已经不在时，再到注册表里导出备份后删除这一项登记。'
    },
    regkey: {
      label: '注册表设置', layer: 'strata', hook: false,
      explain: '软件把自己的设置写在 Software\\厂商名 下面。32 位软件在 64 位系统上会被转到 WOW6432Node 下。留下来只占一点空间，不会自己运行。',
      fix: '确认这个厂商的软件你一个都不用了，再导出备份后删除。'
    },
    run: {
      label: '开机自启', layer: 'strata', hook: true,
      explain: '注册表 Run 键里列着的程序，会在你登录后被系统挨个启动。',
      fix: '在任务管理器的"启动应用"页把它禁用；确认无误后，再到注册表里导出备份并删除。'
    },
    startup: {
      label: '启动文件夹', layer: 'strata', hook: true,
      explain: '"启动"文件夹里的快捷方式，会在你登录时被运行。在地址栏输入 shell:startup 就能打开它。',
      fix: '打开启动文件夹，删除这个快捷方式即可。'
    },
    service: {
      label: '服务', layer: 'strata', hook: true,
      explain: '服务在你登录之前就开始运行，由 services.exe 统一管理。程序删了、服务登记还在，它每次开机都会尝试启动，然后失败。',
      fix: '先在 services.msc 里把启动类型改成"禁用"，观察几天；确认无误后，再用管理员权限运行 sc delete 删除。'
    },
    task: {
      label: '计划任务', layer: 'strata', hook: true,
      explain: '计划任务是"到点或遇到某个事件，就运行某个程序"的登记。软件的自动更新器常藏在这里，"卸载后又复活"多半出在它身上。',
      fix: '打开"任务计划程序"（taskschd.msc），先禁用这项任务，确认无误后再删除。'
    },
    folder: {
      label: '文件夹', layer: 'deep', hook: false,
      explain: '程序本体在 Program Files，设置在 AppData，共享数据在 ProgramData。卸载程序常常故意把数据目录留下，"方便你以后重装"。',
      fix: '确认里面没有你要的东西（比如存档、聊天记录），再删除整个文件夹。'
    },
    driver: {
      label: '驱动', layer: 'core', hook: true,
      explain: '驱动运行在内核态，权限比管理员还高。安全软件的"自我保护"就靠它：在内核里拦下所有删除自己的请求。',
      fix: '风险最高：删错可能开不了机。先用软件官方卸载程序；仍有残留时，先禁用、重启、观察，确认无误后再处理。'
    },
    hosts: {
      label: 'hosts 条目', layer: 'edge', hook: true,
      explain: 'hosts 文件可以强行把一个网址指向某个地址。有的软件用它屏蔽广告，恶意软件和破解工具用它把官方服务器挡在门外。',
      fix: '用管理员身份打开记事本，编辑 C:\\Windows\\System32\\drivers\\etc\\hosts，删除这一行前先复制一份备份。'
    }
  };

  const SIG_OK = new Set(['Valid', 'SignedLarge', 'System', 'WHQL']);
  const SIG_TEXT = {
    Valid: '签名有效', SignedLarge: '已签名（大文件未逐字节校验）', System: '系统文件',
    WHQL: '驱动认证签名（微软代签，厂商名取自文件信息）',
    NotSigned: '没有签名', HashMismatch: '签名被破坏：文件被改过', UnknownError: '签名无法验证', Unknown: '签名无法读取'
  };

  function parseKeywords(input) {
    return String(input || '').split(/[\s,，|]+/).map((k) => k.trim().toLowerCase()).filter((k) => k.length >= 2);
  }

  function lc(v) { return v == null ? '' : String(v).toLowerCase(); }

  // 这条记录的"名字层面"是否对得上关键词
  function textOf(r) {
    const e = r.extra || {};
    return [r.name, r.target, e.publisher, e.display, e.installLocation, e.progId, e.author,
      (r.kind === 'task' ? r.location : '')].map(lc).join('\n');
  }
  function keywordHit(r, kws) {
    const t = textOf(r);
    return kws.some((k) => t.includes(k));
  }

  // 认亲：签名者要拿得出硬证据，才算"一家"。硬证据有三种：
  //   1. 签名者的名字本身对得上关键词（比如 NVIDIA）；
  //   2. 它签的是名字对得上的卸载程序（官方卸载程序只会由官方签）；
  //   3. 它签的文件就在这个软件的安装目录里。
  // 只是"签了一个名字对得上的文件"不算：冒名者正是这么干的。
  function findFamily(records, kws, underAnchor) {
    const counts = new Map();
    const wantsMicrosoft = kws.some((k) => k.includes('microsoft') || 'microsoft'.includes(k));
    for (const r of records) {
      if (!r.signer || !SIG_OK.has(r.sig)) continue;
      if (/^microsoft/i.test(r.signer) && !wantsMicrosoft) continue;
      const hit = keywordHit(r, kws);
      const strong = kws.some((k) => lc(r.signer).includes(k))
        || (hit && r.kind === 'uninstall')
        || (hit && !!underAnchor && !!r.target && underAnchor(r.target));
      if (strong) counts.set(r.signer, (counts.get(r.signer) || 0) + 1);
    }
    return [...counts.entries()].sort((a, b) => b[1] - a[1]).map(([signer, count]) => ({ signer, count }));
  }

  function normPath(p) { return lc(p).replace(/^"|"$/g, '').replace(/\\+$/, ''); }

  // 公共目录不能当成某个软件的"家"，否则它下面所有东西都会被错认
  const GENERIC_DIR = /(^[a-z]:$)|\\(program files( \(x86\))?|programdata|windows|system32|users|users\\[^\\]+|appdata|appdata\\(roaming|local|locallow)|local\\programs|%userprofile%|%userprofile%\\appdata(\\(roaming|local|locallow))?)$/;
  function isAnchor(p) {
    return !!p && p.split('\\').length >= 3 && !GENERIC_DIR.test(p);
  }

  // 给每条记录定性：确定 / 很可能 / 名字像但签名是别人
  function attribute(records, keywordInput) {
    const kws = parseKeywords(keywordInput);
    if (!kws.length) return { kws, family: [], items: [] };
    // 先找"家"：名字对得上的卸载登记里写的安装目录，以及名字对得上的文件夹
    const anchors = [];
    for (const r of records) {
      if (!keywordHit(r, kws)) continue;
      const candidates = [];
      if (r.kind === 'uninstall' && r.extra && r.extra.installLocation) candidates.push(normPath(r.extra.installLocation));
      if (r.kind === 'folder') candidates.push(normPath(`${r.location}\\${r.name}`));
      candidates.filter(isAnchor).forEach((a) => anchors.push(a));
    }
    const underAnchor = (p) => {
      const n = normPath(p);
      return !!n && anchors.some((a) => n === a || n.startsWith(`${a}\\`));
    };
    // 再认亲：只有拿得出硬证据的签名者才算一家，防止冒名者把自己的签名带进来
    const family = findFamily(records, kws, underAnchor);
    const familySet = new Set(family.map((f) => f.signer));

    const items = [];
    for (const r of records) {
      const meta = KINDS[r.kind];
      if (!meta) continue;
      const hit = keywordHit(r, kws);
      const sigOk = SIG_OK.has(r.sig);
      const inFamily = !!r.signer && familySet.has(r.signer);
      let confidence = null;
      let reason = '';
      if (inFamily && sigOk) {
        confidence = 'certain';
        reason = `签名者是 ${r.signer}`;
      } else if (r.target && underAnchor(r.target)) {
        confidence = 'certain';
        reason = '指向它的安装目录';
      } else if (r.kind === 'folder' && underAnchor(`${r.location}\\${r.name}`) && hit) {
        confidence = 'certain';
        reason = '它的安装目录或数据目录';
      } else if (hit) {
        if (r.sig === 'HashMismatch') {
          confidence = 'mismatch';
          reason = '名字对得上，但签名被破坏：文件被改过';
        } else if (sigOk && r.signer && !inFamily) {
          confidence = 'mismatch';
          reason = `名字对得上，但签名者是 ${r.signer}`;
        } else if (r.exists === false) {
          confidence = 'likely';
          reason = '名字对得上，但指向的文件已经不在了';
        } else if (r.target && r.exists && !sigOk) {
          confidence = 'likely';
          reason = '名字对得上，但文件没有有效签名';
        } else {
          confidence = 'likely';
          reason = '名字对得上';
        }
      }
      if (!confidence) continue;
      items.push({ ...r, layer: meta.layer, confidence, reason, broken: r.exists === false });
    }
    return { kws, family, items };
  }

  // "名字像、签名却是别人"的条目单独放：不算它的根，也不算进深度
  function summarize(items) {
    const own = items.filter((it) => it.confidence !== 'mismatch');
    const byLayer = { surface: [], strata: [], deep: [], core: [], edge: [] };
    own.forEach((it) => byLayer[it.layer].push(it));
    const depth = Math.max(0, ...own.map((it) => LAYERS[it.layer].depth));
    const deepest = Object.keys(LAYERS).find((k) => LAYERS[k].depth === depth && depth > 0) || null;
    return {
      total: own.length,
      broken: own.filter((it) => it.broken || it.residue).length,
      hooks: own.filter((it) => KINDS[it.kind].hook).length,
      certain: own.filter((it) => it.confidence === 'certain').length,
      mismatch: items.length - own.length,
      lookalikes: items.filter((it) => it.confidence === 'mismatch'),
      byLayer,
      depth,
      deepest
    };
  }

  // Echo 对结果的一句话
  function echoLine(sum, subject) {
    if (!sum.total) return `灯下找不到「${subject}」的根。要么它从没来过，要么走得很干净。`;
    if (sum.broken && sum.broken === sum.total) return `「${subject}」的人已经走了，可 ${sum.broken} 条根还留在地里，全是断的。`;
    if (sum.broken) return `${sum.total} 条根里，有 ${sum.broken} 条已经断了：登记还在，要找的文件却不见了。`;
    if (sum.deepest === 'core') return `「${subject}」的根一直扎到了核心层。那里的东西，管理员也拔不动。`;
    if (sum.depth <= 1) return `「${subject}」只在地表留下了一点痕迹，是个讲究的住客。`;
    return `「${subject}」在 ${sum.depth} 层地里扎了 ${sum.total} 条根，其中 ${sum.hooks} 条是会自己醒来的钩子。`;
  }

  // —— 快照对比 ——
  function recordKey(r) { return `${r.kind}|${lc(r.location)}|${lc(r.name)}`; }

  function diffSnapshots(before, after, final) {
    const keysOf = (snap) => new Map((snap.records || []).map((r) => [recordKey(r), r]));
    const a = keysOf(before);
    const b = keysOf(after);
    const added = [...b.entries()].filter(([k]) => !a.has(k)).map(([, r]) => r);
    const removed = [...a.entries()].filter(([k]) => !b.has(k)).map(([, r]) => r);
    let leftover = null;
    let cleaned = null;
    if (final) {
      const c = keysOf(final);
      leftover = added.filter((r) => c.has(recordKey(r))).map((r) => c.get(recordKey(r)));
      cleaned = added.filter((r) => !c.has(recordKey(r)));
    }
    return { added, removed, leftover, cleaned };
  }

  // 快照对比里的记录：不需要认亲，前后一比就是铁证
  function asItems(records, isLeftover) {
    return records.filter((r) => KINDS[r.kind]).map((r) => ({
      ...r,
      layer: KINDS[r.kind].layer,
      confidence: 'certain',
      reason: isLeftover ? '装上时出现，卸载后还在' : '这段时间里新出现的',
      broken: r.exists === false,
      residue: !!isLeftover
    }));
  }

  // —— 根系图（只在浏览器里用）——
  function seeded(seedText) {
    let h = 2166136261;
    for (const ch of String(seedText)) { h ^= ch.codePointAt(0); h = Math.imul(h, 16777619); }
    return () => { h ^= h << 13; h ^= h >>> 17; h ^= h << 5; return ((h >>> 0) % 10000) / 10000; };
  }

  function drawRootMap(canvas, model) {
    const W = 1080;
    const H = 1350;
    canvas.width = W;
    canvas.height = H;
    const g = canvas.getContext('2d');
    const rand = seeded(model.title);
    const font = (px, bold) => `${bold ? 'bold ' : ''}${px}px "Microsoft YaHei", "PingFang SC", sans-serif`;
    g.imageSmoothingEnabled = false;

    // 天空
    g.fillStyle = P8.black;
    g.fillRect(0, 0, W, H);
    for (let i = 0; i < 60; i += 1) {
      g.fillStyle = i % 3 ? P8.darkGray : P8.lightGray;
      g.fillRect(Math.floor(rand() * W), Math.floor(rand() * 300), 3, 3);
    }

    // 标题（文字始终正对屏幕）
    g.fillStyle = P8.blue;
    g.font = font(30, true);
    g.fillText('根系探测器', 56, 72);
    g.fillStyle = P8.white;
    g.font = font(model.title.length > 10 ? 44 : 60, true);
    g.fillText(model.title, 56, 140);
    g.fillStyle = P8.lightGray;
    g.font = font(28);
    g.fillText(model.subtitle, 56, 186);

    // 地层：四条横带
    const top = 420;
    const bandH = 190;
    const order = ['surface', 'strata', 'deep', 'core'];
    order.forEach((key, i) => {
      const y = top + i * bandH;
      g.fillStyle = LAYERS[key].band;
      g.fillRect(0, y, W, bandH);
      g.fillStyle = 'rgba(0,0,0,0.25)';
      for (let x = 0; x < W; x += 24) g.fillRect(x + (i % 2) * 12, y + bandH - 6, 12, 6);
      g.fillStyle = P8.white;
      g.font = font(30, true);
      g.fillText(LAYERS[key].name, 40, y + 46);
      g.font = font(24);
      g.fillStyle = P8.peach;
      const n = model.sum.byLayer[key].length;
      g.fillText(n ? `${n} 条根` : '—', 40, y + 82);
    });

    // 小岛：一个漂浮的文件夹（系统物件学：小岛本身是一个文件夹）
    const cx = W / 2 + 80;
    const iy = 330;
    g.fillStyle = P8.yellow;
    g.fillRect(cx - 150, iy - 70, 110, 26);
    g.fillRect(cx - 150, iy - 48, 300, 64);
    g.fillStyle = P8.orange;
    g.fillRect(cx - 150, iy + 8, 300, 10);
    g.fillStyle = P8.brown;
    g.beginPath();
    g.moveTo(cx - 150, iy + 18);
    g.lineTo(cx + 150, iy + 18);
    g.lineTo(cx + 40, iy + 90);
    g.lineTo(cx - 60, iy + 90);
    g.closePath();
    g.fill();

    // 根：每条足迹一条，按层往下扎。黄 = 已验证，蓝 = 未决，红 = 断口
    const roots = [];
    order.forEach((key) => model.sum.byLayer[key].forEach((it) => roots.push(it)));
    const shown = roots.slice(0, 90);
    shown.forEach((it, idx) => {
      const li = order.indexOf(it.layer);
      const endY = top + li * bandH + 40 + rand() * (bandH - 70);
      const endX = 200 + rand() * (W - 260);
      const startX = cx - 50 + (idx % 20) * 5;
      const cut = it.broken || it.residue;
      const color = cut ? P8.red : it.confidence === 'certain' ? P8.yellow : P8.blue;
      g.strokeStyle = color;
      g.lineWidth = cut ? 3 : 4;
      g.setLineDash(it.confidence === 'mismatch' ? [8, 8] : []);
      g.beginPath();
      g.moveTo(startX, iy + 80);
      const steps = 4 + li * 2;
      let x = startX;
      for (let s = 1; s <= steps; s += 1) {
        const t = s / steps;
        const y = iy + 80 + (endY - iy - 80) * t;
        x = x + (endX - x) * (1 / (steps - s + 1)) + (rand() - 0.5) * 30;
        if (cut && s === steps) break; // 断口：最后一截不画
        g.lineTo(Math.round(x), Math.round(y));
      }
      g.stroke();
      g.setLineDash([]);
      g.fillStyle = color;
      if (!cut) g.fillRect(Math.round(endX) - 5, Math.round(endY) - 5, 10, 10);
    });
    if (roots.length > shown.length) {
      g.fillStyle = P8.lightGray;
      g.font = font(22);
      g.fillText(`图里画了 ${shown.length} 条，共 ${roots.length} 条`, 56, 222);
    }

    // 底部：Echo 的话与落款
    const by = top + 4 * bandH;
    g.fillStyle = P8.black;
    g.fillRect(0, by, W, H - by);
    g.fillStyle = P8.blue;
    g.fillRect(56, by + 34, 14, 22);
    g.fillStyle = P8.white;
    g.font = font(28);
    wrapText(g, model.echo, 86, by + 54, W - 140, 40);
    g.fillStyle = P8.darkGray;
    g.font = font(22);
    g.fillText(`数字文明 · 根系探测器 · ${model.date}`, 56, H - 30);
    g.fillStyle = P8.yellow; g.fillRect(W - 300, H - 44, 14, 14);
    g.fillStyle = P8.lightGray; g.fillText('已验证', W - 280, H - 30);
    g.fillStyle = P8.blue; g.fillRect(W - 200, H - 44, 14, 14);
    g.fillStyle = P8.lightGray; g.fillText('未决', W - 180, H - 30);
    g.fillStyle = P8.red; g.fillRect(W - 120, H - 44, 14, 14);
    g.fillStyle = P8.lightGray; g.fillText('断根', W - 100, H - 30);
  }

  function wrapText(g, text, x, y, maxW, lineH) {
    let line = '';
    let yy = y;
    for (const ch of text) {
      if (g.measureText(line + ch).width > maxW) { g.fillText(line, x, yy); line = ch; yy += lineH; }
      else line += ch;
    }
    if (line) g.fillText(line, x, yy);
  }

  return {
    P8, LAYERS, KINDS, SIG_TEXT, ARTICLE,
    parseKeywords, keywordHit, findFamily, attribute, summarize, echoLine,
    recordKey, diffSnapshots, asItems, drawRootMap
  };
});
