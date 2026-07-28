import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiActivity, FiShield, FiCode, FiTrendingUp, FiZap, FiClock } from 'react-icons/fi';
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area,
} from 'recharts';
import { useAuthStore } from '../stores/authStore';

// ── Score Progress Ring ──────────────────────────────────────
function ProgressRing({ score, size = 120, strokeWidth = 8, color = '#667eea' }: {
  score: number; size?: number; strokeWidth?: number; color?: string;
}) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="progress-ring">
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          stroke="rgba(255,255,255,0.06)" strokeWidth={strokeWidth} fill="none"
        />
        <motion.circle
          cx={size / 2} cy={size / 2} r={radius}
          stroke={color} strokeWidth={strokeWidth} fill="none"
          strokeLinecap="round"
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: [0.4, 0, 0.2, 1] }}
          strokeDasharray={circumference}
        />
      </svg>
      <div className="absolute text-center">
        <motion.span
          className="text-2xl font-bold"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          {score}
        </motion.span>
        <p className="text-[10px] text-[var(--text-muted)]">Score</p>
      </div>
    </div>
  );
}

// ── Stats Card ───────────────────────────────────────────────
function StatsCard({ icon: Icon, label, value, change, color, delay }: {
  icon: any; label: string; value: string | number; change?: string; color: string; delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="glass-card p-5"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-[var(--text-muted)] uppercase tracking-wider">{label}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          {change && (
            <p className="text-xs mt-1" style={{ color }}>
              {change}
            </p>
          )}
        </div>
        <div className="p-2.5 rounded-xl" style={{ background: `${color}20` }}>
          <Icon className="w-5 h-5" style={{ color }} />
        </div>
      </div>
    </motion.div>
  );
}

