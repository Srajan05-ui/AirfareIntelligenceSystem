import React, { useState, useEffect } from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Legend
} from 'recharts';
import { 
  PlaneTakeoff, LayoutDashboard, Activity, AlertTriangle, 
  Settings, Database, ArrowUpRight, ArrowDownRight, ShieldCheck
} from 'lucide-react';
import './index.css';

// Mock Data for the prototype
const inflationData = [
  { month: 'Jan', fisherIndex: 100, laspeyres: 100 },
  { month: 'Feb', fisherIndex: 101.2, laspeyres: 102.5 },
  { month: 'Mar', fisherIndex: 103.5, laspeyres: 105.1 },
  { month: 'Apr', fisherIndex: 102.8, laspeyres: 104.2 },
  { month: 'May', fisherIndex: 106.4, laspeyres: 109.8 },
  { month: 'Jun', fisherIndex: 108.7, laspeyres: 112.4 },
];

const anomalyData = [
  { route: 'DEL-BOM', count: 42 },
  { route: 'BLR-DEL', count: 28 },
  { route: 'BOM-GOI', count: 65 },
  { route: 'CCU-DEL', count: 15 },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [nationalIndex, setNationalIndex] = useState(108.7);
  const [apiStatus, setApiStatus] = useState('Offline (Using Mock Data)');

  // API Wiring for Live Deployment
  useEffect(() => {
    const fetchRealData = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/inflation/national', {
          headers: {
            'X-Government-API-Key': 'mospi_admin_778899' // Auth key
          }
        });
        if (response.ok) {
          const result = await response.json();
          setNationalIndex(result.data.current_index_fisher);
          setApiStatus('System Online & Secure');
        }
      } catch (error) {
        console.warn('Backend not running locally yet. Falling back to safe mock data for demo.', error);
      }
    };
    
    fetchRealData();
  }, []);

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <PlaneTakeoff className="brand-icon" size={28} />
          <span>VayuSutra</span>
        </div>
        
        <nav className="nav-menu">
          <a className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
            <LayoutDashboard size={20} />
            National Overview
          </a>
          <a className={`nav-item ${activeTab === 'anomalies' ? 'active' : ''}`} onClick={() => setActiveTab('anomalies')}>
            <AlertTriangle size={20} />
            Anomaly Detection
          </a>
          <a className={`nav-item ${activeTab === 'routes' ? 'active' : ''}`} onClick={() => setActiveTab('routes')}>
            <Activity size={20} />
            Route Analytics
          </a>
          <a className="nav-item" style={{ marginTop: 'auto' }}>
            <Database size={20} />
            Data Trust Center
          </a>
          <a className="nav-item">
            <Settings size={20} />
            Settings
          </a>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <div className="header">
          <div className="header-title">
            <h1>Airfare Intelligence Portal</h1>
            <p>MoSPI & DGCA Secure Data Terminal</p>
          </div>
          <div className="status-badge">
            <div className="status-dot"></div>
            {apiStatus}
          </div>
        </div>

        {/* Top Metrics */}
        <div className="metrics-grid">
          <div className="glass-panel metric-card">
            <div className="metric-header">
              National CPI (Fisher Index)
              <ShieldCheck size={18} color="var(--accent-blue)" />
            </div>
            <div className="metric-value">
              {nationalIndex}
              <span className="metric-trend trend-up">
                <ArrowUpRight size={16} /> +2.3%
              </span>
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '4px' }}>
              Base: Jan 2026 (100.0)
            </div>
          </div>

          <div className="glass-panel metric-card">
            <div className="metric-header">
              Scraping Volume (24h)
              <Database size={18} />
            </div>
            <div className="metric-value">
              142,504
              <span className="metric-trend trend-up">
                <ArrowUpRight size={16} /> +12%
              </span>
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '4px' }}>
              Cryptographically Verified Signatures
            </div>
          </div>

          <div className="glass-panel metric-card">
            <div className="metric-header">
              Outliers Filtered (MAD)
              <AlertTriangle size={18} />
            </div>
            <div className="metric-value">
              8,432
              <span className="metric-trend trend-down">
                <ArrowDownRight size={16} /> -4.1%
              </span>
            </div>
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '4px' }}>
              Prevented from skewing index
            </div>
          </div>
        </div>

        {/* Charts */}
        <div className="charts-grid">
          <div className="glass-panel">
            <h2 className="panel-title">
              <Activity size={20} color="var(--accent-blue)" />
              Inflation Methodology Comparison
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem', lineHeight: '1.5' }}>
              <strong>Why this matters:</strong> The red line (Old Arithmetic Method) overestimates inflation when flights spike. 
              The blue line (Our Fisher Ideal Index) accounts for consumer substitution, providing a much more accurate, stable economic metric for MoSPI.
            </p>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={inflationData} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
                  <defs>
                    <linearGradient id="colorFisher" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--accent-blue)" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="var(--accent-blue)" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorLasp" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--accent-red)" stopOpacity={0.15}/>
                      <stop offset="95%" stopColor="var(--accent-red)" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                  <XAxis 
                    dataKey="month" 
                    stroke="var(--text-secondary)" 
                    tick={{fill: 'var(--text-secondary)'}}
                    dy={10}
                  />
                  <YAxis 
                    domain={[95, 115]} 
                    stroke="var(--text-secondary)" 
                    tick={{fill: 'var(--text-secondary)'}} 
                    dx={-10}
                  />
                  <Tooltip 
                    formatter={(value) => [`${value} Points`, '']}
                    labelStyle={{ color: '#000', fontWeight: 'bold' }}
                    contentStyle={{ backgroundColor: 'rgba(19, 24, 33, 0.95)', border: '1px solid var(--accent-blue)', borderRadius: '8px', color: 'white' }}
                  />
                  <Legend verticalAlign="top" height={36} wrapperStyle={{ paddingBottom: '20px' }}/>
                  <Area type="monotone" dataKey="fisherIndex" name="Our Metric: Fisher Ideal Index (Highly Accurate)" stroke="var(--accent-blue)" strokeWidth={4} fillOpacity={1} fill="url(#colorFisher)" />
                  <Area type="monotone" dataKey="laspeyres" name="Old Metric: Basic Arithmetic Average (Overestimated)" stroke="var(--accent-red)" strokeWidth={2} strokeDasharray="5 5" fillOpacity={1} fill="url(#colorLasp)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass-panel">
            <h2 className="panel-title">
              <AlertTriangle size={20} color="var(--accent-orange)" />
              Anomaly Density by Route
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem', lineHeight: '1.5' }}>
              <strong>What you are seeing:</strong> The number of "glitch" or extreme outlier prices automatically caught and removed by our MAD Modified Z-Score algorithm, preventing data corruption.
            </p>
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={anomalyData} layout="vertical" margin={{ top: 5, right: 30, left: 30, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" horizontal={false} />
                  <XAxis 
                    type="number" 
                    stroke="var(--text-secondary)" 
                    tick={{fill: 'var(--text-secondary)'}}
                  />
                  <YAxis 
                    dataKey="route" 
                    type="category" 
                    stroke="var(--text-primary)" 
                    tick={{fill: 'var(--text-primary)', fontWeight: 'bold'}}
                  />
                  <Tooltip 
                    formatter={(value) => [`${value} Extreme Outliers Removed`, 'Data Cleaned']}
                    labelStyle={{ color: '#000', fontWeight: 'bold' }}
                    cursor={{fill: 'rgba(245, 158, 11, 0.1)'}}
                    contentStyle={{ backgroundColor: 'rgba(19, 24, 33, 0.95)', border: '1px solid var(--accent-orange)', borderRadius: '8px', color: 'white' }}
                  />
                  <Bar dataKey="count" name="Filtered Glitches" fill="var(--accent-orange)" radius={[0, 6, 6, 0]} barSize={32} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
