import { useState } from 'react';
import { motion } from 'framer-motion';
import { FiShield, FiAlertTriangle, FiCheckCircle, FiAlertOctagon, FiInfo } from 'react-icons/fi';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis } from 'recharts';

// Sample security data
const SAMPLE_FINDINGS = [
  { type: 'SQL Injection', severity: 'critical', cvss: 9.8, cwe: 'CWE-89', count: 2, description: 'User input concatenated into SQL queries' },
  { type: 'Command Injection', severity: 'critical', cvss: 9.8, cwe: 'CWE-78', count: 1, description: 'User input passed to os.system()' },
  { type: 'Hardcoded Credentials', severity: 'high', cvss: 7.5, cwe: 'CWE-798', count: 3, description: 'Passwords and API keys in source code' },
  { type: 'XSS', severity: 'high', cvss: 7.5, cwe: 'CWE-79', count: 1, description: 'Unsanitized user input in HTML rendering' },
  { type: 'Weak Hashing', severity: 'medium', cvss: 5.5, cwe: 'CWE-328', count: 2, description: 'MD5 or SHA-1 used for hashing' },
  { type: 'Insecure Random', severity: 'low', cvss: 3.5, cwe: 'CWE-330', count: 4, description: 'Math.random() used for security operations' },
];

export default function SecurityDashboard() {
  const severityColors: Record<string, string> = {
    critical: '#ef4444', high: '#f97316', medium: '#f59e0b', low: '#3b82f6', info: '#06b6d4',
  };

  const severityData = [
    { name: 'Critical', value: 3, color: '#ef4444' },
    { name: 'High', value: 4, color: '#f97316' },
    { name: 'Medium', value: 2, color: '#f59e0b' },
    { name: 'Low', value: 4, color: '#3b82f6' },
  ];

  const trendData = [
    { month: 'Jan', issues: 12 }, { month: 'Feb', issues: 8 },
    { month: 'Mar', issues: 15 }, { month: 'Apr', issues: 6 },
    { month: 'May', issues: 3 }, { month: 'Jun', issues: 5 },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Security <span className="gradient-text">Dashboard</span></h1>
        <p className="text-sm text-[var(--text-secondary)] mt-1">Monitor and track security vulnerabilities across your code</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        {[
          { label: 'Critical', count: 3, icon: FiAlertOctagon, color: '#ef4444' },
          { label: 'High', count: 4, icon: FiAlertTriangle, color: '#f97316' },
          { label: 'Medium', count: 2, icon: FiInfo, color: '#f59e0b' },
          { label: 'Resolved', count: 18, icon: FiCheckCircle, color: '#10b981' },
        ].map((item, i) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card p-5"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-[var(--text-muted)] uppercase">{item.label}</p>
                <p className="text-3xl font-bold mt-1" style={{ color: item.color }}>{item.count}</p>
              </div>
              <item.icon className="w-6 h-6" style={{ color: item.color }} />
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Severity Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-5"
        >
          <h3 className="text-sm font-semibold mb-4">Severity Distribution</h3>
          <div className="flex items-center gap-6">
            <ResponsiveContainer width={180} height={180}>
              <PieChart>
                <Pie data={severityData} cx="50%" cy="50%" innerRadius={50} outerRadius={75} dataKey="value" paddingAngle={4}>
                  {severityData.map((entry, i) => (<Cell key={i} fill={entry.color} />))}
                </Pie>
                <Tooltip contentStyle={{ background: 'rgba(15,15,35,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#f1f5f9' }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-3">
              {severityData.map((s) => (
                <div key={s.name} className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full" style={{ background: s.color }} />
                  <span className="text-xs text-[var(--text-secondary)]">{s.name}</span>
                  <span className="text-xs font-bold">{s.value}</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Trend */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card p-5"
        >
          <h3 className="text-sm font-semibold mb-4">Security Issue Trend</h3>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={trendData}>
              <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: 'rgba(15,15,35,0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#f1f5f9' }} />
              <Bar dataKey="issues" fill="#667eea" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Findings List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="glass-card p-5"
      >
        <h3 className="text-sm font-semibold mb-4">Security Findings</h3>
        <div className="space-y-3">
          {SAMPLE_FINDINGS.map((finding, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 + i * 0.05 }}
              className="flex items-center gap-4 p-4 rounded-xl transition-all hover:bg-[rgba(255,255,255,0.03)]"
              style={{ borderLeft: `3px solid ${severityColors[finding.severity]}` }}
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold px-2 py-0.5 rounded"
                    style={{ background: `${severityColors[finding.severity]}20`, color: severityColors[finding.severity] }}>
                    {finding.severity.toUpperCase()}
                  </span>
                  <span className="text-xs text-[var(--text-muted)]">CVSS: {finding.cvss}</span>
                  <span className="text-xs text-[var(--text-muted)]">{finding.cwe}</span>
                </div>
                <p className="text-sm font-medium mt-1">{finding.type}</p>
                <p className="text-xs text-[var(--text-secondary)]">{finding.description}</p>
              </div>
              <div className="text-center">
                <p className="text-lg font-bold">{finding.count}</p>
                <p className="text-[10px] text-[var(--text-muted)]">instances</p>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