// ── Main Dashboard ───────────────────────────────────────────
export default function Dashboard() {
  const { user } = useAuthStore();

  // Sample dashboard data (in production, fetch from API)
  const qualityData = [
    { subject: 'Readability', A: 82 },
    { subject: 'Maintainability', A: 75 },
    { subject: 'Performance', A: 88 },
    { subject: 'Security', A: 90 },
    { subject: 'Scalability', A: 70 },
    { subject: 'Documentation', A: 65 },
    { subject: 'Architecture', A: 78 },
  ];

  const languageData = [
    { name: 'Python', value: 35, color: '#3572A5' },
    { name: 'JavaScript', value: 25, color: '#f1e05a' },
    { name: 'TypeScript', value: 20, color: '#3178c6' },
    { name: 'Java', value: 12, color: '#b07219' },
    { name: 'Go', value: 8, color: '#00ADD8' },
  ];

  const activityData = [
    { day: 'Mon', analyses: 4 }, { day: 'Tue', analyses: 7 },
    { day: 'Wed', analyses: 3 }, { day: 'Thu', analyses: 8 },
    { day: 'Fri', analyses: 12 }, { day: 'Sat', analyses: 5 },
    { day: 'Sun', analyses: 2 },
  ];

  const recentAnalyses = [
    { id: '1', filename: 'auth_service.py', language: 'Python', score: 85, time: '2 hours ago' },
    { id: '2', filename: 'api.controller.ts', language: 'TypeScript', score: 72, time: '5 hours ago' },
    { id: '3', filename: 'UserRepository.java', language: 'Java', score: 91, time: '1 day ago' },
    { id: '4', filename: 'handlers.go', language: 'Go', score: 88, time: '2 days ago' },
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
      <div>
        <motion.h1
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-2xl font-bold"
        >
          Welcome back, <span className="gradient-text">{user?.username || 'Developer'}</span> 👋
        </motion.h1>
        <p className="text-sm text-[var(--text-secondary)] mt-1">
          Here's an overview of your code quality metrics
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard icon={FiActivity} label="Total Analyses" value="47" change="+12 this week" color="#667eea" delay={0.1} />
        <StatsCard icon={FiTrendingUp} label="Avg Quality" value="82.4" change="+3.2 vs last week" color="#10b981" delay={0.2} />
        <StatsCard icon={FiShield} label="Security Issues" value="3" change="-5 from last scan" color="#f43f5e" delay={0.3} />
        <StatsCard icon={FiCode} label="Lines Analyzed" value="24.5K" change="+8.2K this month" color="#06b6d4" delay={0.4} />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quality Radar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-5"
        >
          <h3 className="text-sm font-semibold mb-4">Quality Overview</h3>
          <div className="flex justify-center">
            <ResponsiveContainer width={280} height={250}>
              <RadarChart data={qualityData}>
                <PolarGrid stroke="rgba(255,255,255,0.08)" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar name="Score" dataKey="A" stroke="#667eea" fill="#667eea" fillOpacity={0.2} strokeWidth={2} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Activity Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card p-5"
        >
          <h3 className="text-sm font-semibold mb-4">Weekly Activity</h3>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={activityData}>
              <defs>
                <linearGradient id="colorAnalyses" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#667eea" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#667eea" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="day" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{
                  background: 'rgba(15,15,35,0.95)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '12px',
                  color: '#f1f5f9',
                }}
              />
              <Area type="monotone" dataKey="analyses" stroke="#667eea" fillOpacity={1} fill="url(#colorAnalyses)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Language Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card p-5"
        >
          <h3 className="text-sm font-semibold mb-4">Languages</h3>
          <div className="flex justify-center">
            <ResponsiveContainer width={200} height={200}>
              <PieChart>
                <Pie data={languageData} cx="50%" cy="50%" innerRadius={55} outerRadius={80} dataKey="value" paddingAngle={3}>
                  {languageData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: 'rgba(15,15,35,0.95)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '12px',
                    color: '#f1f5f9',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap gap-3 mt-2 justify-center">
            {languageData.map((lang) => (
              <div key={lang.name} className="flex items-center gap-1.5">
                <div className="w-2.5 h-2.5 rounded-full" style={{ background: lang.color }} />
                <span className="text-[11px] text-[var(--text-secondary)]">{lang.name}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Overall Score */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card p-6 flex items-center gap-8"
        >
          <ProgressRing score={82} size={140} color="#667eea" />
          <div>
            <h3 className="text-lg font-semibold">Overall Code Quality</h3>
            <p className="text-sm text-[var(--text-secondary)] mt-1">Grade: <span className="text-[#3b82f6] font-bold">B</span></p>
            <p className="text-xs text-[var(--text-muted)] mt-3">
              Your code quality is above average. Focus on improving documentation and reducing complexity.
            </p>
            <div className="flex gap-3 mt-4">
              <span className="px-2.5 py-1 rounded-lg text-[10px] font-medium" style={{ background: 'rgba(16,185,129,0.15)', color: '#10b981' }}>Security: A</span>
              <span className="px-2.5 py-1 rounded-lg text-[10px] font-medium" style={{ background: 'rgba(59,130,246,0.15)', color: '#3b82f6' }}>Performance: B</span>
              <span className="px-2.5 py-1 rounded-lg text-[10px] font-medium" style={{ background: 'rgba(245,158,11,0.15)', color: '#f59e0b' }}>Docs: C</span>
            </div>
          </div>
        </motion.div>

        {/* Recent Analyses */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="glass-card p-5"
        >
          <h3 className="text-sm font-semibold mb-4">Recent Analyses</h3>
          <div className="space-y-3">
            {recentAnalyses.map((item) => (
              <div
                key={item.id}
                className="flex items-center gap-3 p-3 rounded-xl transition-all hover:bg-[rgba(255,255,255,0.03)] cursor-pointer"
              >
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold"
                  style={{ background: `${getScoreColor(item.score)}20`, color: getScoreColor(item.score) }}
                >
                  {item.score}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{item.filename}</p>
                  <p className="text-[11px] text-[var(--text-muted)]">{item.language}</p>
                </div>
                <div className="flex items-center gap-1 text-[11px] text-[var(--text-muted)]">
                  <FiClock className="w-3 h-3" />
                  {item.time}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
