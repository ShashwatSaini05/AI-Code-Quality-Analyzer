import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Editor from '@monaco-editor/react';
import {
  FiPlay, FiCode, FiShield, FiZap, FiActivity, FiAlertTriangle,
  FiCheckCircle, FiClock, FiCopy, FiDownload, FiRefreshCw, FiBookOpen,
  FiTool, FiAlertOctagon, FiCpu, FiDatabase,
} from 'react-icons/fi';
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell,
} from 'recharts';
import api from '../api/client';
import toast from 'react-hot-toast';
import type { AnalysisResponse } from '../types';

const LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'java', label: 'Java' },
  { value: 'cpp', label: 'C++' },
  { value: 'c', label: 'C' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
  { value: 'php', label: 'PHP' },
];

const SAMPLE_CODE = `def fibonacci(n):
    """Calculate the nth Fibonacci number using recursion."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)


def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr


def process_user_input(user_data):
    password = "admin123"
    query = "SELECT * FROM users WHERE name = '" + user_data + "'"
    result = eval(user_data)
    import os
    os.system("echo " + user_data)
    return result


class DataProcessor:
    def __init__(self):
        self.data = []

    def process(self, items):
        for item in items:
            for subitem in item:
                for element in subitem:
                    if element > 0:
                        if element % 2 == 0:
                            self.data.append(element)
        return self.data
`;

// ── Score Card Component ─────────────────────────────────────
function ScoreCard({ label, score, grade, color, explanation }: {
  label: string; score: number; grade: string; color: string; explanation: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-subtle p-4 rounded-xl"
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-[var(--text-muted)] uppercase tracking-wider">{label}</span>
        <span className="text-xs font-bold px-2 py-0.5 rounded-md" style={{ background: `${color}20`, color }}>{grade}</span>
      </div>
      <div className="flex items-end gap-2">
        <span className="text-2xl font-bold" style={{ color }}>{score.toFixed(1)}</span>
        <span className="text-xs text-[var(--text-muted)] mb-1">/100</span>
      </div>
      {/* Progress bar */}
      <div className="w-full h-1.5 rounded-full mt-2" style={{ background: 'rgba(255,255,255,0.06)' }}>
        <motion.div
          className="h-full rounded-full"
          style={{ background: color }}
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 1, ease: [0.4, 0, 0.2, 1] }}
        />
      </div>
      <p className="text-[10px] text-[var(--text-muted)] mt-2 line-clamp-2">{explanation}</p>
    </motion.div>
  );
}

