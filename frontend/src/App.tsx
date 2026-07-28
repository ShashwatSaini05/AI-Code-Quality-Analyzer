import { Routes, Route } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Analysis from './pages/Analysis';
import SecurityDashboard from './pages/SecurityDashboard';
import Chat from './pages/Chat';

export default function App() {
  return (
    <>
      <div className="animated-bg" />
      <AnimatePresence mode="wait">
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/security" element={<SecurityDashboard />} />
            <Route path="/chat" element={<Chat />} />
          </Routes>
        </Layout>
      </AnimatePresence>
    </>
  );
}
