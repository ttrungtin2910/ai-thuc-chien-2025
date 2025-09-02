import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import viVN from 'antd/locale/vi_VN';
import App from './App';
import './index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <ConfigProvider 
        locale={viVN}
        theme={{
          token: {
            colorPrimary: '#D2691E',
            colorLink: '#D2691E',
            colorSuccess: '#228B22',
            colorError: '#CD853F',
            colorWarning: '#DAA520',
            borderRadius: 6,
            fontFamily: "'MaisonNeue', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
          },
        }}
      >
        <App />
      </ConfigProvider>
    </BrowserRouter>
  </React.StrictMode>
);
