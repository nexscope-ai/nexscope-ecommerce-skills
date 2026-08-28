const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const SKILL_DIR = "/root/.claude/skills/geo-eval-ecommerce";
const ALLOWED_ENGINES = ["chatgpt", "claude", "gemini", "deepseek"];

module.exports = { run };

async function run(context, input) {
  const { logStep, outputDir } = context;

  logStep("validate-input", "started", "Validating product info and engines");
  const { productInfo, engines: rawEngines } = input;

  if (!productInfo || !productInfo.name || !productInfo.brand || !productInfo.category || !productInfo.price_range) {
    logStep("validate-input", "failed", "Missing required productInfo fields");
    return { ok: false, summary: "Validation failed", error: "productInfo must include name, brand, category, and price_range." };
  }
  if (!productInfo.usps || !Array.isArray(productInfo.usps) || productInfo.usps.length === 0) {
    logStep("validate-input", "failed", "usps is required and must be non-empty array");
    return { ok: false, summary: "Validation failed", error: "productInfo.usps must be a non-empty array." };
  }
  if (!productInfo.competitors || !Array.isArray(productInfo.competitors) || productInfo.competitors.length === 0) {
    logStep("validate-input", "failed", "competitors is required and must be non-empty array");
    return { ok: false, summary: "Validation failed", error: "productInfo.competitors must be a non-empty array." };
  }

  const engineList = (rawEngines && Array.isArray(rawEngines) && rawEngines.length > 0)
    ? rawEngines.filter(function(e) { return ALLOWED_ENGINES.includes(e); })
    : ALLOWED_ENGINES.slice();

  if (engineList.length === 0) {
    logStep("validate-input", "failed", "No valid engines specified");
    return { ok: false, summary: "Validation failed", error: "engines must contain at least one of: " + ALLOWED_ENGINES.join(", ") };
  }

  logStep("validate-input", "succeeded", "Product: " + productInfo.name + ", Engines: " + engineList.join(","));

  logStep("build-profile", "started", "Writing product info and building profile");

  var tmpJsonPath = path.join(outputDir, "product_info_input.json");
  var normalizedInfo = {
    name: productInfo.name,
    brand: productInfo.brand,
    asin: productInfo.asin || null,
    category: productInfo.category,
    price_range: productInfo.price_range,
    usps: productInfo.usps,
    channels: productInfo.channels || ["Amazon"],
    product_url: productInfo.product_url || null,
    competitors: productInfo.competitors.slice(0, 5).map(function(c) {
      return { name: c.name || "", price: c.price || "", description: c.description || "" };
    }),
    target_users: productInfo.target_users || "",
    core_scenario: productInfo.core_scenario || "",
    pain_points: productInfo.pain_points || ""
  };

  fs.mkdirSync(outputDir, { recursive: true });
  fs.writeFileSync(tmpJsonPath, JSON.stringify(normalizedInfo, null, 2), "utf-8");

  var profileSlug;
  try {
    var buildCmd = "cd " + JSON.stringify(SKILL_DIR) + " && python3 scripts/profile_builder.py " + JSON.stringify(tmpJsonPath);
    var buildOut = execSync(buildCmd, { encoding: "utf-8", timeout: 60000, stdio: ["pipe", "pipe", "pipe"] });
    var slugMatch = buildOut.match(/Profile slug:\s*(.+)/);
    if (slugMatch) {
      profileSlug = slugMatch[1].trim();
    } else {
      var createdMatch = buildOut.match(/Created:\s*profiles\/([^\/]+)/);
      profileSlug = createdMatch ? createdMatch[1].trim() : null;
    }
    if (!profileSlug) {
      logStep("build-profile", "failed", "Could not extract profile slug");
      return { ok: false, summary: "Profile build failed", error: "Could not determine profile slug. Output: " + buildOut.slice(0, 200) };
    }
  } catch (err) {
    var errMsg = (err.stderr || err.message || "").slice(0, 300);
    logStep("build-profile", "failed", errMsg);
    return { ok: false, summary: "Profile build failed", error: "profile_builder.py failed: " + errMsg };
  }

  logStep("build-profile", "succeeded", "Profile slug: " + profileSlug);

  logStep("run-pipeline", "started", "Running pipeline for profile=" + profileSlug);

  var runId;
  try {
    var pipelineCmd = "cd " + JSON.stringify(SKILL_DIR) + " && python3 -m scripts.cli --base-dir " + JSON.stringify(SKILL_DIR) + " run --profile " + JSON.stringify(profileSlug) + " --engines " + JSON.stringify(engineList.join(","));
    var pipelineOut = execSync(pipelineCmd, { encoding: "utf-8", timeout: 600000, stdio: ["pipe", "pipe", "pipe"] });
    var runIdMatch = pipelineOut.match(/run_id=([^\s\n]+)/);
    if (runIdMatch) {
      runId = runIdMatch[1].trim();
    }
    if (!runId) {
      logStep("run-pipeline", "failed", "Could not extract run_id");
      return { ok: false, summary: "Pipeline failed", error: "Could not determine run_id. Output: " + pipelineOut.slice(0, 300) };
    }
  } catch (err) {
    var pipeErrMsg = (err.stderr || err.stdout || err.message || "").slice(0, 500);
    logStep("run-pipeline", "failed", pipeErrMsg.slice(0, 200));
    return { ok: false, summary: "Pipeline execution failed", error: "CLI pipeline failed: " + pipeErrMsg };
  }

  logStep("run-pipeline", "succeeded", "Run completed: " + runId);

  logStep("verify-report", "started", "Checking report.html exists");

  var runDir = path.join(SKILL_DIR, "data", "runs", profileSlug, runId);
  var reportPath = path.join(runDir, "report.html");

  if (!fs.existsSync(reportPath)) {
    logStep("verify-report", "failed", "report.html not found");
    return { ok: false, summary: "Report generation failed", error: "report.html not found in run directory" };
  }

  var reportStat = fs.statSync(reportPath);
  if (reportStat.size < 1024) {
    logStep("verify-report", "failed", "report.html too small");
    return { ok: false, summary: "Report generation failed", error: "report.html is too small, likely incomplete" };
  }

  logStep("verify-report", "succeeded", "Report exists: " + reportStat.size + " bytes");

  logStep("finalize", "started", "Copying report and extracting metrics");

  var reportFileName = "geo-report-" + profileSlug + ".html";
  var destPath = path.join(outputDir, reportFileName);
  fs.copyFileSync(reportPath, destPath);

  var metrics = { mentionRate: 0, avgPosition: null, primaryRate: 0, totalEvaluations: 0 };
  var engineBreakdown = {};

  var preagPath = path.join(runDir, "preaggregate.json");
  if (fs.existsSync(preagPath)) {
    try {
      var preag = JSON.parse(fs.readFileSync(preagPath, "utf-8"));
      var smry = preag.summary || {};
      var engStats = preag.engine_stats || {};
      var recStr = preag.recommendation_strengths || {};
      var totalEvals = smry.total_evaluations || 0;

      metrics = {
        mentionRate: smry.mention_rate || 0,
        avgPosition: smry.avg_position || null,
        primaryRate: totalEvals > 0 ? (recStr.primary || 0) / totalEvals : 0,
        totalEvaluations: totalEvals
      };

      var engineKeys = Object.keys(engStats);
      for (var i = 0; i < engineKeys.length; i++) {
        var ek = engineKeys[i];
        var es = engStats[ek];
        engineBreakdown[ek] = {
          mentionRate: es.mention_rate || 0,
          primaryCount: (es.rec_strengths || {}).primary || 0
        };
      }
    } catch (e) {
      logStep("finalize", "info", "Could not parse preaggregate.json");
    }
  }

  logStep("finalize", "succeeded", "Report: " + reportFileName);

  var summaryText = "GEO evaluation complete: mention_rate=" + (metrics.mentionRate * 100).toFixed(1) + "%, avg_position=" + (metrics.avgPosition ? metrics.avgPosition.toFixed(1) : "N/A") + ", primary_rate=" + (metrics.primaryRate * 100).toFixed(1) + "%, total=" + metrics.totalEvaluations + " evaluations";

  return {
    ok: true,
    summary: summaryText,
    data: {
      reportFile: reportFileName,
      runId: runId,
      profileSlug: profileSlug,
      metrics: metrics,
      engineBreakdown: engineBreakdown
    }
  };
}
