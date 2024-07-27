import logo from './logo.svg';
import './App.css';
import NewsList from './components/NewsList';
import Map from './components/Map';
import MainAppbar from './components/MainAppbar';
import { Routes, Route } from 'react-router-dom';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/" element={<MainAppbar />} />
      </Routes>
    </div>
  );
}

export default App;