// ── Issue Card Component ─────────────────────────────────────
function IssueCard({ issue }: { issue: any }) {
  const [expanded, setExpanded] = useState(false);
  const severityColors: Record<string, string> = {
    critical: '#ef4444', high: '#f97316', medium: '#f59e0b', low: '#3b82f6', info: '#06b6d4',
  };
  const color = severityColors[issue.severity] || '#64748b';

  return (
    <motion.div
      layout
      className="glass-subtle p-4 rounded-xl cursor-pointer"
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-start gap-3">
        <div className="p-1.5 rounded-lg mt-0.5" style={{ background: `${color}15` }}>
          <FiAlertTriangle className="w-3.5 h-3.5" style={{ color }} />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold px-1.5 py-0.5 rounded" style={{ background: `${color}20`, color }}>
              {issue.severity?.toUpperCase()}
            </span>
            <span className="text-[10px] text-[var(--text-muted)]">{issue.type}</span>
          </div>
          <p className="text-sm font-medium mt-1">{issue.title}</p>
          <p className="text-xs text-[var(--text-secondary)] mt-1">{issue.description}</p>

          <AnimatePresence>
            {expanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="mt-3 space-y-2 text-xs"
              >
                {issue.explanation && (
                  <div className="p-2.5 rounded-lg" style={{ background: 'rgba(255,255,255,0.03)' }}>
                    <p className="font-semibold text-[var(--accent-blue)] mb-1">💡 Explanation</p>
                    <p className="text-[var(--text-secondary)]">{issue.explanation}</p>
                  </div>
                )}
                {issue.why_it_matters && (
                  <div className="p-2.5 rounded-lg" style={{ background: 'rgba(255,255,255,0.03)' }}>
                    <p className="font-semibold text-[var(--accent-amber)] mb-1">⚠️ Why it matters</p>
                    <p className="text-[var(--text-secondary)]">{issue.why_it_matters}</p>
                  </div>
                )}
                {issue.how_to_fix && (
                  <div className="p-2.5 rounded-lg" style={{ background: 'rgba(255,255,255,0.03)' }}>
                    <p className="font-semibold text-[var(--accent-green)] mb-1">🔧 How to fix</p>
                    <p className="text-[var(--text-secondary)]">{issue.how_to_fix}</p>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
}

// ── Main Analysis Page ───────────────────────────────────────
export default function Analysis() {
  const [code, setCode] = useState(SAMPLE_CODE);
  const [language, setLanguage] = useState('python');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  const handleAnalyze = useCallback(async () => {
    if (!code.trim()) {
      toast.error('Please enter some code to analyze');
      return;
    }

    setLoading(true);
    try {
      const { data } = await api.post('/analysis/analyze', {
        code,
        language,
        options: {
          quality: true, security: true, performance: true,
          complexity: true, refactoring: true, bug_prediction: true,
          documentation: true, test_generation: true, similarity: true,
          tech_debt: true,
        },
      });
      setResult(data);
      setActiveTab('overview');
      toast.success(`Analysis complete! Score: ${data.overall_quality_score}`);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  }, [code, language]);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: FiActivity },
    { id: 'security', label: 'Security', icon: FiShield },
    { id: 'performance', label: 'Performance', icon: FiZap },
    { id: 'complexity', label: 'Complexity', icon: FiCpu },
    { id: 'bugs', label: 'Bug Prediction', icon: FiAlertOctagon },
    { id: 'refactoring', label: 'Refactoring', icon: FiTool },
    { id: 'docs', label: 'Docs & Tests', icon: FiBookOpen },
  ];

  const getScoreColor = (score: number) => {
    if (score >= 90) return '#10b981';
    if (score >= 80) return '#3b82f6';
    if (score >= 70) return '#f59e0b';
    if (score >= 60) return '#f97316';
    return '#ef4444';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Code <span className="gradient-text">Analysis</span></h1>
          <p className="text-sm text-[var(--text-secondary)] mt-1">Paste your code and get AI-powered insights</p>
        </div>
        <div className="flex items-center gap-3">
          {/* Language Selector */}
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="px-3 py-2 rounded-xl text-sm"
            style={{
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid rgba(255,255,255,0.1)',
              color: 'var(--text-primary)',
              outline: 'none',
            }}
          >
            {LANGUAGES.map((l) => (
              <option key={l.value} value={l.value} style={{ background: '#1a1a3e' }}>{l.label}</option>
            ))}
          </select>

          {/* Analyze Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleAnalyze}
            disabled={loading}
            className="btn-primary"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <FiPlay className="w-4 h-4" />
            )}
            {loading ? 'Analyzing...' : 'Analyze Code'}
          </motion.button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Code Editor */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-card overflow-hidden"
        >
          <div className="flex items-center justify-between px-4 py-3" style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
            <div className="flex items-center gap-2">
              <FiCode className="w-4 h-4 text-[var(--accent-blue)]" />
              <span className="text-sm font-medium">Source Code</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-[var(--text-muted)]">
              <span>{code.split('\n').length} lines</span>
              <span>•</span>
              <span>{language}</span>
            </div>
          </div>
          <div className="monaco-wrapper" style={{ height: '500px' }}>
            <Editor
              height="500px"
              language={language === 'cpp' ? 'cpp' : language}
              value={code}
              onChange={(v) => setCode(v || '')}
              theme="vs-dark"
              options={{
                fontSize: 13,
                fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                padding: { top: 16, bottom: 16 },
                lineNumbers: 'on',
                renderLineHighlight: 'gutter',
                smoothScrolling: true,
                cursorBlinking: 'smooth',
                cursorSmoothCaretAnimation: 'on',
                bracketPairColorization: { enabled: true },
              }}
            />
          </div>
        </motion.div>

        {/* Results Panel */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-card overflow-hidden"
        >
          {!result ? (
            <div className="h-full flex flex-col items-center justify-center p-8 text-center min-h-[560px]">
              <motion.div
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ duration: 3, repeat: Infinity }}
                className="w-20 h-20 rounded-2xl flex items-center justify-center mb-6"
                style={{ background: 'linear-gradient(135deg, rgba(102,126,234,0.15), rgba(118,75,162,0.15))' }}
              >
                <FiActivity className="w-10 h-10 text-[var(--accent-blue)]" />
              </motion.div>
              <h3 className="text-lg font-semibold">Ready to Analyze</h3>
              <p className="text-sm text-[var(--text-secondary)] mt-2 max-w-xs">
                Paste your code in the editor and click "Analyze Code" to get comprehensive AI-powered insights.
              </p>
            </div>
          ) : (
            <div className="flex flex-col h-full">
              {/* Tab Bar */}
              <div className="flex gap-1 px-3 pt-3 overflow-x-auto" style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                {tabs.map(({ id, label, icon: Icon }) => (
                  <button
                    key={id}
                    onClick={() => setActiveTab(id)}
                    className={`flex items-center gap-1.5 px-3 py-2 text-xs font-medium rounded-t-lg transition-all whitespace-nowrap ${
                      activeTab === id
                        ? 'text-white bg-[rgba(255,255,255,0.08)]'
                        : 'text-[var(--text-muted)] hover:text-white'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    {label}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4" style={{ maxHeight: '500px' }}>
                {activeTab === 'overview' && (
                  <>
                    {/* Overall Score */}
                    <div className="flex items-center gap-4 p-4 rounded-xl" style={{ background: 'rgba(255,255,255,0.03)' }}>
                      <div className="text-center">
                        <div
                          className="text-4xl font-bold"
                          style={{ color: getScoreColor(result.overall_quality_score) }}
                        >
                          {result.overall_quality_score.toFixed(1)}
                        </div>
                        <p className="text-xs text-[var(--text-muted)] mt-1">Overall Score</p>
                      </div>
                      <div className="flex-1 text-xs text-[var(--text-secondary)]">
                        <div className="flex items-center gap-2 mb-1">
                          <FiClock className="w-3 h-3" />
                          <span>Analyzed in {result.processing_time_ms}ms</span>
                        </div>
                        <div className="flex items-center gap-2 mb-1">
                          <FiCode className="w-3 h-3" />
                          <span>{result.total_lines} lines ({result.code_lines} code, {result.comment_lines} comments)</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <FiCheckCircle className="w-3 h-3" />
                          <span>{result.language?.toUpperCase()} • {result.issues?.length || 0} issues found</span>
                        </div>
                      </div>
                    </div>

                    {/* Score Cards */}
                    <div className="grid grid-cols-2 gap-3">
                      {Object.entries(result.scores || {}).map(([key, val]) => (
                        <ScoreCard
                          key={key}
                          label={val.label}
                          score={val.score}
                          grade={val.grade}
                          color={val.color}
                          explanation={val.explanation}
                        />
                      ))}
                    </div>

                    {/* Radar Chart */}
                    {result.scores && Object.keys(result.scores).length > 0 && (
                      <div className="glass-subtle p-4 rounded-xl">
                        <h4 className="text-xs font-semibold mb-2">Quality Radar</h4>
                        <ResponsiveContainer width="100%" height={200}>
                          <RadarChart data={Object.entries(result.scores).map(([k, v]) => ({ subject: v.label, A: v.score }))}>
                            <PolarGrid stroke="rgba(255,255,255,0.08)" />
                            <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 9 }} />
                            <Radar dataKey="A" stroke="#667eea" fill="#667eea" fillOpacity={0.2} strokeWidth={2} />
                          </RadarChart>
                        </ResponsiveContainer>
                      </div>
                    )}

                    {/* Issues */}
                    {result.issues && result.issues.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold mb-3">Issues Found ({result.issues.length})</h4>
                        <div className="space-y-2">
                          {result.issues.map((issue, i) => (
                            <IssueCard key={i} issue={issue} />
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}

                {activeTab === 'security' && (
                  <>
                    <h4 className="text-sm font-semibold">Security Vulnerabilities</h4>
                    {result.security_vulnerabilities && result.security_vulnerabilities.length > 0 ? (
                      <div className="space-y-3">
                        {result.security_vulnerabilities.map((vuln, i) => (
                          <motion.div key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.1 }} className="glass-subtle p-4 rounded-xl">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="text-xs font-bold px-2 py-0.5 rounded"
                                style={{ background: vuln.severity === 'critical' ? '#ef444420' : vuln.severity === 'high' ? '#f9731620' : '#f59e0b20',
                                         color: vuln.severity === 'critical' ? '#ef4444' : vuln.severity === 'high' ? '#f97316' : '#f59e0b' }}>
                                {vuln.severity?.toUpperCase()}
                              </span>
                              {vuln.cvss_score && <span className="text-[10px] text-[var(--text-muted)]">CVSS: {vuln.cvss_score}</span>}
                              {vuln.cwe_id && <span className="text-[10px] text-[var(--text-muted)]">{vuln.cwe_id}</span>}
                            </div>
                            <h5 className="text-sm font-medium">{vuln.title}</h5>
                            <p className="text-xs text-[var(--text-secondary)] mt-1">{vuln.description}</p>
                            {vuln.recommendation && (
                              <div className="mt-2 p-2 rounded-lg text-xs" style={{ background: 'rgba(16,185,129,0.08)' }}>
                                <span className="text-[var(--accent-green)] font-semibold">Fix: </span>
                                <span className="text-[var(--text-secondary)]">{vuln.recommendation}</span>
                              </div>
                            )}
                            {vuln.code_snippet && (
                              <div className="mt-2 p-2 rounded-lg font-mono text-[11px]" style={{ background: 'rgba(239,68,68,0.05)' }}>
                                Line {vuln.line_number}: <code>{vuln.code_snippet}</code>
                              </div>
                            )}
                          </motion.div>
                        ))}
                      </div>
                    ) : (
                      <div className="flex flex-col items-center justify-center py-12 text-center">
                        <FiCheckCircle className="w-10 h-10 text-[var(--accent-green)] mb-3" />
                        <p className="text-sm font-medium">No security vulnerabilities detected!</p>
                        <p className="text-xs text-[var(--text-muted)] mt-1">Your code passed all security checks.</p>
                      </div>
                    )}
                  </>
                )}

                {activeTab === 'performance' && (
                  <>
                    <h4 className="text-sm font-semibold">Performance Analysis</h4>
                    {/* Time/Space Complexity */}
                    {result.time_space_complexity && (
                      <div className="glass-subtle p-4 rounded-xl">
                        <h5 className="text-xs font-semibold mb-3">Time & Space Complexity</h5>
                        <div className="grid grid-cols-2 gap-3">
                          <div className="text-center p-3 rounded-lg" style={{ background: 'rgba(255,255,255,0.03)' }}>
                            <p className="text-lg font-bold text-[var(--accent-blue)]">{result.time_space_complexity.time_complexity}</p>
                            <p className="text-[10px] text-[var(--text-muted)]">Time (Average)</p>
                          </div>
                          <div className="text-center p-3 rounded-lg" style={{ background: 'rgba(255,255,255,0.03)' }}>
                            <p className="text-lg font-bold text-[var(--accent-purple)]">{result.time_space_complexity.space_complexity}</p>
                            <p className="text-[10px] text-[var(--text-muted)]">Space</p>
                          </div>
                          <div className="text-center p-3 rounded-lg" style={{ background: 'rgba(255,255,255,0.03)' }}>
                            <p className="text-sm font-bold text-[var(--accent-rose)]">{result.time_space_complexity.worst_case}</p>
                            <p className="text-[10px] text-[var(--text-muted)]">Worst Case</p>
                          </div>
                          <div className="text-center p-3 rounded-lg" style={{ background: 'rgba(255,255,255,0.03)' }}>
                            <p className="text-sm font-bold text-[var(--accent-green)]">{result.time_space_complexity.best_case}</p>
                            <p className="text-[10px] text-[var(--text-muted)]">Best Case</p>
                          </div>
                        </div>
                        <p className="text-xs text-[var(--text-secondary)] mt-3">{result.time_space_complexity.explanation}</p>
                      </div>
                    )}
                    {/* Performance Issues */}
                    {result.performance_issues?.map((issue, i) => (
                      <div key={i} className="glass-subtle p-4 rounded-xl">
                        <p className="text-sm font-medium">{issue.title}</p>
                        <p className="text-xs text-[var(--text-secondary)] mt-1">{issue.description}</p>
                        {issue.current_complexity && (
                          <div className="flex items-center gap-2 mt-2">
                            <span className="text-xs px-2 py-1 rounded" style={{ background: 'rgba(239,68,68,0.1)', color: '#ef4444' }}>{issue.current_complexity}</span>
                            <span className="text-[var(--text-muted)]">→</span>
                            <span className="text-xs px-2 py-1 rounded" style={{ background: 'rgba(16,185,129,0.1)', color: '#10b981' }}>{issue.suggested_complexity}</span>
                          </div>
                        )}
                        {issue.suggested_approach && (
                          <p className="text-xs text-[var(--accent-green)] mt-2">💡 {issue.suggested_approach}</p>
                        )}
                      </div>
                    ))}
                  </>
                )}

                {activeTab === 'complexity' && result.complexity_metrics && (
                  <>
                    <h4 className="text-sm font-semibold">Complexity Metrics</h4>
                    <div className="grid grid-cols-2 gap-3">
                      {[
                        { label: 'Cyclomatic Complexity', value: result.complexity_metrics.cyclomatic_complexity, max: 50 },
                        { label: 'Cognitive Complexity', value: result.complexity_metrics.cognitive_complexity, max: 100 },
                        { label: 'Maintainability Index', value: result.complexity_metrics.maintainability_index, max: 100 },
                        { label: 'Max Nesting Depth', value: result.complexity_metrics.max_nesting_depth, max: 10 },
                        { label: 'Halstead Difficulty', value: result.complexity_metrics.halstead_difficulty, max: 100 },
                        { label: 'Avg Function Length', value: result.complexity_metrics.avg_function_length, max: 100 },
                      ].map((m) => (
                        <div key={m.label} className="glass-subtle p-3 rounded-xl">
                          <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider">{m.label}</p>
                          <p className="text-xl font-bold mt-1">{typeof m.value === 'number' ? m.value.toFixed(1) : m.value}</p>
                          <div className="w-full h-1 rounded-full mt-2" style={{ background: 'rgba(255,255,255,0.06)' }}>
                            <div className="h-full rounded-full" style={{
                              width: `${Math.min((m.value / m.max) * 100, 100)}%`,
                              background: m.value / m.max > 0.7 ? '#ef4444' : m.value / m.max > 0.4 ? '#f59e0b' : '#10b981'
                            }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                )}

                {activeTab === 'bugs' && result.bug_prediction && (
                  <>
                    <h4 className="text-sm font-semibold">Bug Prediction</h4>
                    <div className="glass-subtle p-4 rounded-xl text-center">
                      <div className="text-4xl font-bold" style={{
                        color: result.bug_prediction.bug_probability > 0.6 ? '#ef4444' :
                               result.bug_prediction.bug_probability > 0.3 ? '#f59e0b' : '#10b981'
                      }}>
                        {(result.bug_prediction.bug_probability * 100).toFixed(1)}%
                      </div>
                      <p className="text-xs text-[var(--text-muted)] mt-1">Bug Probability</p>
                      <p className="text-xs mt-2">
                        Defect Likelihood: <span className="font-bold">{result.bug_prediction.defect_likelihood?.toUpperCase()}</span>
                      </p>
                      <p className="text-xs text-[var(--text-muted)]">
                        Confidence: {(result.bug_prediction.confidence * 100).toFixed(0)}%
                      </p>
                    </div>
                    {/* Risk Factors */}
                    <div>
                      <h5 className="text-xs font-semibold mb-2">Top Risk Factors</h5>
                      <div className="space-y-2">
                        {result.bug_prediction.top_risk_factors?.map((f, i) => (
                          <div key={i} className="flex items-center justify-between glass-subtle p-3 rounded-lg">
                            <span className="text-xs">{f.factor}</span>
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-mono">{f.value}</span>
                              <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                                f.impact === 'high' ? 'bg-red-500/10 text-red-400' :
                                f.impact === 'medium' ? 'bg-amber-500/10 text-amber-400' : 'bg-green-500/10 text-green-400'
                              }`}>{f.impact}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}

                {activeTab === 'refactoring' && (
                  <>
                    <h4 className="text-sm font-semibold">Refactoring Suggestions</h4>
                    {result.refactoring_suggestions?.map((s, i) => (
                      <div key={i} className="glass-subtle p-4 rounded-xl">
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                            s.priority === 'high' ? 'bg-red-500/10 text-red-400' :
                            s.priority === 'medium' ? 'bg-amber-500/10 text-amber-400' : 'bg-blue-500/10 text-blue-400'
                          }`}>{s.priority}</span>
                          <span className="text-[10px] text-[var(--text-muted)]">{s.type}</span>
                        </div>
                        <p className="text-sm font-medium">{s.title}</p>
                        <p className="text-xs text-[var(--text-secondary)] mt-1">{s.description}</p>
                        {s.principle && <p className="text-xs text-[var(--accent-blue)] mt-2">📐 {s.principle}</p>}
                        <p className="text-xs text-[var(--accent-green)] mt-1">✨ {s.benefit}</p>
                      </div>
                    ))}
                    {(!result.refactoring_suggestions || result.refactoring_suggestions.length === 0) && (
                      <div className="flex flex-col items-center justify-center py-8 text-center">
                        <FiCheckCircle className="w-8 h-8 text-[var(--accent-green)] mb-2" />
                        <p className="text-sm">No refactoring suggestions — code looks clean!</p>
                      </div>
                    )}
                  </>
                )}

                {activeTab === 'docs' && (
                  <>
                    {/* Generated Tests */}
                    {result.generated_tests && (
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="text-sm font-semibold">Generated Tests ({result.generated_tests.test_count})</h4>
                          <span className="text-[10px] px-2 py-1 rounded-lg" style={{ background: 'rgba(102,126,234,0.15)', color: '#667eea' }}>
                            {result.generated_tests.framework}
                          </span>
                        </div>
                        <div className="glass-subtle p-3 rounded-xl">
                          <pre className="text-[11px] text-[var(--text-secondary)] overflow-x-auto whitespace-pre font-mono">
                            {result.generated_tests.test_code}
                          </pre>
                        </div>
                      </div>
                    )}
                    {/* Documentation */}
                    {result.documentation?.readme && (
                      <div className="mt-4">
                        <h4 className="text-sm font-semibold mb-2">Generated Documentation</h4>
                        <div className="glass-subtle p-3 rounded-xl">
                          <pre className="text-[11px] text-[var(--text-secondary)] overflow-x-auto whitespace-pre-wrap">
                            {result.documentation.readme}
                          </pre>
                        </div>
                      </div>
                    )}
                  </>
                )}

                {/* Tech Debt (shown in overview) */}
                {activeTab === 'overview' && result.tech_debt && (
                  <div className="glass-subtle p-4 rounded-xl">
                    <h4 className="text-xs font-semibold mb-3">Technical Debt</h4>
                    <div className="grid grid-cols-3 gap-3 text-center">
                      <div>
                        <p className="text-lg font-bold text-[var(--accent-amber)]">{result.tech_debt.debt_score.toFixed(1)}</p>
                        <p className="text-[10px] text-[var(--text-muted)]">Debt Score</p>
                      </div>
                      <div>
                        <p className="text-lg font-bold text-[var(--accent-blue)]">{result.tech_debt.estimated_fix_hours}h</p>
                        <p className="text-[10px] text-[var(--text-muted)]">Est. Fix Time</p>
                      </div>
                      <div>
                        <p className="text-lg font-bold uppercase" style={{
                          color: result.tech_debt.priority === 'critical' ? '#ef4444' :
                                 result.tech_debt.priority === 'high' ? '#f97316' : '#f59e0b'
                        }}>{result.tech_debt.priority}</p>
                        <p className="text-[10px] text-[var(--text-muted)]">Priority</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
