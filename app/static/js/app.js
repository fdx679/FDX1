/* 智能招聘简历筛选系统 - 前端交互逻辑 */
"use strict";

const SAMPLE_RESUME = `Name: Li Ming
Email: liming@example.com
Phone: +86 138 0000 0000
Education: Bachelor of Computer Science, 2019-2023

Summary:
Passionate Python Developer with 3 years of experience building backend services and data pipelines. Strong skills in Python, Django, Flask, SQL, MySQL, Redis, and REST API development. Experience with machine learning using scikit-learn, pandas and numpy. Familiar with Docker, Kubernetes, Git and Linux.

Work Experience:
Backend Developer, TechCompany (2023 - Present)
- Developed REST APIs with Flask and Django
- Designed and optimized MySQL databases
- Built ETL data pipelines with Python and pandas
- Deployed services using Docker and CI/CD

Skills:
Python, Java, Django, Flask, SQL, MySQL, Redis, REST API, Git, Linux, Docker, Kubernetes, pandas, numpy, scikit-learn, machine learning, communication, teamwork`;

let graphChart = null;

// ---------------------------------------------------------------------------
// 工具函数
// ---------------------------------------------------------------------------
function el(id) { return document.getElementById(id); }

function escapeHtml(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function chipList(items) {
  if (!items || !items.length) return '<span class="hint">无</span>';
  return items.map(i => `<span class="chip">${escapeHtml(i)}</span>`).join("");
}

// ---------------------------------------------------------------------------
// 初始化
// ---------------------------------------------------------------------------
async function init() {
  el("btnAnalyze").addEventListener("click", analyze);
  el("btnSample").addEventListener("click", () => {
    el("resumeText").value = SAMPLE_RESUME;
  });
  el("btnGraph").addEventListener("click", () => loadGraphSkills());
  el("graphJob").addEventListener("change", () => loadGraphSkills());

  await loadJobs();
  await loadGraph();
  await loadHistory();
}

// 加载岗位类别
async function loadJobs() {
  try {
    const res = await fetch("/api/graph/jobs");
    const data = await res.json();
    const sel = el("jobFilter");
    sel.innerHTML = "";
    (data.jobs || []).forEach(j => {
      const opt = document.createElement("option");
      opt.value = j; opt.textContent = j;
      sel.appendChild(opt);
    });
    const gsel = el("graphJob");
    gsel.innerHTML = "";
    (data.jobs || []).forEach(j => {
      const opt = document.createElement("option");
      opt.value = j; opt.textContent = j;
      gsel.appendChild(opt);
    });
  } catch (e) { console.error(e); }
}

// ---------------------------------------------------------------------------
// 解析与匹配
// ---------------------------------------------------------------------------
async function analyze() {
  const text = el("resumeText").value.trim();
  if (!text) { el("resultArea").innerHTML = '<div class="error">请先输入简历文本</div>'; return; }

  el("resultArea").innerHTML = '<div class="loading">正在解析与匹配，请稍候…</div>';

  const jobs = Array.from(el("jobFilter").selectedOptions).map(o => o.value);
  const body = { text };
  if (jobs.length) body.jobs = jobs;

  try {
    const res = await fetch("/api/match/rank", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "请求失败");
    renderResult(data);
    await loadHistory();
  } catch (e) {
    el("resultArea").innerHTML = `<div class="error">解析失败：${escapeHtml(e.message)}</div>`;
  }
}

function renderResult(data) {
  const p = data.parsed || {};
  const cls = data.classification || {};
  const ranking = data.ranking || [];

  let html = "";

  // 解析结果
  html += `<div class="result-block"><h3>简历解析结果</h3><div class="kv-grid">
    <div class="kv"><span class="k">姓名</span><span class="v">${escapeHtml(p.name || "未识别")}</span></div>
    <div class="kv"><span class="k">邮箱</span><span class="v">${escapeHtml(p.email || "-")}</span></div>
    <div class="kv"><span class="k">电话</span><span class="v">${escapeHtml(p.phone || "-")}</span></div>
    <div class="kv"><span class="k">学历</span><span class="v">${escapeHtml((p.education||[]).join("、") || "未识别")}</span></div>
    <div class="kv"><span class="k">经验</span><span class="v">${p.experience_years || 0} 年</span></div>
    <div class="kv"><span class="k">岗位意向</span><span class="v">${escapeHtml((p.job_intent||[]).join("、") || "-")}</span></div>
  </div>
  <p style="margin-top:8px;"><strong>技能（${p.skill_count || 0} 项）：</strong>${chipList(p.skills)}</p>
  </div>`;

  // 分类结果
  html += `<div class="result-block"><h3>岗位分类（TF-IDF + 逻辑回归）</h3>
    <p><strong>预测岗位：</strong>${escapeHtml(cls.predicted_category || "-")}
    <span class="chip">置信度 ${(cls.confidence*100||0).toFixed(1)}%</span></p>
    <p style="margin-top:6px;"><strong>Top 候选：</strong>${(cls.top_k||[]).map(t =>
      `<span class="chip">${escapeHtml(t.category)} ${(t.score*100).toFixed(0)}%</span>`).join("")}</p>
  </div>`;

  // 匹配排名
  html += `<div class="result-block"><h3>岗位匹配排名（多维度融合）</h3>`;
  if (!ranking.length) {
    html += '<span class="hint">无匹配结果</span>';
  } else {
    ranking.forEach(r => {
      const levelClass = r.level === "高匹配" ? "good" : (r.level === "中匹配" ? "mid" : "low");
      const pct = Math.max(0, Math.min(100, r.match_score));
      html += `<div class="match-row">
        <span class="job-name">${escapeHtml(r.job_category)}</span>
        <div class="bar-bg"><div class="bar-fill ${levelClass}" style="width:${pct}%"></div></div>
        <span class="score">${pct.toFixed(0)}</span>
        <span class="level">${r.level}</span>
      </div>
      <div class="hint">命中技能：${r.matched_skills.length}/${r.job_required_skills.length}，
        ${r.missing_skills.length ? `缺失技能：${escapeHtml(r.missing_skills.join("、"))}` : "技能全覆盖 ✓"}
        （知识图谱推理）</div>`;
    });
  }
  html += `</div>`;

  el("resultArea").innerHTML = html;
}

// ---------------------------------------------------------------------------
// 知识图谱
// ---------------------------------------------------------------------------
async function loadGraph() {
  try {
    const res = await fetch("/api/graph/echarts");
    const data = await res.json();
    renderGraph(data);
  } catch (e) { console.error(e); }
}

async function loadGraphSkills() {
  const job = el("graphJob").value;
  if (!job) return;
  try {
    const res = await fetch(`/api/graph/job_skills?job=${encodeURIComponent(job)}`);
    const data = await res.json();
    if (data.skills) {
      el("graphSkillInfo").innerHTML =
        `<strong>${escapeHtml(job)}</strong> 所需技能：${chipList(data.skills)}`;
    }
    const gres = await fetch(`/api/graph/echarts?jobs=${encodeURIComponent(job)}`);
    const gdata = await gres.json();
    renderGraph(gdata);
  } catch (e) { console.error(e); }
}

function renderGraph(data) {
  const dom = el("graphChart");
  if (!graphChart) graphChart = echarts.init(dom);
  const nodes = (data.nodes || []).map(n => ({
    name: n.name,
    category: n.category === "job" ? 0 : 1,
    symbolSize: n.category === "job" ? 30 : 16,
    itemStyle: n.category === "job"
      ? { color: "#2a5a8f" }
      : { color: "#5aa9e6" },
  }));
  const links = (data.links || []).map(l => ({ source: l.source, target: l.target }));

  graphChart.setOption({
    tooltip: { formatter: p => p.dataType === "node" ? p.data.name : `${p.data.source} → ${p.data.target}` },
    legend: [{ data: ["岗位", "技能"], top: 4 }],
    series: [{
      type: "graph",
      layout: "force",
      roam: true,
      data: nodes,
      links: links,
      categories: [{ name: "岗位" }, { name: "技能" }],
      label: { show: true, fontSize: 10 },
      force: { repulsion: 180, edgeLength: 60 },
      lineStyle: { color: "#c0d4e8", width: 1 },
    }],
  });
}

// ---------------------------------------------------------------------------
// 历史记录
// ---------------------------------------------------------------------------
async function loadHistory() {
  try {
    const res = await fetch("/api/match/history");
    const data = await res.json();
    const rows = data.analyses || [];
    const area = el("historyArea");
    if (!rows.length) {
      area.innerHTML = '<div class="empty-tip">暂无历史记录</div>';
      return;
    }
    let html = `<table class="history-table"><tr>
      <th>姓名</th><th>预测岗位</th><th>最佳匹配</th><th>最高分</th><th>时间</th></tr>`;
    rows.forEach(r => {
      const best = (r.match_result || [])[0] || {};
      html += `<tr>
        <td>${escapeHtml(r.resume_name || "-")}</td>
        <td>${escapeHtml(r.predicted_category || "-")}</td>
        <td>${escapeHtml(best.job_category || "-")}</td>
        <td>${best.match_score != null ? best.match_score.toFixed(1) : "-"}</td>
        <td>${escapeHtml(r.created_at || "")}</td></tr>`;
    });
    html += "</table>";
    area.innerHTML = html;
  } catch (e) { console.error(e); }
}

document.addEventListener("DOMContentLoaded", init);
window.addEventListener("resize", () => { if (graphChart) graphChart.resize(); });
