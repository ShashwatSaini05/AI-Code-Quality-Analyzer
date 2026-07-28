/* ── API Types ─────────────────────────────────────────── */

export interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  avatar_url?: string;
  role: string;
  auth_provider: string;
  is_active: boolean;
  is_verified: boolean;
  organization_name?: string;
  created_at: string;
  last_login_at?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface ScoreBreakdown {
  score: number;
  grade: string;
  label: string;
  explanation: string;
  color: string;
}

export interface CodeIssue {
  type: string;
  severity: string;
  title: string;
  description: string;
  line_number?: number;
  code_snippet?: string;
  explanation: string;
  why_it_matters: string;
  real_world_example?: string;
  how_to_fix: string;
  expected_improvement?: string;
}

export interface SecurityVulnerability {
  type: string;
  severity: string;
  cvss_score?: number;
  cwe_id?: string;
  title: string;
  description: string;
  line_number?: number;
  code_snippet?: string;
  recommendation: string;
  real_world_example?: string;
}

export interface PerformanceIssue {
  type: string;
  severity: string;
  title: string;
  description: string;
  current_approach?: string;
  suggested_approach?: string;
  current_complexity?: string;
  suggested_complexity?: string;
  memory_impact?: string;
  line_number?: number;
}

export interface RefactoringSuggestion {
  type: string;
  title: string;
  description: string;
  current_code?: string;
  suggested_code?: string;
  principle?: string;
  benefit: string;
  effort: string;
  priority: string;
}

export interface ComplexityMetrics {
  cyclomatic_complexity: number;
  cognitive_complexity: number;
  maintainability_index: number;
  halstead_vocabulary: number;
  halstead_length: number;
  halstead_difficulty: number;
  halstead_effort: number;
  halstead_volume: number;
  max_nesting_depth: number;
  avg_function_length: number;
  total_functions: number;
  total_classes: number;
}

export interface BugPrediction {
  bug_probability: number;
  maintainability_score: number;
  defect_likelihood: string;
  risk_score: number;
  confidence: number;
  top_risk_factors: Array<{ factor: string; value: number; impact: string }>;
}

export interface TechDebt {
  debt_score: number;
  estimated_fix_hours: number;
  priority: string;
  business_impact: string;
  developer_effort: string;
  breakdown: Array<{ category: string; hours: number; description: string }>;
}

export interface TimeSpaceComplexity {
  time_complexity: string;
  space_complexity: string;
  worst_case: string;
  average_case: string;
  best_case: string;
  explanation: string;
  suggestions: string[];
}

export interface MemoryAnalysis {
  estimated_memory: string;
  object_creation_count: number;
  stack_depth: number;
  heap_usage: string;
  recursive_depth?: number;
  suggestions: string[];
}

export interface DocumentationResult {
  function_docs: Array<{ name: string; doc: string }>;
  class_docs: Array<{ name: string; doc: string }>;
  readme?: string;
  api_docs?: string;
}

export interface TestGenerationResult {
  test_code: string;
  framework: string;
  test_count: number;
  coverage_areas: string[];
}

export interface AnalysisResponse {
  id: string;
  language: string;
  filename?: string;
  status: string;
  total_lines: number;
  code_lines: number;
  comment_lines: number;
  blank_lines: number;
  overall_quality_score: number;
  scores: Record<string, ScoreBreakdown>;
  complexity_metrics?: ComplexityMetrics;
  time_space_complexity?: TimeSpaceComplexity;
  memory_analysis?: MemoryAnalysis;
  issues: CodeIssue[];
  security_vulnerabilities: SecurityVulnerability[];
  performance_issues: PerformanceIssue[];
  refactoring_suggestions: RefactoringSuggestion[];
  bug_prediction?: BugPrediction;
  tech_debt?: TechDebt;
  documentation?: DocumentationResult;
  generated_tests?: TestGenerationResult;
  processing_time_ms: number;
  created_at?: string;
}

export interface AnalysisRequest {
  code: string;
  language?: string;
  filename?: string;
  project_id?: string;
  options?: Record<string, boolean>;
}

export interface DashboardStats {
  total_analyses: number;
  avg_quality_score: number;
  recent_analyses: Array<{
    id: string;
    language: string;
    filename?: string;
    score: number;
    created_at: string;
  }>;
  language_distribution: Record<string, number>;
  total_lines_analyzed: number;
  security_issues_found: number;
}

export interface ChatSession {
  id: string;
  title: string;
  language?: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  code_snippet?: string;
  created_at: string;
}
