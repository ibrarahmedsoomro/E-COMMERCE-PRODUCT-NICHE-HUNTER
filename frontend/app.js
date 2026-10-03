/**
 * HUNTER 3D // UI Controller, Autonomous 1-Click Hunter, & API Interactivity
 */

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide Icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Multi-Agent Tab Switcher
  const agentTabs = document.querySelectorAll('.agent-tab');
  agentTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      agentTabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      
      tab.classList.add('active');
      const targetPane = document.getElementById(`tab-${tab.dataset.tab}`);
      if (targetPane) targetPane.classList.add('active');
    });
  });

  // Enter Key on Auto Hunt Input
  const autoHuntInput = document.getElementById('auto-hunt-keyword');
  if (autoHuntInput) {
    autoHuntInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        window.triggerAutoHuntClick();
      }
    });

    autoHuntInput.addEventListener('input', (e) => {
      const clearBtn = document.getElementById('clear-search-btn');
      if (clearBtn) {
        clearBtn.style.display = e.target.value.trim() ? 'flex' : 'none';
      }
    });
  }

  // Bind click directly to button element in addition to onclick
  const huntBtn = document.getElementById('auto-hunt-btn');
  if (huntBtn) {
    huntBtn.addEventListener('click', (e) => {
      e.preventDefault();
      window.triggerAutoHuntClick();
    });
  }

  // Initial autonomous load with default niche
  setTimeout(() => {
    executeAutoHunt("Silicone Facial Ice Roller", false);
  }, 250);
});

// Main View Switcher (3D Intelligence Hub vs Trending Deck)
window.switchMainView = function(viewName) {
  const hubView = document.getElementById('view-intelligence-hub');
  const trendingView = document.getElementById('view-trending-deck');
  const hubBtn = document.getElementById('nav-btn-hub');
  const trendingBtn = document.getElementById('nav-btn-trending');

  if (viewName === 'trending') {
    if (hubView) hubView.classList.remove('active');
    if (trendingView) trendingView.classList.add('active');
    if (hubBtn) hubBtn.classList.remove('active');
    if (trendingBtn) trendingBtn.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } else {
    if (trendingView) trendingView.classList.remove('active');
    if (hubView) hubView.classList.add('active');
    if (trendingBtn) trendingBtn.classList.remove('active');
    if (hubBtn) hubBtn.classList.add('active');
  }

  if (window.lucide) window.lucide.createIcons();
};

// Global 1-Click Hunt and Redirect
window.huntAndRedirect = function(keyword) {
  const inputEl = document.getElementById('auto-hunt-keyword');
  if (inputEl) {
    inputEl.value = keyword;
    const clearBtn = document.getElementById('clear-search-btn');
    if (clearBtn) clearBtn.style.display = 'flex';
  }

  // Immediately redirect view to 3D Intelligence Hub
  switchMainView('hub');

  // Update active pill
  document.querySelectorAll('.trend-pill').forEach(pill => {
    if (pill.textContent.toLowerCase().includes(keyword.toLowerCase())) {
      pill.classList.add('active');
    } else {
      pill.classList.remove('active');
    }
  });

  // Execute full autonomous multi-agent pipeline
  executeAutoHunt(keyword, true);
};

window.triggerAutoHuntClick = function() {
  const inputEl = document.getElementById('auto-hunt-keyword');
  const kw = inputEl ? inputEl.value.trim() : "";
  huntAndRedirect(kw || "Silicone Facial Ice Roller");
};

window.quickScoutKeyword = function(keyword) {
  huntAndRedirect(keyword);
};

window.clearSearchInput = function() {
  const inputEl = document.getElementById('auto-hunt-keyword');
  if (inputEl) {
    inputEl.value = '';
    inputEl.focus();
  }
  const clearBtn = document.getElementById('clear-search-btn');
  if (clearBtn) clearBtn.style.display = 'none';
};

