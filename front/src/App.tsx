import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./App.css";

// Import components
import Navigation from "./components/Navigation/Navigation";

// Import pages
import Checkout from "./pages/Checkout/Checkout";
import Success from "./pages/Success/Success";

const App = () => {
  return (
    <div>
      <Router>
        <Navigation />
        <div className="credix-main">
          <Routes>
            <Route path="/" element={<Checkout />} />
            <Route path="/success/:order_id" element={<Success />} />
          </Routes>
        </div>
      </Router>
    </div>
  );
};

export default App;
