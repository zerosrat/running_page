import './styles/index.css';
import { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { Helmet, HelmetProvider } from 'react-helmet-async';
import getSiteMetadata from '@core/hooks/useSiteMetadata';
import Index from './pages/index';

const Summary = lazy(() => import('./pages/summary'));

function CanonicalLink() {
  const { pathname } = useLocation();
  const page = pathname.replace(/\/$/, '') === '/summary' ? 'summary' : '';
  return (
    <Helmet>
      <link
        rel="canonical"
        href={new URL(page, getSiteMetadata().siteUrl).href}
      />
    </Helmet>
  );
}

export default function ClassicTheme() {
  return (
    <HelmetProvider>
      <BrowserRouter basename={import.meta.env.BASE_URL}>
        <CanonicalLink />
        <Suspense fallback={<div>Loading...</div>}>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/summary" element={<Summary />} />
            <Route path="*" element={<Index />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </HelmetProvider>
  );
}