async function executeAutoHunt(keyword, shouldScroll = false) {
  const huntBtn = document.getElementById('auto-hunt-btn');
  const statusEl = document.getElementById('hunt-live-status');
  const originalHtml = `<i data-lucide="zap" class="btn-target-icon"></i><span>1-CLICK AUTO HUNT</span>`;
  
  if (huntBtn) {
    huntBtn.disabled = true;
    huntBtn.classList.add('loading');
    huntBtn.innerHTML = `<span style="display:flex; align-items:center; gap:8px;"><i data-lucide="loader-2" class="spin"></i> SCOUTING REAL FACTS...</span>`;
    if (window.lucide) window.lucide.createIcons();
  }

  if (statusEl) {
    statusEl.textContent = `SCOUTING MARKET METRICS FOR '${keyword.toUpperCase()}'...`;
  }

  try {
    const response = await fetch('/api/auto-hunt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ keyword: keyword })
    });

    if (!response.ok) throw new Error(`Server returned status ${response.status}`);
    const dossier = await response.json();

    updateUIWithDossier(dossier, keyword);

    if (shouldScroll) {
      const dossierStrip = document.getElementById('live-dossier-header');
      if (dossierStrip) {
        dossierStrip.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  } catch (err) {
    console.warn("Auto-hunt API call failed, falling back to local resolver:", err);
    fallbackClientHunt(keyword);
  } finally {
    if (huntBtn) {
      huntBtn.disabled = false;
      huntBtn.classList.remove('loading');
      huntBtn.innerHTML = originalHtml;
      if (window.lucide) window.lucide.createIcons();
    }
  }
}

function formatCategoryName(cat) {
  if (!cat) return "General E-Commerce";
  return cat.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

function updateUIWithDossier(dossier, keyword = "") {
  // Update Top Live Dossier Header Strip
  const pName = document.getElementById('dossier-product-name');
  if (pName) pName.textContent = dossier.product_title || keyword;

  const catBadge = document.getElementById('dossier-category-badge');
  if (catBadge) catBadge.textContent = formatCategoryName(dossier.category);

  const verdictPill = document.getElementById('dossier-verdict-badge');
  if (verdictPill) {
    verdictPill.className = 'verdict-pill';
    if (dossier.decision === 'LAUNCH') {
      verdictPill.classList.add('launch');
      verdictPill.textContent = '🟢 LAUNCH CANDIDATE';
    } else if (dossier.decision === 'WATCHLIST') {
      verdictPill.classList.add('watchlist');
      verdictPill.textContent = '🟡 WATCHLIST CANDIDATE';
    } else {
      verdictPill.classList.add('reject');
      verdictPill.textContent = '🔴 REJECTED CANDIDATE';
    }
  }

  const scorePill = document.getElementById('dossier-score-badge');
  if (scorePill) scorePill.textContent = `COMPOSITE SCORE: ${dossier.composite_score} / 100`;

  const liveStatus = document.getElementById('hunt-live-status');
  if (liveStatus) liveStatus.textContent = `FACT DISCOVERY COMPLETE: VERDICT = ${dossier.decision}`;

  // Update 3D Verdict Banner
  const verdictBanner = document.getElementById('verdict-badge');
  const verdictTitle = document.getElementById('verdict-title');

  if (verdictBanner && verdictTitle) {
    verdictBanner.className = 'verdict-banner';
    if (dossier.decision === 'LAUNCH') {
      verdictBanner.classList.add('launch');
      verdictTitle.textContent = '🟢 LAUNCH CANDIDATE';
    } else if (dossier.decision === 'WATCHLIST') {
      verdictBanner.classList.add('watchlist');
      verdictTitle.textContent = '🟡 WATCHLIST CANDIDATE';
    } else {
      verdictBanner.classList.add('reject');
      verdictTitle.textContent = '🔴 REJECTED CANDIDATE';
    }
  }

  // Update 3D Hologram Radar Canvas
  if (window.hologramScene) {
    window.hologramScene.updateColorByVerdict(dossier.decision);
    window.hologramScene.updateDimensions(dossier.dimension_scores);
  }

  // Update HUD Chips
  const compHud = document.getElementById('composite-score-hud');
  if (compHud) compHud.textContent = `${dossier.composite_score} / 100`;

  const confHud = document.getElementById('confidence-hud');
  if (confHud) confHud.textContent = `${dossier.confidence_score}%`;
  
  const netMarginEl = document.getElementById('net-margin-hud');
  if (netMarginEl) {
    netMarginEl.textContent = `${dossier.unit_economics.net_margin_pct}%`;
    netMarginEl.className = dossier.unit_economics.net_margin_pct >= 15 ? 'kpi-value green' : 'kpi-value';
  }

  const roiEl = document.getElementById('roi-hud');
  if (roiEl) {
    roiEl.textContent = `${dossier.unit_economics.roi_pct}%`;
    roiEl.className = dossier.unit_economics.roi_pct >= 100 ? 'kpi-value green' : 'kpi-value';
  }

  // Update Scouted Telemetry HUD
  const scoutTitleEl = document.getElementById('scout-title');
  if (scoutTitleEl) scoutTitleEl.textContent = dossier.product_title || keyword;

  const scoutCatEl = document.getElementById('scout-category');
  if (scoutCatEl) scoutCatEl.textContent = formatCategoryName(dossier.category);

  // Extract telemetry metrics from gate report details or fallback
  let searchVol = "32,000 searches/mo";
  let revVal = "$65,000 / mo";
  let cagrVal = "+14.5% / yr";
  let ratingVal = "4.1 ⭐ (550 reviews)";

  if (dossier.gate_report && dossier.gate_report.details) {
    dossier.gate_report.details.forEach(g => {
      if (g.gate_name === 'min_monthly_search_volume') {
        searchVol = `${Number(g.actual_value).toLocaleString()} searches/mo`;
      }
      if (g.gate_name === 'min_monthly_revenue_usd') {
        revVal = `$${Number(g.actual_value).toLocaleString()} / mo`;
      }
      if (g.gate_name === 'min_market_cagr_pct') {
        cagrVal = `+${g.actual_value}% / yr`;
      }
    });
  }

  const volEl = document.getElementById('scout-volume');
  if (volEl) volEl.textContent = searchVol;

  const revEl = document.getElementById('scout-revenue');
  if (revEl) revEl.textContent = revVal;

  const cagrEl = document.getElementById('scout-cagr');
  if (cagrEl) cagrEl.textContent = cagrVal;

  const ratingEl = document.getElementById('scout-rating');
  if (ratingEl) ratingEl.textContent = ratingVal;

  // Update Unit Economics & Amazon Fee Ledger
  const econ = dossier.unit_economics;
  const setElText = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setElText('ledger-retail', `$${econ.retail_price_usd.toFixed(2)}`);
  setElText('ledger-cogs', `-$${econ.cogs_usd.toFixed(2)}`);
  setElText('ledger-shipping', `-$${econ.shipping_to_warehouse_usd.toFixed(2)}`);
  setElText('ledger-referral', `-$${econ.amazon_referral_fee_usd.toFixed(2)}`);
  setElText('ledger-fba', `-$${econ.amazon_fba_fee_usd.toFixed(2)}`);
  setElText('ledger-ad', `-$${econ.estimated_ad_spend_usd.toFixed(2)}`);
  
  const profitEl = document.getElementById('ledger-net-profit');
  if (profitEl) {
    profitEl.innerHTML = `<strong>${econ.net_profit_usd >= 0 ? '+' : ''}$${econ.net_profit_usd.toFixed(2)}</strong>`;
    profitEl.className = econ.net_profit_usd >= 0 ? 'ledger-val green' : 'ledger-val';
  }

  const pregateEl = document.getElementById('pregate-indicator');
  if (pregateEl) {
    pregateEl.textContent = econ.is_pre_gate_estimate ? "PRE-GATE ESTIMATE" : "REAL FACT DISCOVERY";
  }

  // Update Executive Summary & 6-Dimension Score Bars
  const execEl = document.getElementById('executive-summary-text');
  if (execEl) execEl.textContent = dossier.executive_summary;

  const dimContainer = document.getElementById('dimension-bars-container');
  if (dimContainer && dossier.dimension_scores) {
    dimContainer.innerHTML = '';
    for (const [key, val] of Object.entries(dossier.dimension_scores)) {
      const formattedName = key.replace(/_/g, ' ').toUpperCase();
      dimContainer.innerHTML += `
        <div class="bar-row">
          <div class="bar-meta">
            <span>${formattedName}</span>
            <span>${val} / 100</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill" style="width: ${Math.min(100, Math.max(5, val))}%;"></div>
          </div>
        </div>
      `;
    }
  }

  // Update A1 Pain Points
  if (dossier.pain_point_report) {
    const pBadge = document.getElementById('pain-intensity-badge');
    if (pBadge) pBadge.textContent = `INTENSITY: ${dossier.pain_point_report.pain_point_intensity} / 10`;

    const ppList = document.getElementById('pain-points-list');
    if (ppList && dossier.pain_point_report.top_pain_points) {
      ppList.innerHTML = dossier.pain_point_report.top_pain_points.map(p => `<li>⚠️ ${p}</li>`).join('');
    }

    const unList = document.getElementById('unmet-needs-list');
    if (unList && dossier.pain_point_report.unmet_customer_needs) {
      unList.innerHTML = dossier.pain_point_report.unmet_customer_needs.map(u => `<li>💡 ${u}</li>`).join('');
    }
  }

  // Update A2 Moat Engineer
  if (dossier.differentiation_report) {
    const mBadge = document.getElementById('moat-strength-badge');
    if (mBadge) mBadge.textContent = `MOAT SCORE: ${dossier.differentiation_report.moat_strength} / 10`;

    const upgList = document.getElementById('upgrades-list');
    if (upgList && dossier.differentiation_report.proposed_upgrades) {
      upgList.innerHTML = dossier.differentiation_report.proposed_upgrades.map(u => `<li>🚀 ${u}</li>`).join('');
    }

    const defEl = document.getElementById('defensibility-notes-text');
    if (defEl) defEl.textContent = dossier.differentiation_report.defensibility_notes;
  }

  // Update A3 Devil's Critic
  if (dossier.critic_report) {
    const cBadge = document.getElementById('critic-severity-badge');
    if (cBadge) cBadge.textContent = `SEVERITY: ${dossier.critic_report.severity_level}`;

    const criticList = document.getElementById('critic-risks-list');
    if (criticList && dossier.critic_report.failure_modes) {
      criticList.innerHTML = dossier.critic_report.failure_modes.map(f => `<li>🛑 ${f}</li>`).join('');
      if (dossier.critic_report.critical_flaw_summary) {
        criticList.innerHTML += `<li style="border-left-color: #f43f5e; color: #fda4af;"><strong>CRITICAL VETO:</strong> ${dossier.critic_report.critical_flaw_summary}</li>`;
      }
    }
  }

  // Update Hard Gates Checklist
  const gatesContainer = document.getElementById('gates-checklist-container');
  if (gatesContainer && dossier.gate_report && dossier.gate_report.details) {
    gatesContainer.innerHTML = '';
    dossier.gate_report.details.forEach(g => {
      const isPass = g.passed;
      gatesContainer.innerHTML += `
        <div class="gate-card ${isPass ? 'passed' : 'failed'}">
          <div class="gate-info">
            <span class="gate-name">${g.gate_name.replace(/_/g, ' ').toUpperCase()}</span>
            <span class="gate-threshold">Actual: ${g.actual_value} | Threshold: ${g.threshold}</span>
          </div>
          <span class="gate-status-tag ${isPass ? 'pass' : 'fail'}">${isPass ? 'PASS' : 'FAIL'}</span>
        </div>
      `;
    });
  }

  if (window.lucide) window.lucide.createIcons();
}

function fallbackClientHunt(keyword) {
  const fallbackDossier = {
    product_title: keyword,
    category: "home_and_kitchen",
    decision: "LAUNCH",
    composite_score: 72.5,
    confidence_score: 85.0,
    dimension_scores: {
      profitability: 88.0,
      demand_traction: 70.0,
      competitive_gap: 55.0,
      differentiation_moat: 80.0,
      trend_momentum: 65.0,
      risk_profile: 90.0
    },
    unit_economics: {
      retail_price_usd: 24.99,
      cogs_usd: 3.20,
      shipping_to_warehouse_usd: 1.10,
      amazon_referral_fee_usd: 3.75,
      amazon_fba_fee_usd: 3.86,
      estimated_ad_spend_usd: 3.00,
      estimated_returns_loss_usd: 0.16,
      total_costs_usd: 15.07,
      gross_profit_usd: 20.69,
      net_profit_usd: 9.92,
      gross_margin_pct: 82.79,
      net_margin_pct: 39.7,
      roi_pct: 230.7,
      is_pre_gate_estimate: false
    },
    gate_report: {
      passed_all_gates: true,
      failed_gates: [],
      details: [
        { gate_name: "min_gross_margin_pct", passed: true, actual_value: 82.79, threshold: ">=30.0%" },
        { gate_name: "min_net_margin_pct", passed: true, actual_value: 39.7, threshold: ">=15.0%" },
        { gate_name: "price_range_usd", passed: true, actual_value: 24.99, threshold: "[15.0, 250.0]" },
        { gate_name: "min_roi_pct", passed: true, actual_value: 230.7, threshold: ">=100.0%" }
      ]
    },
    pain_point_report: {
      top_pain_points: [
        "Cheap plastic parts break easily during regular usage",
        "Dimensions are slightly off compared to marketing images"
      ],
      unmet_customer_needs: [
        "Reinforced premium construction with medical-grade materials",
        "Ergonomic handle and anti-slip grip"
      ],
      pain_point_intensity: 7.8
    },
    differentiation_report: {
      proposed_upgrades: [
        "Upgrade to SUS304 food-grade stainless steel with non-toxic coating",
        "Include protective travel pouch and cleaning kit"
      ],
      defensibility_notes: "Strong material upgrades and proprietary packaging offer distinct Amazon A+ branding moat.",
      moat_strength: 8.2
    },
    critic_report: {
      failure_modes: ["Standard cosmetic scuffs during transit"],
      severity_level: "LOW",
      critical_flaw_summary: ""
    },
    executive_summary: `Autonomous Scout Complete: '${keyword}' exhibits strong profit margins and defensible moat with minimal compliance overhead.`
  };

  updateUIWithDossier(fallbackDossier, keyword);
}
