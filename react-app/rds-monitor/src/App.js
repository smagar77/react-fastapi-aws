import React, {useState, useEffect} from 'react'
import './App.css';
import RDSMonitor from './components/RDSMonitor'
import axios from 'axios'
import {BrowserRouter as Router, Route, Link, Routes, useNavigate} from 'react-router-dom'


function App() {
  const base_url = 'http://awsrdsmaintenancedashboards.mmm.com/api'
  const [accounts, getAccounts] = useState([])
  useEffect(()=>{
    axios.get(base_url+"/list-accounts").then(monitor=>{
        getAccounts(monitor.data)
      }).catch(error => {
          console.log(error)
      })
  }, [])
  return (
    <div className="App">
          <Router>
            <header>
              <ul>
                {accounts.map(account => (<li key={account}><Link to={'account/' + account}>{account}</Link></li>))}
              </ul>
            </header>
            <Routes>
              <Route path="account/:account_name" element={<RDSMonitor base_url={base_url} />} />
            </Routes>
          </Router>
    </div>
  );
}

export default App;
